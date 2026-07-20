from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request
)

from yacut import db
from yacut.forms import FileUploadForm, URLForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id, is_custom_id_valid

TEMPLATE_INDEX = 'index.html'
TEMPLATE_FILES = 'files.html'

FLASH_SUCCESS_SHORTEN = 'Ссылка успешно сокращена!'
FLASH_ERROR_NO_FILES = 'Файлы не выбраны'
FLASH_UPLOAD_SUCCESS = 'Успешно загружено {count} файлов'
FLASH_UPLOAD_ERROR_PREFIX = 'Ошибка загрузки {filename}: {error}'
DEFAULT_ERROR_MESSAGE = 'Неизвестная ошибка'

FLASH_CATEGORY_ERROR = 'error'
FLASH_CATEGORY_SUCCESS = 'success'

KEY_SUCCESS = 'success'
KEY_DOWNLOAD_LINK = 'download_link'
KEY_FILENAME = 'filename'
KEY_ERROR = 'error'
KEY_SHORT_URL = 'short_url'

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = URLForm()
    short_link = None

    if form.validate_on_submit():
        original = form.original_link.data.strip()
        custom_id = form.custom_id.data.strip() if form.custom_id.data else ''

        if not custom_id:
            short = get_unique_short_id()
        else:
            valid, message = is_custom_id_valid(custom_id)
            if not valid:
                flash(message, FLASH_CATEGORY_ERROR)
                return render_template(
                    TEMPLATE_INDEX,
                    form=form,
                    short_link=None
                )
            short = custom_id

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)
        db.session.commit()

        short_link = request.host_url + short
        flash(FLASH_SUCCESS_SHORTEN, FLASH_CATEGORY_SUCCESS)

    return render_template(TEMPLATE_INDEX, form=form, short_link=short_link)


@bp.route('/files', methods=['GET', 'POST'])
def files():
    form = FileUploadForm()
    results = None

    if form.validate_on_submit():
        uploaded_files = request.files.getlist('files')
        if not uploaded_files:
            flash(FLASH_ERROR_NO_FILES, FLASH_CATEGORY_ERROR)
            return render_template(TEMPLATE_FILES, form=form, results=None)

        files_data = []
        for file in uploaded_files:
            if file and file.filename:
                filename = file.filename
                file_bytes = file.read()
                files_data.append((filename, file_bytes))

        token = current_app.config['DISK_TOKEN']
        from yacut.ya_disk_async import sync_upload_files
        upload_results = sync_upload_files(files_data, token)

        results = []
        for res in upload_results:
            if res.get(KEY_SUCCESS):
                short = get_unique_short_id()
                url_map = URLMap(original=res[KEY_DOWNLOAD_LINK], short=short)
                db.session.add(url_map)
                db.session.commit()
                short_url = request.host_url + short
                results.append({
                    KEY_FILENAME: res[KEY_FILENAME],
                    KEY_SHORT_URL: short_url
                })
            else:
                error_msg = res.get(KEY_ERROR, DEFAULT_ERROR_MESSAGE)
                flash(
                    FLASH_UPLOAD_ERROR_PREFIX.format(
                        filename=res.get(KEY_FILENAME, '?'),
                        error=error_msg
                    ),
                    FLASH_CATEGORY_ERROR
                )

        if results:
            flash(
                FLASH_UPLOAD_SUCCESS.format(count=len(results)),
                FLASH_CATEGORY_SUCCESS
            )

    return render_template(TEMPLATE_FILES, form=form, results=results)


@bp.route('/<string:short_id>')
def redirect_to_original(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        abort(404)
    return redirect(url_map.original)

from flask import Blueprint, jsonify, request

from yacut import db
from yacut.models import URLMap
from yacut.utils import get_unique_short_id, is_custom_id_valid

EMPTY_BODY = 'Отсутствует тело запроса'
MISSING_URL = '"url" является обязательным полем!'
INVALID_URL = 'Некорректный URL'
NOT_FOUND = 'Указанный id не найден'

HTTP_BAD_REQUEST = 400
HTTP_CREATED = 201
HTTP_OK = 200
HTTP_NOT_FOUND = 404

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'message': EMPTY_BODY}), HTTP_BAD_REQUEST
    if 'url' not in data:
        return jsonify({'message': MISSING_URL}), HTTP_BAD_REQUEST

    original = data['url'].strip()
    if not original.startswith(('http://', 'https://')):
        return jsonify({'message': INVALID_URL}), HTTP_BAD_REQUEST

    custom_id = data.get(
        'custom_id', ''
    ).strip() if data.get(
        'custom_id'
    ) else ''

    if not custom_id:
        short = get_unique_short_id()
    else:
        valid, message = is_custom_id_valid(custom_id)
        if not valid:
            return jsonify({'message': message}), HTTP_BAD_REQUEST
        short = custom_id

    url_map = URLMap(original=original, short=short)
    db.session.add(url_map)
    db.session.commit()

    short_url = request.host_url + short
    return jsonify({'url': original, 'short_link': short_url}), HTTP_CREATED


@bp.route('/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if not url_map:
        return jsonify({'message': NOT_FOUND}), HTTP_NOT_FOUND
    return jsonify({'url': url_map.original}), HTTP_OK

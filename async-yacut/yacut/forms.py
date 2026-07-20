from flask_wtf import FlaskForm
from wtforms import MultipleFileField, StringField
from wtforms.validators import DataRequired, Length, Regexp

ORIGINAL_REQUIRED = 'Обязательное поле'
CUSTOM_ID_LENGTH = 'Длина не более 16 символов'
CUSTOM_ID_REGEX = 'Разрешены только латинские буквы и цифры'
FILES_REQUIRED = 'Выберите хотя бы один файл'

MAX_CUSTOM_ID_LEN = 16
CUSTOM_ID_REGEX_PATTERN = r'^[A-Za-z0-9]*$'

ORIGINAL_LINK = 'Длинная ссылка'
CUSTOM_ID = 'Ваш вариант короткой ссылки'
FILES = 'Файлы'


class URLForm(FlaskForm):
    """Форма для главной страницы: сокращение ссылки."""
    original_link = StringField(
        ORIGINAL_LINK,
        validators=[DataRequired(message=ORIGINAL_REQUIRED)]
    )
    custom_id = StringField(
        CUSTOM_ID,
        validators=[
            Length(max=MAX_CUSTOM_ID_LEN, message=CUSTOM_ID_LENGTH),
            Regexp(
                CUSTOM_ID_REGEX_PATTERN,
                message=CUSTOM_ID_REGEX
            )
        ]
    )


class FileUploadForm(FlaskForm):
    """Форма для страницы загрузки файлов."""
    files = MultipleFileField(
        FILES,
        validators=[DataRequired(message=FILES_REQUIRED)]
    )

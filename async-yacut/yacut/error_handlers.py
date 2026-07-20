from flask import render_template

ERROR_404_MESSAGE = 'Страница не найдена'
ERROR_500_MESSAGE = 'Внутренняя ошибка сервера'

HTTP_404_NOT_FOUND = 404
HTTP_500_INTERNAL_ERROR = 500

TEMPLATE_ERROR = 'error.html'


def register_error_handlers(app):
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def page_not_found(e):
        return render_template(
            TEMPLATE_ERROR,
            error_message=ERROR_404_MESSAGE
        ), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_ERROR)
    def internal_server_error(e):
        return render_template(
            TEMPLATE_ERROR,
            error_message=ERROR_500_MESSAGE
        ), HTTP_500_INTERNAL_ERROR
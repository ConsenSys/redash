import redash

from flask import jsonify
from flask_login import login_required

from redash.handlers.api import api
from redash.handlers.base import routes, restful
from redash.monitor import get_status
from redash.permissions import require_super_admin


# @routes.route(settings.ROOT_API_URL + '/ping', methods=['GET'])
@restful.route('/ping', methods=['GET'])
def ping():
    return 'PONG.'


# @routes.route(settings.ROOT_API_URL + '/status.json')
@restful.route('/status.json')
@login_required
@require_super_admin
def status_api():
    status = get_status()
    return jsonify(status)


def init_app(app):
    from redash import settings
    from redash.handlers import embed, queries, static, authentication, admin, setup, organization
    app.register_blueprint(routes, url_prefix=settings.ROOT_UI_URL)
    app.register_blueprint(restful, url_prefix=settings.ROOT_API_URL)
    api.init_app(app)

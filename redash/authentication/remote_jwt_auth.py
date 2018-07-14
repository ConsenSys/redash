import logging

from jose import jwt
from flask import redirect, url_for, Blueprint, request, make_response
from redash.authentication import create_and_login_user, logout_and_redirect_to_index, get_jwt_public_key
from redash.authentication.org_resolving import current_org
from redash.handlers.base import org_scoped_rule
from redash import settings

logger = logging.getLogger('remote_jwt_auth')

blueprint = Blueprint('remote_jwt_auth', __name__)


@blueprint.route(org_scoped_rule("/remote_jwt/login"))
def login(org_slug=None):
    next_path = request.args.get('next')

    if not settings.REMOTE_JWT_LOGIN_ENABLED:
        logger.error("Cannot use remote user for login without being enabled in settings")
        return redirect(url_for('redash.index', next=next_path, org_slug=org_slug))

    jwttoken = request.headers.get(settings.REMOTE_USER_HEADER) or request.cookies.get('jwt')

    # Some Apache auth configurations will, stupidly, set (null) instead of a
    # falsey value.  Special case that here so it Just Works for more installs.
    # '(null)' should never really be a value that anyone wants to legitimately
    # use as a redash user jwt.
    if jwttoken == '(null)':
        jwttoken = None

    if not jwt:
        logger.error("Cannot use remote jwt for login when it's not provided in the request (looked in headers['" + settings.REMOTE_USER_HEADER + "'])")
        return redirect(url_for('redash.index', next=next_path, org_slug=org_slug))

    try:
        public_key = get_jwt_public_key()
        jwt_decoded = jwt.get_unverified_claims(jwttoken) if public_key is '' else jwt.decode(jwttoken, public_key)
        email = jwt_decoded.get('email', None)

        if not email:
            logger.error("Cannot use remote jwt for login when it's not provided in the request (looked in headers['" + settings.REMOTE_USER_HEADER + "'])")
            return redirect(url_for('redash.index', next=next_path, org_slug=org_slug))

        logger.info("Logging in " + email + " via remote jwt")

        user = create_and_login_user(current_org, email, email)
        if user is None:
            return logout_and_redirect_to_index()

        resp = make_response(redirect((request.host_url[:-1] + next_path) or url_for('redash.index', org_slug=org_slug), code=302))
        resp.set_cookie('jwt', jwttoken, secure=True, httponly=True)

        logger.info("Redirecting %s to %s" % (email, request.host_url[:-1] + next_path)
        logger.info(resp.headers)

        return resp
    except jwt.JWTError, jwt.ExpiredSignatureError:
        logger.error("Remote user attempted entry using key with invalid signature")
        logger.info(settings.REMOTE_JWT_EXPIRED_ENDPOINT)
        return redirect(url_for('redash.index', next=next_path, org_slug=org_slug))

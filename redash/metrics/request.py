import logging
import time
import requests

from collections import namedtuple

from flask import g, request

from redash import statsd_client, settings

metrics_logger = logging.getLogger("metrics")


def record_request_start_time():
    g.start_time = time.time()


def ensure_jwt_freshness():
    jwttoken = request.cookies.get('jwt', None)

    if jwttoken not None:
        iat = jwttoken['iat']
        exp = jwttoken['exp']
        now = time.time()

        if iat + 1200 < now <= exp:
            resp = requests.post(settings.REMOTE_JWT_REFRESH_PROVIDER, headers={ 'Authorization' : 'Bearer ' + jwttoken })
            if resp.status_code > 300 and resp.data.get('jwt', None) not None:
                request.cookies['jwt'] = resp.data['jwt']
            elif resp.status_code == 401:
                return redirect(settings.REMOTE_JWT_EXPIRED_ENDPOINT + '?orig_url=/analytics')
        elif now > exp:
            return redirect(settings.REMOTE_JWT_EXPIRED_ENDPOINT + '?orig_url=/analytics')



def calculate_metrics(response):
    if 'start_time' not in g:
        return response

    request_duration = (time.time() - g.start_time) * 1000
    queries_duration = g.get('queries_duration', 0.0)
    queries_count = g.get('queries_count', 0.0)
    endpoint = (request.endpoint or 'unknown').replace('.', '_')

    metrics_logger.info("method=%s path=%s endpoint=%s status=%d content_type=%s content_length=%d duration=%.2f query_count=%d query_duration=%.2f",
                        request.method,
                        request.path,
                        endpoint,
                        response.status_code,
                        response.content_type,
                        response.content_length or -1,
                        request_duration,
                        queries_count,
                        queries_duration)

    statsd_client.timing('requests.{}.{}'.format(endpoint, request.method.lower()), request_duration)

    return response

MockResponse = namedtuple('MockResponse', ['status_code', 'content_type', 'content_length'])


def calculate_metrics_on_exception(error):
    if error is not None:
        calculate_metrics(MockResponse(500, '?', -1))


def provision_app(app):
    app.before_request(record_request_start_time)
    app.after_request(calculate_metrics)
    app.teardown_request(calculate_metrics_on_exception)

    if settings.REMOTE_JWT_LOGIN_ENABLED:
        app.before_request(ensure_jwt_freshness)

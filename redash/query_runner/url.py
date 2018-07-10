import requests
import re
import json
import simplejson

from redash.query_runner import BaseQueryRunner, register
from redash.utils import JSONEncoder


class Url(BaseQueryRunner):
    @classmethod
    def configuration_schema(cls):
        return {
            'type': 'object',
            'properties': {
                'url': {
                    'type': 'string',
                    'title': 'URL base path'
                }
            }
        }

    @classmethod
    def annotate_query(cls):
        return False

    def test_connection(self):
        pass

    def decode_query(self, query):
        try:
            return simplejson.loads(query)
        except simplejson.JSONDecodeError:
            return { 'path' : query }

    def pre_query(self, query, request):
        json_query = self.decode_query(query)
        simple_matcher = re.compile("{(.*)}")

        if 'headers' in json_query:
            for k, v in json_query['headers'].iteritems():
                for swap in simple_matcher.findall(v):
                    swap_parts = swap.split(".")
                    if swap_parts[0] == "request":
                        if swap_parts[1] == "cookies":
                            json_query['headers'][k] = json_query['headers'][k].replace("{%s}" % swap, request.cookies.get(swap_parts[2], ""))
        
        return json.dumps(json_query, cls=JSONEncoder)

    def run_query(self, query, user):
        base_url = self.configuration.get("url", None)
        
        try:
            error = None
            json_query = self.decode_query(query)
            query = json_query.get("path", "").strip()

            if base_url is not None and base_url != "":
                if query.find("://") > -1:
                    return None, "Accepting only relative URLs to '%s'" % base_url

            if base_url is None:
                base_url = ""

            url = base_url + query

            if json_query.get('_m', None) == 'POST':
                response = requests.post(url, headers=json_query.get("headers", {}), data=json_query.get("data", None))
            else:
                response = requests.get(url, headers=json_query.get("headers", {}))
            response.raise_for_status()

            if 'query' in json_query:
                columns = self.fetch_columns(json_query['query'].values())
                rows = [dict((v[0], d[k]) for k, v in json_query['query'].iteritems()) for d in response.json()]
                json_data = json.dumps({ 'columns' : columns, 'rows' : rows }, cls=JSONEncoder)
            else:
                json_data = response.content.strip()

            if not json_data:
                error = "Got empty response from '{}'.".format(url)

            return json_data, error
        except requests.RequestException as e:
            return None, str(e)
        except KeyboardInterrupt:
            error = "Query cancelled by user."
            json_data = None

        return json_data, error

register(Url)

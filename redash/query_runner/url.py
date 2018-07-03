import requests
import re

from redash.query_runner import BaseQueryRunner, register


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

        if '_h' is in json_query:
            for k, v in json_query['_h'].iteritems():
                for swap from simple_matcher.findall(v):
                    swap_parts = swap.split(".")
                    if swap_parts[0] == "request":
                        if swap_parts[1] == "cookies":
                            json_query['_h'][k] = json_query['_h'][k].replace("{%s}" % swap, request.cookies.get(swap_parts[2], ""))

    def run_query(self, query, user):
        base_url = self.configuration.get("url", None)

        try:
            error = None
            query = query.strip()

            if base_url is not None and base_url != "":
                if query.find("://") > -1:
                    return None, "Accepting only relative URLs to '%s'" % base_url

            if base_url is None:
                base_url = ""

            url = base_url + query

            response = requests.get(url)
            response.raise_for_status()
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

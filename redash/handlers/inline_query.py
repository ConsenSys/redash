import re
import pystache
import requests

from jose import jwt


crud = {
    "environment": {
        "method": "GET",
        "params": ["consortia_id", "environment_id"],
        "url": "https://control-dev.photic.io/api/v1/consortia/{{consortia_id}}/environments/{{environment_id}}"
    }
}


def create_call_func(inline_parts):
    def function_template(auth):
        operation = crud.get(inline_parts[0], None)

        if operation is not None:
            params = dict(zip(operation['params'], inline_parts[1].replace("(", "").replace(")", "").replace(" ", "").split(",")))
            url = pystache.render(operation['url'], params)
            cred = 'Bearer %s' % auth if 'Bearer' not in auth else auth

            if operation['method'] == "GET":
                resp = requests.get(url, headers={ "Authorization" : cred })
                field = inline_parts[2].replace(".", "")

                if resp.status_code == 401:
                    raise jwt.ExpiredSignatureError("Jwt token has expired")

                return resp.json().get(field) if resp.status_code < 300 else ""
        
        return ""

    return function_template


inline_matcher = re.compile(r"\?(.*)\?")
parts_matcher = re.compile(r"(\w+)(\(.+\))(.*)")
def parse_inline_queries(query):
    inline = inline_matcher.findall(query)
    result = {}

    for q in inline:
        parts = parts_matcher.findall(q)[0]
        caller = create_call_func(parts)
        result['?%s?' % q] = caller
    return result

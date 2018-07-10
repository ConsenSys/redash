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
            auth = 'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6InRvbS5oZWdlQGNvbnNlbnN5cy5uZXQiLCJ1c2VyX2lkIjoienpqbzEyemNhcyIsIm9yZ3MiOlsienpkOGJjdTN4cCJdLCJvcmdfcGxhbnMiOnsienpkOGJjdTN4cCI6eyJjb25zb3J0aWEiOnsicGVyIjp7Im9yZyI6Mn19LCJlbnZpcm9ubWVudHMiOnsicGVyIjp7ImNvbnNvcnRpYSI6M30sInF1b3J1bSI6eyJyYWZ0Ijp7InBlciI6eyJjb25zb3J0aWEiOjN9fSwiaWJmdCI6eyJwZXIiOnsiY29uc29ydGlhIjoyfX19LCJnZXRoIjp7InBvYSI6eyJwZXIiOnsiY29uc29ydGlhIjo1fX19LCJxdWllc2NlIjp7ImFmdGVyIjp7ImlkbGVfaG91cnMiOjI0LCJpbml0aWFsX2RlbGF5IjoyNH19fSwibm9kZXMiOnsicGVyIjp7ImVudmlyb25tZW50Ijo0LCJvcmciOjEwMH19LCJtZW1iZXJzaGlwcyI6eyJwZXIiOnsiY29uc29ydGlhIjo0fX0sImRhcHBzIjp7InBlciI6eyJtZW1iZXJzaGlwIjoxMH19LCJrZXlzIjp7InBlciI6eyJlbnZpcm9ubWVudCI6MTB9fSwicm9sZXMiOnsicGVyIjp7Im9yZyI6MTAwfX0sImluZ3Jlc3MiOnsicnBzIjp7InBlciI6eyJub2RlIjo1fX0sImNvbm5zIjp7InBlciI6eyJub2RlIjo1fX19fX0sImlhdCI6MTUzMDU3MjUxMCwiZXhwIjoxNTMwNTc2MTEwfQ.Jm1l2Wm0n5t972zvUAg1t9iFX-OEUCoCVf0d7fPnXRMOSpd3Vk3T9yXZQOdOirs1bOoweFNSJoEs7i2zvBIcAQ'
            cred = 'Bearer %s' % auth if 'Bearer' not in auth else auth

            if operation['method'] == "GET":
                resp = requests.get(url, headers={ "Authorization" : cred })
                field = inline_parts[2].replace(".", "")

                if resp.status_code == 401:
                    raise jwt.ExpiredSignatureError("Jwt token has expired")

                return resp.json().get(field) if resp.status_code < 300 else ""
        
        return ""

    return function_template


inline_matcher = re.compile("\?(.*)\?")
parts_matcher = re.compile("(\w+)(\(.+\))(.*)")
def parse_inline_queries(query):
    inline = inline_matcher.findall(query)
    result = {}

    for q in inline:
        parts = parts_matcher.findall(q)[0]
        caller = create_call_func(parts)
        result['?%s?' % q] = caller
    return result

import pystache
import re

from redash import settings

_url_call_map = None
_remote_creds = None


'''
Used for getting the appropriate resource validator URL given the parameters.
'''
def get_validator(parameters):
    global _url_call_map
    if not _url_call_map:
        validator = settings.REMOTE_RESOURCE_VALIDATOR
        matches = re.compile("(http.*)\((.*)\)").match(validator)
        _url_call_map = {
            'root': matches.group(1)
        }
        paths = matches.group(2)

        if paths:
            path_matcher = re.compile("{{(\w*)}}")
            for path in paths.split(','):
                _url_call_map["".join(sorted(path_matcher.findall(path)))] = _url_call_map['root'] + path

    return pystache.render(_url_call_map.get("".join(sorted(parameters.keys())), _url_call_map['root']), parameters)


'''
Creates a mapping function which will grab info from a query run request/user
for use in the call to the validator. 
'''
def create_map_func(cred_mapping):
    def function_template(user, req):
        result = {}
        for to_key, from_loc in cred_mapping.items():
            loc, key = from_loc
            
            if loc == 'headers':
                result[to_key] = req.headers[key]
            elif loc == 'cookies':
                result[to_key] = req.cookies[key]
            else:
                result[to_key] = user.__getattribute__(key)
            
            if to_key is 'Authorization' and 'Bearer' not in result[to_key]:
                result[to_key] = 'Bearer ' + result[to_key].strip()
        return result

    return function_template


'''
Retrieves a dict of the parsed credential mappings.
'''
def get_resource_creds():
    global _remote_creds
    if not _remote_creds:
        _remote_creds = {}
        creds = settings.REMOTE_RESOURCE_CREDENTIAL
        cred_parts = creds.split(',')

        for cred in cred_parts:
            parts = cred.split('=')

            if len(parts) is 1:
                parts.insert(0, parts[0].replace('user.', 'data.') if 'user.' in parts[0] else parts[0])

            _to = parts[0].split('.')
            _from = parts[1].split('.')
            _to_loc = _to[0]
            _to_loc_key = _to[1]

            if _to_loc not in _remote_creds:
                _remote_creds['_' + _to_loc] = {}
                _remote_creds[_to_loc] = create_map_func(_remote_creds['_' + _to_loc])

            _remote_creds['_' + _to_loc][_to_loc_key] = (_from[0], _from[1])
            
    return _remote_creds


'''
Tests the parameters against the validator for a query run request/user to determine if
the remote resource is restricted from the user.
'''
def remote_resource_restriction(parameters, user, req):
    if not settings.REMOTE_RESOURCE_RESTRICTION_ENABLED or settings.REMOTE_RESOURCE_VALIDATOR:
        return False

    creds = get_resource_creds()
    headers = creds['headers'](user, req) if 'headers' in creds else None
    data = creds['data'](user, req) if 'data' in creds else None
    cookies = creds['cookies'](user, req) if 'cookies' in creds else None

    try:
        if body:
            resp = requests.post(get_validator(parameters), headers=headers, cookies=cookies, data=data)
        else:
            resp = requests.get(get_validator(parameters), headers=headers, cookies=cookies)
    except:
        return True

    return resp.status_code >= 300
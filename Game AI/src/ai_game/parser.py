"""
This module is used to parse the `params.json` file.
"""

import json

def load_params(path=None):
    if path is None:
        path = 'params.json'

    with open(path) as params_json:
        params = json.load(params_json)

    return params

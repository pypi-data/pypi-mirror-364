"""Submodule for defining response translations to file output"""

from typing import Generator, Callable
from json import dumps
from tqdm import tqdm

from httpx import Response

__all__ = ['FORMATS']

# Type alias for a list of responses mixed with exceptions
Responses = list[Response | BaseException]
FilterFunc = Callable[[Responses], bytes]

def _filter_responses(responses: Responses, fmt: str) -> Generator[Response, None, None]:
    for response in tqdm(responses, desc=f'Building {fmt}', colour='cyan'):
        if isinstance(response, Response) and response.is_success:
            yield response

def as_geojson(responses: Responses) -> bytes:
    geojson = {
        'type': None,
        'features': []
    }
    for response in _filter_responses(responses, 'geojson'):
        response_json: dict = response.json()
        for k in response_json:
            if k == 'features':
                geojson['features'].extend(response_json['features'])
            else:
                geojson.setdefault(k, response_json[k])
        if not geojson['type']:
            geojson['type'] = 'FeatureCollection'
    return dumps(geojson).encode('utf-8')

def as_json(responses: Responses) -> bytes:
    esri_json = {
        'displayFieldName': None,
        'fieldAliases': {},
        'geometryType': None,
        'spatialReference': {},
        'fields': [],
        'features': [],
    }
    for response in _filter_responses(responses, 'json'):
        response_json: dict = response.json()
        for k in response_json:
            if k == 'features':
                esri_json['features'].extend(response_json['features'])
            else:
                esri_json.setdefault(k, response_json[k])
    return dumps(esri_json).encode('utf-8')

def as_pbf(responses: Responses) -> bytes:
    return bytes().join(response.read() for response in _filter_responses(responses, 'pbf'))

def as_kmz(responses: Responses) -> bytes:
    raise NotImplementedError('KML Document conversion requires fastkml, use geojson instead')
    return bytes()

def as_html(responses: Responses) -> bytes:
    raise NotImplementedError
    return bytes()

# Define Format mappings
FORMATS: dict[str, FilterFunc] = {
    'geojson': as_geojson,
    'json'   : as_json,
    'pbf'    : as_pbf,
#    'html'   : as_html,
#    'kmz'    : as_kmz,
    
}
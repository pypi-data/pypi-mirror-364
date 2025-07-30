#! /usr/bin/env/python3

from __future__ import annotations

from pathlib import Path
import asyncio
import sys
import os
from argparse import ArgumentParser
from typing import (
    Generator,
    Any,
)
from tqdm import tqdm
from httpx import (
    get,
    AsyncClient,
    AsyncHTTPTransport,
    Request,
    Response,
    Limits,
)

from _conversion import FORMATS

# HTTP Transport Settings
TRANSPORT = AsyncHTTPTransport(retries=5)

# Get geojson
BASE_PARAMS= {
    'f'        : 'geojson', 
    'outfields': '*',
    'returnTrueCurves': True,
}

# Get Feature Count
COUNT_PARAMS = {
    'f'              : 'json',
    'where'          : '1=1',
    'returnCountOnly': True,
}

# TQDM Bar format
BAR_FORMAT = '{}'

from functools import wraps
from builtins import print as _print
VERBOSE = False
@wraps(_print)
def print(*args, **kwargs):
    if VERBOSE:
        _print(*args, **kwargs)
    return

def batch(count: int, size: int=2000, start: int=1) -> Generator[tuple[int, int], None, None]:
    while start <= count:
        yield (start, start+size-1)
        start += size

def build_requests(source: str, batches: Generator[tuple[int, int], None, None]) -> Generator[Request, None, None]:
    for start, stop in batches:
        where = {'where': f'OBJECTID >= {start} AND OBJECTID <= {stop}'}
        yield Request(
            'GET',
            source,
            params={**BASE_PARAMS, **where},
        )

async def fetch_features(source: str, max_connections: int=10, batch_size: int=2000) -> bytes:
    count: int = get(source, params=COUNT_PARAMS).json()['count']
    print(f"Found {count} features...")
    requests = list(build_requests(source, batch(count, size=batch_size)))
    async with AsyncClient(limits=Limits(max_connections=max_connections, keepalive_expiry=None), transport=TRANSPORT) as client:
        print(f"Gathering {len(requests)} tasks...")
        tasks = [client.send(request) for request in requests]
        
        print(f"Sending requests...")
        responses: list[Response | BaseException] = []
        for index in tqdm(range(0, len(tasks), max_connections), 
                          desc='Extracting Features',
                          colour='green',
                          dynamic_ncols=True):
            responses.extend(await asyncio.gather(*tasks[index:index+max_connections], return_exceptions=True))
        
        _print(f"Building {BASE_PARAMS['f']}")
        
        failures = [
            resp for resp in responses 
            if isinstance(resp, Exception) or isinstance(resp, Response) and resp.is_error
        ]
        if failures:
            print(f'{len(failures)} requests failed!')
            for resp in failures:
                print(str(resp))
                
        if ( formatter := FORMATS.get(BASE_PARAMS['f']) ) is None:
            raise ValueError(f"{BASE_PARAMS['f']} format has no implemented compiler!")
        return formatter(responses)

def get_capabilities(source: str) -> dict[str, Any]:
    if source.endswith('/query'):
        source = source[:-6]
    return get(source, params={'f': 'json'}).json()
    
async def main(source: str, target: str, max_connections: int, batch_size: int):
    data = await fetch_features(source=source, max_connections=max_connections, batch_size=batch_size)
    target_file = Path(target).with_suffix(f".{BASE_PARAMS['f']}")
    if not target_file.parent.exists():
        target_file.parent.mkdir(exist_ok=True, parents=True)
    print("Writing file...")
    target_file.open('wb').write(data)
    print(f"Completed {target_file.name}!")

if __name__ == '__main__':
    parser = ArgumentParser(
        prog='Heathcliff Pro',
        usage='Extract Features from a public arcgis REST server',
    )
    parser.add_argument('source',
                      help='Feature Server to extract features from')
    parser.add_argument('target',
                      help='Output file for the extracted features. * at end will use service provided name')
    parser.add_argument('-m', '--max_con',
                      help='Maximum number of concurrent connections to make',
                      type=int,
                      default=10,
                      metavar='')
    parser.add_argument('-b', '--batch',
                      help='Amount of features to request per batch',
                      type=int,
                      default=1000,
                      metavar='')
    parser.add_argument('-f', '--format',
                        help=f'Format to request data in {set(FORMATS.keys())}',
                        type=str,
                        default='geojson',
                        metavar='')
    parser.add_argument('-v', '--verbose',
                        help='Toggle Verbosity On',
                        action='store_true')
    parser.add_argument('--fields',
                             help='Fields to request from the service',
                             type=str,
                             default='*',
                             metavar='')
    args = parser.parse_args()
    
    # GET SOURCE URL
    source: str = args.source
    if not source.endswith('query'):
        source = f"{source}{'/' if not source.endswith('/') else ''}query"
    
    # GET CAPABILITIES
    capabilities = get_capabilities(source=source)
    supported_formats: str = capabilities.get('supportedQueryFormats', '')
    max_records: int = capabilities.get('maxRecordCount', 0)
    name: str = capabilities.get('name', 'out')
    available_fields: list[str] = [f['name'] for f in capabilities.get('fields', [])]
    VERBOSE = args.verbose
    
    # SET FIELDS
    fields: list[str] = args.fields.split()
    if fields != ['*']: 
        if not all(f in available_fields for f in fields):
            raise ValueError(f"Invalid field selection {set(fields)}, must be one of: {os.linesep.join(available_fields)}")
        _print(f"Pulling field{'s' if len(fields) > 1 else ''} {set(fields)}")
    BASE_PARAMS['outfields'] = fields
    
    # SET TARGET
    target: str = args.target
    if target.endswith('*'):
        _print(f'Using service name {name}...')
        target = f'{target[:-1]}{name}'
    
    # GET OUTPUT FORMAT
    q_format: str = args.format.lower()
    if q_format not in ( available := [fmt.lower() for fmt in supported_formats.split(', ')] ):
        _print(f"{q_format} not supported on server! Supported Formats: {supported_formats}. Defaulting to geojson...")
        if 'geojson' not in available:
            raise ValueError(f'No valid format available on server!')
        q_format = 'geojson'
    BASE_PARAMS['f'] = q_format
    
    # GET BATCHSIZE
    batch_size: int = int(args.batch)
    if batch_size > max_records:
        _print(f'batch_size of {batch_size} is greater than server supported max of {max_records}! Using server max...')
        batch_size = max_records-1
    
    # GET MAX CONNECTIONS
    max_connections: int = int(args.max_con)
    if max_connections < 1:
        _print(f'Max Connections must be >= 1 to make requests, setting to 1...')
        max_connections = 1
    
    # RUN REQUESTS
    try:
        asyncio.run(main(source=source, target=target, max_connections=max_connections, batch_size=batch_size))
    except KeyboardInterrupt:
        _print('Stopping...')
        sys.exit(0)
    except (RuntimeError, RuntimeWarning) as e:
        if isinstance(e.__cause__, KeyboardInterrupt):
            _print('Stopping...')
            sys.exit(0)
        print(f'Failed: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'Failed: {e}')
        sys.exit(1)
    sys.exit(0)
    
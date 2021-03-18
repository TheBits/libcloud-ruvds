import json
import os
from libcloud.common.types import InvalidCredsError
import vcr

from ruvdsdriver import RUVDSConnection

filter_query = (
    ('username', 'EMAIL'),
    ('password', 'PASSWORD'),
    ('key', 'KEY'),
)

def filter_response(response):
    try:
        del response['headers']['Set-Cookie']
    except KeyError:
        pass

    body = json.loads(response['body']['string'])
    if 'sessionToken' in body:
        body['sessionToken'] = 'SESSION_TOKEN'
        response['body']['string'] = json.dumps(body)

    return response 

with vcr.use_cassette('fixtures/logon.yaml', filter_query_parameters=filter_query, before_record_response=filter_response):
    resp = RUVDSConnection(os.getenv('RUVDS_EMAIL'), os.getenv('RUVDS_PASSWORD'), os.getenv('RUVDS_KEY'))
    print('logon ok')

with vcr.use_cassette('fixtures/logon_empty_email_and_password.yaml', filter_query_parameters=filter_query, before_record_response=filter_response):
    try:
        RUVDSConnection("", "", os.getenv('RUVDS_KEY'))
    except InvalidCredsError as e:
        print('empty email and password:', e)

with vcr.use_cassette('fixtures/logon_empty_email.yaml', filter_query_parameters=filter_query, before_record_response=filter_response):
    try:
        RUVDSConnection("", os.getenv('RUVDS_PASSWORD'), os.getenv('RUVDS_KEY'))
    except InvalidCredsError as e:
        print('empty email:', e)

with vcr.use_cassette('fixtures/logon_empty_password.yaml', filter_query_parameters=filter_query, before_record_response=filter_response):
    try:
        RUVDSConnection(os.getenv('RUVDS_EMAIL'), '', os.getenv('RUVDS_KEY'))
    except InvalidCredsError as e:
        print('empty password:', e)

with vcr.use_cassette('fixtures/logon_wrong_password.yaml', filter_query_parameters=filter_query, before_record_response=filter_response):
    try:
        RUVDSConnection(os.getenv('RUVDS_EMAIL'), 'PASSWORD', os.getenv('RUVDS_KEY'))
    except InvalidCredsError as e:
        print('wrong password:', e)

with vcr.use_cassette('fixtures/logon_empty_key.yaml', filter_query_parameters=filter_query, before_record_response=filter_response):
    try:
        RUVDSConnection(os.getenv('RUVDS_EMAIL'), os.getenv('RUVDS_PASSWORD'), '')
    except InvalidCredsError as e:
        print('empty key:', e)

with vcr.use_cassette('fixtures/logon_wrong_key.yaml', filter_query_parameters=filter_query, before_record_response=filter_response):
    try:
        RUVDSConnection(os.getenv('RUVDS_EMAIL'), os.getenv('RUVDS_PASSWORD'), 'KEY')
    except InvalidCredsError as e:
        print('wrong key:', e)
    
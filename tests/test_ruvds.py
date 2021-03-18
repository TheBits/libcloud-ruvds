import vcr
import pytest

from libcloud.common.types import InvalidCredsError
from ruvdsdriver import RUVDSConnection


@vcr.use_cassette('./tests/fixtures/logon.yaml')
def test_logon_ok():
    ruvds = RUVDSConnection('EMAIL', 'PASSWORD', 'KEY')
    assert ruvds.session_token == 'SESSION_TOKEN'


@vcr.use_cassette('./tests/fixtures/logon_empty_email_and_password.yaml')
def test_logon_empty_email_and_password():
    with pytest.raises(InvalidCredsError) as e:
        ruvds = RUVDSConnection('', '', 'KEY')
    assert e.value.value == 'Username is not specified or incorrect'


@vcr.use_cassette('./tests/fixtures/logon_empty_email.yaml')
def test_logon_empty_email():
    with pytest.raises(InvalidCredsError) as e:
        ruvds = RUVDSConnection('', 'PASSWORD', 'KEY')
    assert e.value.value == 'Username is not specified or incorrect'
    

@vcr.use_cassette('./tests/fixtures/logon_empty_password.yaml')
def test_logon_empty_password():
    with pytest.raises(InvalidCredsError) as e:
        ruvds = RUVDSConnection('EMAIL', '', 'KEY')
    assert e.value.value == 'Password is not specified'


@vcr.use_cassette('./tests/fixtures/logon_wrong_password.yaml')
def test_logon_wrong_password():
    with pytest.raises(InvalidCredsError) as e:
        ruvds = RUVDSConnection('EMAIL', 'PASSWORD', 'KEY')
    assert e.value.value == 'User not found or incorrect password'


@vcr.use_cassette('./tests/fixtures/logon_empty_key.yaml')
def test_logon_empty_key():
    with pytest.raises(InvalidCredsError) as e:
        ruvds = RUVDSConnection('EMAIL', 'PASSWORD', '')
    assert e.value.value == 'API key is not specified. Please visit account settings page.'


@vcr.use_cassette('./tests/fixtures/logon_wrong_key.yaml')
def test_logon_wrong_key():
    with pytest.raises(InvalidCredsError) as e:
        ruvds = RUVDSConnection('EMAIL', 'PASSWORD', 'KEY')
    assert e.value.value == 'Incorrect API key. Please visit account settings page.'


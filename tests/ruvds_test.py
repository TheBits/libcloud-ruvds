import functools
import json
import os
from collections import namedtuple
from pathlib import Path

import pytest
import vcr
from libcloud.common.types import InvalidCredsError

from ruvdsdriver import RUVDSConnection, RUVDSNodeDriver

cred_keys = ("username", "password", "key")


filter_query = (
    ("username", "USERNAME"),
    ("password", "PASSWORD"),
    ("key", "KEY"),
    ("sessionToken", "SESSION_TOKEN"),
)


def filter_response(response):
    try:
        del response["headers"]["Set-Cookie"]
    except KeyError:
        pass

    body = json.loads(response["body"]["string"])
    if "sessionToken" in body:
        body["sessionToken"] = "SESSION_TOKEN"
        response["body"]["string"] = json.dumps(body)

    return response


def vcr_record(f):
    @functools.wraps(f)
    def wrapper(*args, **kwds):
        path = Path("./tests/fixtures/") / f"{f.__name__}.yaml"
        kwargs = dict(
            filter_post_data_parameters=cred_keys,
            filter_query_parameters=filter_query,
            match_on=["method", "path"],
            path=str(path),
        )
        if not path.exists():
            kwargs["before_record_response"] = filter_response
        with vcr.use_cassette(**kwargs):
            return f(*args, **kwds)

    return wrapper


@pytest.fixture()
def ruvds_creds():
    Creds = namedtuple("Creds", cred_keys)
    creds = Creds(username=os.getenv("RUVDS_USERNAME"), password=os.getenv("RUVDS_PASSWORD"), key=os.getenv("RUVDS_KEY"))
    return creds


@vcr_record
def test_logon_ok(ruvds_creds):
    ruvds = RUVDSConnection(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    assert len(ruvds.session_token) in (13, 64)


@vcr_record
def test_logon_empty_username_and_password(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(username="", password="", key=ruvds_creds.key)
    assert e.value.value == "Username is not specified or incorrect"


@vcr_record
def test_logon_empty_username(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(username="", password=ruvds_creds.password, key=ruvds_creds.key)
    assert e.value.value == "Username is not specified or incorrect"


@vcr_record
def test_logon_invalid_username(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(username="invalid_username", password=ruvds_creds.password, key=ruvds_creds.key)
    assert e.value.value == "Username is not specified or incorrect"


@vcr_record
def test_logon_empty_password(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(username=ruvds_creds.username, password="", key=ruvds_creds.key)
    assert e.value.value == "Password is not specified"


@vcr_record
def test_logon_wrong_password(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(username=ruvds_creds.username, password="invalid_password", key=ruvds_creds.key)
    assert e.value.value == "User not found or incorrect password"


@vcr_record
def test_logon_empty_key(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(username=ruvds_creds.username, password=ruvds_creds.password, key="")
    assert e.value.value == "API key is not specified. Please visit account settings page."


@vcr_record
def test_logon_wrong_key(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(username=ruvds_creds.username, password=ruvds_creds.password, key="invalid_key")
    assert e.value.value == "Incorrect API key. Please visit account settings page."


@vcr_record
def test_locations(ruvds_creds):
    ruvds = RUVDSNodeDriver(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    locs = ruvds.list_locations()
    assert len(locs) == 11


@vcr_record
def test_create_node(ruvds_creds):
    ruvds = RUVDSNodeDriver(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    response = ruvds.create_node()
    assert response is True


@vcr_record
def test_create_node_error(ruvds_creds):
    ruvds = RUVDSNodeDriver(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    response = ruvds.create_node()
    assert response is False

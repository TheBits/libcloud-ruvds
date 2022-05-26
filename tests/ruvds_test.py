import functools
import json
import os
from collections import namedtuple
from pathlib import Path

import pytest
import vcr
from libcloud.common.types import InvalidCredsError
from libcloud.compute.base import NodeImage

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
def username() -> str:
    key = os.getenv("RUVDS_USERNAME")
    if key is None:
        pytest.exit("set up RUVDS_USERNAME environment variable")
    return str(key)


@pytest.fixture()
def password() -> str:
    key = os.getenv("RUVDS_PASSWORD")
    if key is None:
        pytest.exit("set up RUVDS_PASSWORD environment variable")
    return str(key)


@pytest.fixture()
def key() -> str:
    key = os.getenv("RUVDS_KEY")
    if key is None:
        pytest.exit("set up RUVDS_KEY environment variable")
    return str(key)


@pytest.fixture()
def ruvds_creds(username, password, key):
    Creds = namedtuple("Creds", cred_keys)
    creds = Creds(username=username, password=password, key=key)
    return creds


@pytest.fixture()
@vcr.use_cassette("./tests/fixtures/test_logon_ok.yaml")
def compute_conn(ruvds_creds):
    return RUVDSNodeDriver(ruvds_creds.username, ruvds_creds.key, password=ruvds_creds.password)


@vcr_record
def test_logon_ok(ruvds_creds):
    ruvds = RUVDSConnection(ruvds_creds.username, ruvds_creds.key, password=ruvds_creds.password)
    assert len(ruvds.session_token) in (13, 64)


@vcr_record
def test_logon_endless(ruvds_creds):
    ruvds = RUVDSConnection(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key, endless=1)
    assert len(ruvds.session_token) in (13, 64)


@vcr_record
def test_logon_empty_username_and_password(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection("", ruvds_creds.key, password="")
    assert e.value.value == "Username is not specified or incorrect"


@vcr_record
def test_logon_empty_username(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection("", ruvds_creds.key, password=ruvds_creds.password)
    assert e.value.value == "Username is not specified or incorrect"


@vcr_record
def test_logon_invalid_username(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection("invalid_username", ruvds_creds.key, password=ruvds_creds.password)
    assert e.value.value == "Username is not specified or incorrect"


@vcr_record
def test_logon_empty_password(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(ruvds_creds.username, ruvds_creds.key, password="")
    assert e.value.value == "Password is not specified"


@vcr_record
def test_logon_wrong_password(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(ruvds_creds.username, ruvds_creds.key, password="invalid_password")
    assert e.value.value == "User not found or incorrect password"


@vcr_record
def test_logon_empty_key(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(ruvds_creds.username, "", password=ruvds_creds.password)
    assert e.value.value == "API key is not specified. Please visit account settings page."


@vcr_record
def test_logon_wrong_key(ruvds_creds):
    with pytest.raises(InvalidCredsError) as e:
        RUVDSConnection(ruvds_creds.username, "invalid_key", password=ruvds_creds.password)
    assert e.value.value == "Incorrect API key. Please visit account settings page."


@vcr_record
def test_locations(compute_conn):
    locs = compute_conn.list_locations()
    assert len(locs) == 11


@vcr_record
def test_create_node(compute_conn):
    response = compute_conn.create_node()
    assert response is True


@vcr_record
def test_create_node_error(compute_conn):
    result = compute_conn.create_node()
    assert result is False


@vcr_record
def test_start_node(compute_conn):
    result = compute_conn.start_node(123)
    assert result is True


@vcr_record
def test_stop_node(compute_conn):
    result = compute_conn.stop_node(123)
    assert result is True


@vcr_record
def test_reboot_node(compute_conn):
    result = compute_conn.reboot_node(123)
    assert result is True


@vcr_record
def test_destroy_node(compute_conn):
    result = compute_conn.destroy_node(123)
    assert result is True


@vcr_record
def test_list_images(compute_conn):
    images = compute_conn.list_images()
    image = images.pop()
    assert image.id == "12"
    assert image.name == "Ubuntu 16.04 LTS (ENG)"
    assert isinstance(image, NodeImage)


@vcr_record
def test_get_image(compute_conn):
    image = compute_conn.get_image("12")
    assert image.id == "12"
    assert image.name == "Ubuntu 16.04 LTS (ENG)"
    assert isinstance(image, NodeImage)

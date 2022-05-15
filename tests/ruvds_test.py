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
def ruvds_creds():
    Creds = namedtuple("Creds", cred_keys)
    creds = Creds(username=os.getenv("RUVDS_USERNAME"), password=os.getenv("RUVDS_PASSWORD"), key=os.getenv("RUVDS_KEY"))
    return creds


@vcr_record
def test_logon_ok(ruvds_creds):
    ruvds = RUVDSConnection(ruvds_creds.username, ruvds_creds.key, password=ruvds_creds.password)
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
def test_locations(ruvds_creds):
    ruvds = RUVDSNodeDriver(ruvds_creds.username, ruvds_creds.key, password=ruvds_creds.password)
    locs = ruvds.list_locations()
    assert len(locs) == 11


@vcr_record
def test_create_node(ruvds_creds):
    ruvds = RUVDSNodeDriver(ruvds_creds.username, ruvds_creds.key, password=ruvds_creds.password)
    response = ruvds.create_node()
    assert response is True


@vcr_record
def test_create_node_error(ruvds_creds):
    ruvds = RUVDSNodeDriver(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    result = ruvds.create_node()
    assert result is False


@vcr_record
def test_start_node(ruvds_creds):
    ruvds = RUVDSNodeDriver(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    result = ruvds.start_node(123)
    assert result is True


@vcr_record
def test_stop_node(ruvds_creds):
    ruvds = RUVDSNodeDriver(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    result = ruvds.stop_node(123)
    assert result is True


@vcr_record
def test_reboot_node(ruvds_creds):
    ruvds = RUVDSNodeDriver(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    result = ruvds.reboot_node(123)
    assert result is True


@vcr_record
def test_destroy_node(ruvds_creds):
    ruvds = RUVDSNodeDriver(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    result = ruvds.destroy_node(123)
    assert result is True


@vcr_record
def test_list_images(ruvds_creds):
    ruvds = RUVDSNodeDriver(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    images = ruvds.list_images()
    image = images.pop()
    assert image.id == "12"
    assert image.name == "Ubuntu 16.04 LTS (ENG)"
    assert isinstance(image, NodeImage)


@vcr_record
def test_get_image(ruvds_creds):
    ruvds = RUVDSNodeDriver(username=ruvds_creds.username, password=ruvds_creds.password, key=ruvds_creds.key)
    image = ruvds.get_image("12")
    assert image.id == "12"
    assert image.name == "Ubuntu 16.04 LTS (ENG)"
    assert isinstance(image, NodeImage)

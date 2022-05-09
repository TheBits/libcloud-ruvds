import json
import warnings

from libcloud.common.base import Connection, JsonResponse
from libcloud.common.exceptions import RateLimitReachedError
from libcloud.common.types import InvalidCredsError, ServiceUnavailableError
from libcloud.compute.base import NodeDriver, NodeImage, NodeLocation
from libcloud.utils.py3 import httplib


class RUVDSResponse(JsonResponse):
    def success(self):
        return super().success() and '"errMessage"' not in self.body

    def parse_error(self):
        body = super().parse_error()

        # error codes https://ruvds.com/en-usd/use_api # sign-insection
        reject_reason = body["rejectReason"]
        if reject_reason in (1, 2, 3, 6, 7):
            raise InvalidCredsError(value=body["errMessage"])
        elif reject_reason == 5:
            raise ServiceUnavailableError()
        elif reject_reason == 8:
            raise RateLimitReachedError()

        return body


class RUVDSConnection(Connection):
    responseCls = RUVDSResponse
    session_token = None

    def __init__(self, *args, **kwargs):
        kwargs["url"] = "https://ruvds.com/"
        username = kwargs.pop("username", None)
        password = kwargs.pop("password", None)
        key = kwargs.pop("key", None)
        super().__init__(*args, **kwargs)
        data = dict(
            username=username,
            password=password,
            key=key,
            endless=0,
        )
        data = json.dumps(data)
        response = self.request(
            action="api/logon/",
            method="POST",
            data=data,
        )

        self.session_token = response.object["sessionToken"]

    def add_default_params(self, params):
        if self.session_token is not None:
            params.update(dict(sessionToken=self.session_token))
        return params


class RUVDSNodeDriver(NodeDriver):
    connectionCls = RUVDSConnection
    name = "RUVDS"
    website = "https://ruvds.com/"

    def list_locations(self):
        response = self.connection.request("api/datacenter")
        countries = {
            1: "RU",
            2: "CH",
            3: "GB",
            5: "RU",
            8: "RU",
            9: "RU",
            10: "RU",
            21: "DE",
            25: "RU",
            29: "NL",
            32: "RU",
        }

        locations = []
        for loc in response.object["datacenters"]:
            location_id = loc["id"]
            location_name = loc["name"]
            country = countries.get(location_id)
            if country:
                locations.append(NodeLocation(location_id, location_name, country, self))
            else:
                warnings.warn(f"Unknown datacenter: ({location_id}) {location_name}")
        return locations

    def list_images(self):
        images = []
        response = self.connection.request("api/os")
        for image in response.object["os"]:
            images.append(NodeImage(image["Id"], image["Name"], self))
        return images

    def list_sizes(self, location=None):
        if location is not None:
            warnings.warn("location argument ignored")
        response = self.connection.request("api/tariff")
        return response

    def list_nodes(self):
        response = self.connection.request("api/servers")
        nodes = []
        if response.object["rejectReason"] == 0:
            for n in response.object["items"]:
                nodes.append(n)
        return nodes

    def create_node(self, **kwargs) -> bool:
        response = self.connection.request("api/server/create/", params=kwargs, method="POST")
        return response.status == httplib.OK and response.object.get("rejectReason") == 0

    def _run_command(self, command: str, node_id: int):
        params = {
            "type": command,
            "id": node_id,
        }
        response = self.connection.request("api/server/command/", params=params, method="POST")
        return response.status == httplib.OK and response.object.get("rejectReason") == 0

    def stop_node(self, node_id: int) -> bool:
        return self._run_command("stop", node_id)

    def start_node(self, node_id: int) -> bool:
        return self._run_command("start", node_id)

    def reboot_node(self, node_id: int) -> bool:
        return self._run_command("reset", node_id)

    def destroy_node(self, node_id: int) -> bool:
        return self._run_command("remove", node_id)

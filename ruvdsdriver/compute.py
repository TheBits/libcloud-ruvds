from libcloud.compute.base import NodeDriver, NodeImage, NodeLocation
from libcloud.compute.providers import set_driver

from . import RUVDSConnection


set_driver("ruvds", "ruvdsdriver.compute", "RUVDSNodeDriver")



class RUVDSNodeDriver(NodeDriver):
    connectionCls = RUVDSConnection
    name = 'RUVDS'
    website = 'https://ruvds.com/'

    def list_locations(self):
        response = self.connection.request('api/datacenter')
        countries = {
            1: 'RU',
            2: 'CH',
            3: 'GB',
            5: 'RU',
            8: 'RU',
            9: 'RU',
            10: 'RU',
            21: 'DE',
            25: 'RU',
        }

        locations = []
        for loc in response.object['datacenters']:
            location_id = loc['id']
            location_name = loc['name']
            country = country.get(location_id)
            if country:
                locations.append(NodeLocation(location_id, location_name, country, self))
            else:
                warnings.warn(f'Unknown datacenter: ({location_id}) {location_name}')
        return locations

    def list_images(self):
        images = []
        response = self.connection.request('api/os')
        for image in response.object['os']:
            images.append(NodeImage(image['Id'], image['Name'], self))
        return images

    def list_sizes(self, location=None):
        if location is not None:
            warnings.warn('location argument ignored')
        response = self.connection.request('api/tariff')
        from prettyprinter import cpprint
        cpprint(response.object)

    def list_nodes(self):
        response = self.connection.request('api/servers')
        nodes = []
        if response.object['rejectReason'] == 0 :
            for n in response.object['items']:
                nodes.append(n)
        from prettyprinter import cpprint
        cpprint(response.object)
        return nodes

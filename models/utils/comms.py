import socket
import sys
import time
import re
import xml.dom.minidom
import os
import json

if sys.version_info < (3, 0):
    import httplib
else:
    import http.client as httplib


class Comms(object):
    """
    Communication with the bridge.
    """

    def __init__(self):
        self.get_bridge_data()

    def get_bridge_data(self):
        """
        Get the bridge IP and user from 'bridge.cfg'.

        If there is data in the file validate it.
        If there is no data to validate, restart the whole process - scan for IP and add user when bridge is found.

        :return None
        """

        try:
            print('Attempting to use stored config')
            f = open(os.path.join(os.path.abspath('.'), 'bridge.cfg'), 'r')
            f.seek(0)
            self.bridge_ip = f.readline().replace('\n', '')
            self.bridge_user = f.readline().replace('\n', '')
            f.close()
            print('Done reading stored config')
        except IOError:
            print('Failed reading stored config')
            self.bridge_user = ''
            self.init_bridge_data()
            return

        if not self.verify_bridge_data():
            self.init_bridge_data()
        print('Connection successful')

    def verify_bridge_data(self):
        """
        Validate the bridge IP and user from 'bridge.cfg'.

        Validate the bridge IP by sending HTTP GET for 'http://<bridgeIP>:80/description.xml'.
        Parse the resulted XML for <modelName> against Philips hue bridge.

        :return None
        """
        if sys.version_info < (3, 0):
            conn_exception = socket.error
        else:
            conn_exception = TimeoutError
        try:
            print('Validating bridge IP by sending HTTP GET to http://' + str(self.bridge_ip) + '/description.xml')
            conn = httplib.HTTPConnection(self.bridge_ip, 80)
            conn.request('GET', '/description.xml')
        except (conn_exception):
            print('Failed to get HTTP response, bridge IP not valid')
            return False

        print('Getting HTTP response')
        r1 = conn.getresponse()
        data = r1.read()
        try:
            dom = xml.dom.minidom.parseString(data)
        except xml.parsers.expat.ExpatError:
            print('XML parse error')
            return False
        model_name = dom.getElementsByTagName('modelName')[0].firstChild.nodeValue
        print('Parsing XML from HTTP response')
        if (not set(['Philips', 'hue', 'bridge']).issubset(model_name.split()) or
                isinstance(self.get(''), list)):
            print('Bridge IP or user not valid')
            return False
        print('Bridge IP and user are valid')
        return True

    def init_bridge_data(self):
        """
        Raise exception if bridge was not found.

        :return None
        """

        print('Attempting to find bridge IP')
        found = False
        for ip, url in self._scan():
            print('Checking IP = ' + str(ip) + ', URL = ' + str(url) + ' from SSDP scan results')
            if self.write_bridge_data(ip, url):
                found = True
                break
        if not found:
            raise RuntimeError('Bridge not found !!!')

    def _scan(self):
        """
        Scans for the bridge IP.

        Send out an UDP packet to multicast address 239.255.255.250:1900 (for IPv4).
        Parse each response LOCATION URL (the bridge will respond with 'LOCATION: http://<IP>:80/description.xml').

        :return (IP, URL)
        """

        # get your IP address
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except (socket.error):
            print('Failed to create socket')
            sys.exit()

        try:
            # let's hope there is an internet connection
            s.connect(('meethue.com', 80))
        except:
            # if not... (this doesn't even have to be reachable)
            s.connect(('10.255.255.255', 0))
        finally:
            local_interface = s.getsockname()[0]
            s.close()

        found = False
        dest_ips = []

        # send HTTP M-SEARCH as UDP multicast (239.255.255.250:1900 for IPv4)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        except (socket.error):
            print('Failed to create socket')
            sys.exit()

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 12)
        sock.settimeout(1)
        sock.bind((local_interface, 0))

        try:
            sock.sendto(('M-SEARCH * HTTP/1.1\r\n'
                         'HOST: 239.255.255.250:1900\r\n'
                         'MAN: "ssdp:discover"\r\n'
                         'MX: 1\r\n'
                         'ST: ssdp:all\r\n\r\n').encode('utf-8'),
                        ('239.255.255.250', 1900))
        except (socket.error):
            print('Failed to send M-SEARCH on ' + local_interface)
            sys.exit()

        initial_time = time.time()

        # parse each response received for the UDP packet sent (there could be more than one device responding)
        while 1:
            if time.time() - initial_time > 10:
                break
            try:
                data = sock.recv(1024).decode('ascii', 'ignore')
                if data:
                    ip = port = url = ''
                    for line in data.split('\n'):
                        # try to extract IP, port, URL from LOCATION tag response
                        res = re.match(r'^LOCATION:\s*http://([\d]+.[\d]+.[\d]+.[\d]+):([\d]+)(/[\w./-]+)', line)
                        if res:
                            ip = res.group(1)
                            port = res.group(2)
                            url = res.group(3).replace('\r', '')
                            break

                    # check if extracted data is valid
                    if ip == '':
                        continue
                    # further a HTTP GET message will be sent, port must be 80
                    if port != '80':
                        continue
                    # the same device can send the same response more than once
                    if ip not in dest_ips:
                        dest_ips.append(ip)
                        found = True
                        # a valid and unique pair of IP, URL that can be further used
                        yield (ip, url)
                    else:
                        continue

            except (socket.error):
                print('Waiting to receive NOTIFY to ' + local_interface)
                time.sleep(1)

        sock.close()
        if not found:
            raise RuntimeError('Bridge not found !!!')

    def write_bridge_file(self):
        """
        Write bridge IP and user in 'bridge.cfg'

        :return None
        """

        f = open(os.path.join(os.path.abspath('.'), 'bridge.cfg'), 'w+')
        f.seek(0)
        f.write(self.bridge_ip + '\n' + self.bridge_user + '\n')
        f.close()

    def write_bridge_data(self, ip, url):
        """
        Parse the XML obtained from IP and URL and check <modelName> for Philips hue bridge.

        If the device is indeed a Philips hue bridge, then we have our bridge IP, otherwise exception is raised.
        Try to add a new bridge user and write it in 'bridge.cfg' if none is given or existing one is not valid.

        :param ip: IP extracted from LOCATION tag in the HTTP response.
        :param url: URL extracted from LOCATION tag in the HTTP response (bridge responds with 'description.xml').
        :return True is valid bridge IP and user were written in 'bridge.cfg' or False otherwise.
        """

        # get XML from 'http://<ip>:80/<url>'
        conn = httplib.HTTPConnection(ip, 80)
        conn.request('GET', url)
        r1 = conn.getresponse()
        res = r1.read()
        dom = xml.dom.minidom.parseString(res)
        model_name = dom.getElementsByTagName('modelName')[0].firstChild.nodeValue

        # check <modelName> from XML for Philips hue bridge device
        if set(['Philips', 'hue', 'bridge']).issubset(model_name.split()):
            print('Philips hue bridge found')
            self.model_number = dom.getElementsByTagName('modelNumber')[0].firstChild.nodeValue
            self.serial_number = dom.getElementsByTagName('serialNumber')[0].firstChild.nodeValue
            self.bridge_ip = ip

            # no bridge user present in 'bridge.cfg' or existing one is not valid
            if (self.bridge_user == '') or isinstance(self.get(''), list):
                print('No bridge user present in bridge.cfg or existing one is not valid')
                self.bridge_user = ''
                initial_time = time.time()
                while 1:
                    if time.time() - initial_time > 30:
                        break
                    data = self.post('', '{"devicetype":"PieShine#user"}')
                    if 'success' in data[0].keys():
                        self.bridge_user = data[0]['success']['username']
                        print('New user added: ' + self.bridge_user)
                    else:
                        if ((data[0]['error']['type'] == 101) or
                                (data[0]['error']['description'] == 'link button not pressed')):
                            print('Press the bridge button to add a new user !')
                            time.sleep(10)
                        else:
                            print(
                                'Error ' + str(data[0]['error']['type']) + ' : ' + str(data[0]['error']['description']))
                    if self.bridge_user != '':
                        break
                if self.bridge_user == '':
                    raise RuntimeError('Failed to add a new user and write configuration file !!!')
            # got valid bridge IP and user, writing in 'bridge.cfg'
            print('Got valid bridge IP and user, writing in bridge.cfg')
            self.write_bridge_file()
            return True

        # device is not Philips hue bridge
        return False

    def get(self, url_suffix):
        """
        Get data from the bridge. See 'http://<bridgeIP>/debug/clip.html'.

        :param url_suffix: Object to get (i.e. 'lights', 'groups', 'schedules', 'config', 'scenes', 'rules', etc.).
        :return Requested data in JSON format.
        """

        conn = httplib.HTTPConnection(self.bridge_ip, 80)
        conn.request('GET', r'/api/' + self.bridge_user + r'/' + url_suffix)
        data = conn.getresponse().read()
        conn.close()
        return json.loads(data.decode('utf-8'))

    def put(self, url_suffix, data):
        """
        Set data on the bridge. See 'http://<bridgeIP>/debug/clip.html'.

        :param url_suffix: Object to set (i.e. 'lights', 'groups', 'schedules', 'config', 'scenes', 'rules', etc.).
        :param data: data to send to the bridge
                    (Change the brightness of a light to 200:
                     url_suffix = 'lights/<light_id>/state'
                     data = '{"bri":200}')
        :return None
        """

        conn = httplib.HTTPConnection(self.bridge_ip, 80)
        conn.request('PUT', r'/api/' + self.bridge_user + r'/' + url_suffix, data)
        conn.close()

    def post(self, url_suffix, data):
        """
        Add data to the bridge. See 'http://<bridgeIP>/debug/clip.html' and 'post_<obj>' methods.

        :param url_suffix: Object to which the data is added
                           (i.e. 'lights', 'groups', 'schedules', 'config', 'scenes', 'rules', etc.).
        :param data: data to add to the bridge
                    (Add a group having the name 'Group X' and containing lights with ids 2 and 4:
                     url_suffix = 'group'
                     data = '{"name":"Group X", "lights":["2", "4"]}')
        :return response in JSON format
        """

        conn = httplib.HTTPConnection(self.bridge_ip, 80)
        conn.request("POST", r'/api/' + url_suffix, data, {"Accept": "text/plain"})
        response = conn.getresponse()
        if (response.status == httplib.OK) and (response.reason == 'OK'):
            data = json.loads(response.read().decode('utf-8'))
        else:
            data = None
        conn.close()
        return data

    def delete(self, url_suffix):
        """
        Delete data from the bridge. See 'http://<bridgeIP>/debug/clip.html' and 'delete_<obj>' methods.

        :param url_suffix: Object to which the data is deleted
                           (i.e. 'lights', 'groups', 'schedules', 'config', 'scenes', 'rules', etc.).
        :return response in JSON format
        """

        conn = httplib.HTTPConnection(self.bridge_ip, 80)
        conn.request("DELETE", r'/api/' + self.bridge_user + r'/' + url_suffix)
        response = conn.getresponse()
        if (response.status == httplib.OK) and (response.reason == 'OK'):
            data = json.loads(response.read().decode('utf-8'))
        else:
            data = None
        conn.close()
        return data

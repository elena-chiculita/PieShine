import time
import pprint
from models.lights import Lights
from models.groups import Groups
from models.utils.comms import Comms


class Bridge(object):
    """
    Access the bridge along with all the lights, groups, etc. from the setup.
    """

    def __init__(self):
        self._comms = Comms()                           # bridge communication
        self.lights = Lights(self._comms)               # collection of lights (acting as a dictionary)
        self.groups = Groups(self._comms, self.lights)  # collection of groups (acting as a dictionary)

    def post_group(self, light_ids, name=None):
        """
        Creates a new group (if name is not given, one random generated will be assigned).
        Verify the group creation:
        - from 'bridge.groups. <TAB pressed>' or
        - see 'http://<bridgeIP>/debug/clip.html', GET '/api/<bridgeUser>/groups/'.

        :param light_ids: List of light ids.
        :param name: Name of the group (optional parameter).
        :return None
        """

        lights_str = ''
        i = 0
        for light_id in light_ids:
            i += 1
            lights_str += "\"" + str(light_id) + "\"" + ('' if i == len(light_ids) else ',')
        name_str = ''
        if name:
            name_str = "\"" + str(name) + "\""

        data = self._comms.post(self._comms.bridge_user + 'r/groups',
                                '{' + ('"name":' + name_str + ',' if name else '') + '"lights":[' + lights_str + ']}')
        if 'success' in data[0].keys():
            group_id = data[0]['success']['id']
            print('New group added: ' + ('name: ' + name_str + ', ' if name else '') + 'id: ' + str(
                group_id) + ', lights: ' + str(light_ids))
            self.groups._add_group(self._comms, group_id, self.lights)
        else:
            print('Error ' + str(data[0]['error']['type']) + ' : ' + str(data[0]['error']['description']))

    def delete_group(self, group_id):
        """
        Delete a group. See 'http://<bridgeIP>/debug/clip.html', DELETE '/api/<bridgeUser>/groups/<group_id>'.

        :param group_id: Group id to be deleted.
        :return None.
        """

        self.groups._delete_group(group_id)
        data = self._comms.delete(r'groups/' + str(group_id))
        if 'success' in data[0].keys():
            print('Group deleted: ' + str(group_id))
        else:
            print('Error ' + str(data[0]['error']['type']) + ' : ' + str(data[0]['error']['description']))

    def post_user(self):
        """
        Creates a new random generated user id having #name='PieShine#user'.
        Verify the user creation:
        - by calling bridge._comms.display_users() or
        - see 'whitelist' at 'http://<bridgeIP>/debug/clip.html', GET '/api/<bridgeUser>/config/'.

        :return None
        """

        data = self._comms.post('', '{"devicetype":"PieShine#user"}')
        if 'success' in data[0].keys():
            self.bridge_user = data[0]['success']['username']
            print('New user added: ' + self.bridge_user)
        else:
            if data[0]['error']['type'] == 101 or data[0]['error']['description'] == 'link button not pressed':
                print('Press the bridge button to add a new user !')
            else:
                print('Error ' + str(data[0]['error']['type']) + ' : ' + str(data[0]['error']['description']))

    def delete_user(self, user_id):
        """
        Delete a user. See 'http://<bridgeIP>/debug/clip.html', DELETE '/api/<bridgeUser>/config/whitelist/<user_id>'.

        :param user_id: User id to be deleted.
        :return None.
        """

        data = self._comms.delete(r'config/whitelist/' + str(user_id))
        if 'success' in data[0].keys():
            print('User deleted: ' + str(user_id))
        else:
            print('Error ' + str(data[0]['error']['type']) + ' : ' + str(data[0]['error']['description']))

    def display_users(self):
        """
        Display existing users. See 'whitelist' at 'http://<bridgeIP>/debug/clip.html', GET '/api/<bridgeUser>/config/'.

        :return None
        """

        pp = pprint.PrettyPrinter(indent=4)
        res = self._comms.get('config')
        if 'whitelist' in res.keys():
            pp.pprint(res['whitelist'])

    def test(self):
        """
        Test framework.

        :return None
        """

        self.passed = self.failed = 0
        self.exec_time = 0
        print('')

        passed = failed = 0
        start = time.time()
        for light in self.lights.values():
            light._test()
            self.passed += light.passed
            self.failed += light.failed
            passed += light.passed
            failed += light.failed
            self.exec_time += light.exec_time
        m, s = divmod(time.time() - start, 60)
        h, m = divmod(m, 60)
        print('======== [TOTAL ALL LIGHTS] TOTAL PASSED : %d , TOTAL FAILED : %d , TIME = %dmin:%02ds ========\n\n' % (
            passed, failed, m, s))

        passed = failed = 0
        start = time.time()
        for group in self.groups.values():
            group._test()
            self.passed += group.passed
            self.failed += group.failed
            passed += group.passed
            failed += group.failed
            self.exec_time += group.exec_time
        m, s = divmod(time.time() - start, 60)
        h, m = divmod(m, 60)
        print('======== [GROUPS COLLECTION] TOTAL PASSED : %d , TOTAL FAILED : %d , TIME = %dmin:%02ds ========\n\n' % (
                passed, failed, m, s))

        passed = failed = 0
        start = time.time()
        self.lights._test()
        self.passed += self.lights.passed
        self.failed += self.lights.failed
        passed += self.lights.passed
        failed += self.lights.failed
        self.exec_time += self.lights.exec_time
        m, s = divmod(time.time() - start, 60)
        h, m = divmod(m, 60)
        print('======== [LIGHTS COLLECTION] TOTAL PASSED : %d , TOTAL FAILED : %d , TIME = %dmin:%02ds ========\n\n' % (
            passed, failed, m, s))

        m, s = divmod(self.exec_time, 60)
        h, m = divmod(m, 60)
        print('======== [BRIDGE SUMMARY] TOTAL PASSED : %d , TOTAL FAILED : %d , TIME = %dmin:%02ds ========\n' % (
            self.passed, self.failed, m, s))

if __name__ == "__main__":
    bridge = Bridge()

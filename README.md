# PieShine
Python interactive shell for controlling Philips hue lights.

## Features
* Compliant with the Philips Hue API 1.16.0
* Support for Lights and Groups (more to come)
* Compatible with Python 2.7 and Python 3.5.2

## Prerequisites
Python 2.7 or Python 3.5.2

## Running
```python
python pysh.py bridge.py
```
or
```python
./pysh.py bridge.py
```
The script will scan for the bridge IP and if found, you must create a new user by pressing the bridge button (you will be notified when to press). IP and user will be saved in 'bridge.cfg' and subsequent runs of the script will restore IP and user from the file.

## Usage

### Controlling the lights

To see available lights:
```python
bridge.lights. # <TAB pressed>
```

For example the name of a light is "Living Tall" and it's a colored light.

To see available settings for a light:
```python
bridge.lights.LivingTall. # <TAB pressed>
```
**GET**
```python
bridge.lights.LivingTall.on
bridge.lights.LivingTall.bri
bridge.lights.LivingTall.alert
bridge.lights.LivingTall.effect
bridge.lights.LivingTall.colormode
bridge.lights.LivingTall.ct
bridge.lights.LivingTall.hue
bridge.lights.LivingTall.sat
bridge.lights.LivingTall.gamut
bridge.lights.LivingTall.xy
bridge.lights.LivingTall.id
bridge.lights.LivingTall.name
bridge.lights.LivingTall.type
bridge.lights.LivingTall.reachable
bridge.lights.LivingTall.refresh_time
bridge.lights.LivingTall.manufacturer_name
bridge.lights.LivingTall.model_id
bridge.lights.LivingTall.unique_id
bridge.lights.LivingTall.sw_version
```
**SET** (along with some examples)
```python
bridge.lights.LivingTall.turn_off()
bridge.lights.LivingTall.turn_on()
bridge.lights.LivingTall.set_bri(255)
bridge.lights.LivingTall.set_alert('select')
bridge.lights.LivingTall.set_effect('colorloop')
bridge.lights.LivingTall.set_effect('none')
```

Color can be set by:

- hue and saturation
```python
bridge.lights.LivingTall.set_hue(30000)
bridge.lights.LivingTall.set_sat(150)
```
- color temperature
```python
bridge.lights.LivingTall.set_ct(200)
```
- gamut coordinates
```python
bridge.lights.LivingTall.set_xy(0.4, 0.4)
```
- RGB values (if the resulting color is outside of the supported gamut the calculated XY coordinates will be aproximated to the nearest 
point on the edge of the gamut on a best-effort basis)
```python
bridge.lights.LivingTall.set_color(255, 255, 255)
```

SET methods can be applied to all lights: 
```python
bridge.lights. # <TAB pressed>

bridge.lights.turn_off()
bridge.lights.turn_on()
bridge.lights.set_bri(255)
bridge.lights.set_alert('select')
#etc.
```

Display information about all lights:
```python
bridge.lights
```

Display information about one light:
```python
bridge.lights.LivingTall
```

### Controlling the groups

To see all available groups:
```python
bridge.groups. # <TAB pressed>
```

For example the name of a group is "Living".

To see all lights from the group and access these like described in the lights chapter:
```python
bridge.groups.Living. # <TAB pressed>

bridge.groups.Living.LivingTall
bridge.groups.Living.LivingShort
#etc.

bridge.groups.Living.LivingTall. # <TAB pressed>
bridge.groups.Living.LivingTall.turn_off()
bridge.groups.Living.LivingTall.turn_on()
bridge.groups.Living.LivingTall.on
#etc.
```

SET methods supported by the lights can also be called for the whole group:
```python
bridge.groups.Living. # <TAB pressed>

bridge.groups.Living.turn_off()
bridge.groups.Living.turn_on()
#etc.
```

Display information about all groups:
```python
bridge.groups
```

Display information about all lights from a group:
```python
bridge.groups.Living
```

Groups can be created by specifying the lights associated as a list of ids (name is optional):
```python
bridge.lights
(1) * Living Tall * On * bri = 254 * Gamut B [x,y] = [0.5268, 0.4133] * sat = 226 * hue = 12510 * ct = 500  
(2) * Living Short * On * bri = 254 * Gamut B [x,y] = [0.5268, 0.4133] * sat = 226 * hue = 12510 * ct = 500 

bridge.post_group([1,2])
New group added: id: 8, lights: [1,2]

bridge.post_group([1,2], 'Living 2')
New group added: name: "Living 2", id: 9, lights: [1,2]
```

Deleting a group can be done by specifying the id:
```python
bridge.groups
(9) * Living 2 (LightGroup) *** Living Tall, Living Short
(8) * Group 1 (LightGroup) *** Living Tall, Living Short

bridge.delete_group(8)
Group deleted: 8
```

### Controlling the users

When creating a user you must press the bridge button first (id will be radomly generated and the name will be "PieShine#user"):
```python
bridge.post_user()
```

Display all users (id, create date, last use date, name):
```python
bridge.display_users()
```

Delete user by specifying the id:
```python
bridge.display_users()
    u'xg3EwQGabcV6QWqszyAvmZcJ3X9defJNVjDifZGb': {   u'create date': u'2016-12-10T03:05:56',
                                                     u'last use date': u'2016-12-10T03:26:24',
                                                     u'name': u'PieShine#user'}}
                                                     
bridge.delete_user('xg3EwQGabcV6QWqszyAvmZcJ3X9defJNVjDifZGb')
```

### Write your own scripts (how to access objects)

For example set brightness to 255 for all lights/groups.

* Access all the lights from the setup (one of the following will do):
```python
for light in bridge.lights.values():
    light.set_bri(255)
````
```python
[light.set_bri(255) for light in bridge.lights.values()]
```

* Access all the groups from the setup (one of the following will do):
```python
for group in bridge.groups.values():
    group.set_bri(255)
```
```python
[group.set_bri(255) for group in bridge.groups.values()]
```
```python
for group in bridge.groups.values():
    for light in group.values():
        light.set_bri(255)
```
```python
[light.set_bri(255) for group in bridge.groups.values() for light in group.values()]
```

## Running the tests

If you've changed the code remember to run the bridge test at some point to make sure you haven't ruined anything :)
```python
bridge.test()
```

Or to break the bridge test into more specific tests for light and group objects:
```python
bridge.lights.LivingTall._test()
bridge.lights._test()
bridge.groups.Living._test()
```

## Acknowledgments:

Many thanks for the `TAB` autocompletion and history file script: http://code.activestate.com/recipes/473900-history-and-completion-for-the-python-shell/ .

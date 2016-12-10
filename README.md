PieShine - Python interactive shell for controlling Philips hue lights


Features

Compliant with the Philips Hue API 1.16.0
Support for Lights and Groups (more to come)
Compatible with Python 2.7 and Python 3.5.2


Getting Started


Prerequisites

Python 2.7 or Python 3.5.2


Running

python pysh.py bridge.py
	or:
./pysh.py bridge.py


Usage

1. Controlling the lights

For example the name of a light is "Living Tall" and it's a colored light.

To see available settings: bridge.lights.LivingTall. <TAB pressed>

GET

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

SET (along with some examples)

bridge.lights.LivingTall.turn_off()
bridge.lights.LivingTall.turn_on()
bridge.lights.LivingTall.set_bri(255)
bridge.lights.LivingTall.set_alert('select')
bridge.lights.LivingTall.set_effect('colorloop')
bridge.lights.LivingTall.set_effect('none')

* Color can be set by:

- hue and saturation
bridge.lights.LivingTall.set_hue(30000)
bridge.lights.LivingTall.set_sat(150

- color temperature
bridge.lights.LivingTall.set_ct(200)

- gamut coordinates
bridge.lights.LivingTall.set_xy(0.4, 0.4)

- RGB values (if the resulting color is outside of the supported gamut the
calculated XY coordinates will be aproximated to the nearest point on the
edge of the gamut on a best-effort basis)
bridge.lights.LivingTall.set_color(255, 255, 255)

* test all available settings for a light
bridge.lights.LivingTall._test()


SET methods can be applied to all lights: bridge.lights. <TAB pressed>

bridge.lights.turn_off()
bridge.lights.turn_on()
bridge.lights.set_bri(255)
bridge.lights.set_alert('select')
etc.


2. Controlling the groups

To see all available groups: bridge.groups. <TAB pressed>

For example the name of a group is "Living".

SET methods supported by the lights can also be called for the whole group: bridge.groups.Living. <TAB pressed>

bridge.groups.Living.turn_off()
bridge.groups.Living.turn_on()
etc.

* test all available settings for a group
bridge.groups.Living._test()


3. Write your own scripts (how to access objects)

For example set brightness to 255 for all lights/groups.

a) Access all the lights from the setup:

for light in bridge.lights.values():
    light.set_bri(255)

[light.set_bri(255) for light in bridge.lights.values()]

b) Access all the groups from the setup:

Each of the following four will do:

for group in bridge.groups.values():
    group.set_bri(255)

[group.set_bri(255) for group in bridge.groups.values()]

for group in bridge.groups.values():
    for light in group.values():
        light.set_bri(255)

[light.set_bri(255) for group in bridge.groups.values() for light in group.values()]


Running the tests

If you've changed the code remember to call bridge.test() at some point to make sure you haven't ruined anything :)


Acknowledgments:

Many thanks for the <TAB> autocompletion and history file script: http://code.activestate.com/recipes/473900-history-and-completion-for-the-python-shell/ .

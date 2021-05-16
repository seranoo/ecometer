# ecometer
ECOMETER S to MQTT

Communicates using USB with the display unit. I'm using a Raspberry Pi 3. The Pi then sends the filling level (liters) and the temperature using MQTT to my Home Assistant installation.

You have to edit the .py file and include the IP-adress of your MQTT broker (e.g. Home Assistant) + username + password.

In my Home Assistant configuration.yaml I then include:

sensor:
  - platform: mqtt
    name: "Bajstank"
    state_topic: "homeassistant/bajstank"
    unit_of_measurement: "liter"
  - platform: mqtt
    name: "Bajstank_temp"
    state_topic: "homeassistant/bajstank_temp"
    unit_of_measurement: '°C'   

To install as a serrvice:

sudo systemctl --force --full edit my-ecometer.service

Paste the content of the .service file + save. Then run:

sudo systemctl enable my-ecometer.service

Reboot the Pi.

New values are available approximately every 30 minutes.  

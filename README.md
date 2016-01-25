# Purpose: 

Crouton Dashboard: http://crouton.mybluemix.net/crouton/gettingStarted (Available at: https://github.com/edfungus/Crouton)
is MQTT based dashboard for IoT, with automatic configuration.

This repository, has a simple monitoring agent that sends disk space and CPU load to the Dashboard.

# Running:

Modify the all.py file, on the first lines, the client name, the MQTT broker address and port.

To run just do:

	- pip install paho-mqtt		(Only needed once)
	- pip install psutil		(Only needed once)
	- source venv/bin/activate
	- python app.py

Then on the Crouton Dashboard register the device with the Odroid name (the default on this repository)
If another name is required, change on all.py the clientName variable.

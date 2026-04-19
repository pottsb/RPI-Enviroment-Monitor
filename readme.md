<p align="center">
  <img src="./example.png" alt="Grafana Dashboard example" />
</p>

# What
This project validates environmental data from a raspberry pi sense hat and one wire temperature sensors then writes them into influxDB version 3. This uses the newer flux query language and doesn't support InfluxDB version 2.

Data is validated to be in a sensible range and implausible rapid changes are rejected. This results in nice clean grafana plots.

# Why
I use the sense hat LED matrix to display the current humidity and temperature. Due to the proximity of the sense hat temperature sensor to the LED matrix this affects accuracy. The one wire sensors are more accurate and precise than the sense hat and allow logging from multiple sensors.

# How
w1_initsensors.py can be used to name sensors. when running main.py if no name is found the ID will be used. This script is designed for one new sensor to be added to the bus at a time.

# Limitations
Alerting is currently disabled as I've improved my ventilation system and no longer need to open my shed door when it gets too hot 🥳.

# To Do
This project has been working for eleven months at this point so I'm unlikely to make further improvements until they become required.

add error handling for the InfluxDBManager class<br />
add error handling for loading the .env file<br />
Move os.environ.get() calls to better places<br />
Remove value in normal range messages from the validateSensor class<br />
add print for sample wait time<br />
move to venv with requirements.txt<br />
add method to name sensors based on lowest temperature. Using an inverted air duster can to freeze the sensors could then be used to identify them. <br />

# Packages
sudo /usr/bin/python -m pip install influxdb-client<br />
sudo /usr/bin/python -m pip install w1thermsensor<br />
sudo /usr/bin/python -m pip install python-dotenv<br />
import logging
from w1thermsensor import W1ThermSensor
from classes.EnvironmentalSensor import EnvironmentalSensor
from classes.DisplayManager import DisplayManager
from influxdb_client import Point
from utils.persistant_data_manager import read_dict_from_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


SENSOR_CONFIG_FILENAME = "sensor_config.json"


class SensorManager:
    
    def __init__(self, senseHat):
        self.validateSensor = EnvironmentalSensor()
        self.senseHat = senseHat

    def get_w1_data(self):
        """
        Collects temperature data from 1-wire sensors, validates it, and prepares data points for InfluxDB.

        Parameters:

        Returns:
            list[Point]: A list of InfluxDB Point objects representing the temperature measurements that 
            passed validation. Returns an empty list if the sensor configuration file is not found or if 
            there are no valid measurements.
        """

        sensor_dict = read_dict_from_file(SENSOR_CONFIG_FILENAME)
        data_points = []

        if len(sensor_dict) == 0:
            logging.error("No sensor config found.")

        sensors = W1ThermSensor.get_available_sensors()
        for i in sensors:
            if i.id not in sensor_dict:
                logging.error("Uninitialized sensor found using ID.")
                sensor_name = i.id
            else:
                sensor_name = sensor_dict[i.id]

            sensor_temperature = i.get_temperature()

            if self.validateSensor.update_temperature(sensor_name, sensor_temperature):
                logging.info(f"Sensor {sensor_name} has temperature {sensor_temperature}°C")
                data_points.append(Point("temperature").tag("sensor", sensor_name).field("value", sensor_temperature))
                DisplayManager.display_success(self.senseHat)
            else:
                logging.error(f"Data validation failed for sensor {sensor_name} with temperature {sensor_temperature}°C")
                DisplayManager.display_fail(self.senseHat)

        return data_points

    def get_sensehat_data(self):
        """
        Collects temperature, pressure, and humidity data from the Sense HAT, validates it, and prepares 
        data points for InfluxDB.

        Parameters:

        Returns:
            list[Point]: A list of InfluxDB Point objects representing the environmental measurements 
            (temperature, pressure, humidity) that passed validation. Each point is tagged with the 
            sensor type ('sensehat') and contains fields for the respective validated measurement values.
        """
        
        data_points = []
        
        sensehat_temperature = round(self.senseHat.get_temperature(), 1)
        if self.validateSensor.update_temperature('sensehat', sensehat_temperature):
            logging.info(f"Sense HAT temperature: {sensehat_temperature}°C")
            data_points.append(Point("temperature").tag("sensor", "sensehat").field("value", sensehat_temperature))
            DisplayManager.display_success(self.senseHat)
        else:
            logging.error(f"Data validation failed for Sense HAT temperature: {sensehat_temperature}°C")
            DisplayManager.display_fail(self.senseHat)

        sensehat_pressure = round(self.senseHat.get_pressure(), 3)
        if self.validateSensor.update_pressure(sensehat_pressure):
            logging.info(f"Pressure: {sensehat_pressure}mb")
            data_points.append(Point("pressure").tag("sensor", "sensehat").field("value", sensehat_pressure))
            DisplayManager.display_success(self.senseHat)
        else:
            logging.error(f"Data validation failed for pressure: {sensehat_pressure}mb")
            DisplayManager.display_fail(self.senseHat)

        sensehat_humidity = round(self.senseHat.get_humidity(), 1)
        if self.validateSensor.update_humidity(sensehat_humidity):
            logging.info(f"Humidity: {sensehat_humidity}%")
            data_points.append(Point("humidity").tag("sensor", "sensehat").field("value", sensehat_humidity))
            DisplayManager.display_success(self.senseHat)
        else:
            logging.error(f"Data validation failed for humidity: {sensehat_humidity}%")
            DisplayManager.display_fail(self.senseHat)

        return data_points
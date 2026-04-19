from utils.persistant_data_manager import write_dict_to_file, read_dict_from_file
from w1thermsensor import W1ThermSensor

SENSOR_CONFIG_FILENAME = "sensor_config.json"


if __name__ == '__main__':

    sensor_dict = read_dict_from_file(SENSOR_CONFIG_FILENAME)

    if sensor_dict is None:
        sensor_dict = {}
        print("No sensor config file found. Creating a new one.")
    else:
        print("Sensor config file found. Reading it.")
        for key in sensor_dict:
            print(f"Sensor {key} is set to {sensor_dict[key]}")

    sensor = W1ThermSensor.get_available_sensors()
    for i in sensor:
        if i.id not in sensor_dict:
            sensor_dict[i.id] = 0
            
            print(f"New sensor {i.id} found. Please enter a name.")
            name = input("Enter a name for the sensor: ")
            sensor_dict[i.id] = name
        else:
            print(f"Sensor {i.id} already in the config file.")

    print(f"Writing sensor config to {SENSOR_CONFIG_FILENAME}")
    print(sensor_dict)

    write_dict_to_file(sensor_dict, SENSOR_CONFIG_FILENAME)
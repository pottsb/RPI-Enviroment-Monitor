from classes.InfluxDBManager import InfluxDBManager
from classes.SensorManager import SensorManager
from classes.DisplayManager import DisplayManager
from sense_hat import SenseHat
from dotenv import load_dotenv
from fastapi import FastAPI
import uvicorn
import os

import logging
import signal
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
SENSOR_CONFIG_FILENAME = os.environ.get("SENSOR_CONFIG_FILENAME")
SAMPLE_PERIOD = int(os.environ.get("SAMPLE_PERIOD"))
RECONNECT_INTERVAL = int(os.environ.get("RECONNECT_INTERVAL"))
URL = os.environ.get("URL")
TOKEN = os.environ.get("TOKEN")
ORG = os.environ.get("ORG")
BUCKET = os.environ.get("BUCKET")
DISPLAY_W1_SENSOR_NAME = os.environ.get("DISPLAY_W1_SENSOR_NAME")
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8000"))

shutdown_event = threading.Event()
api_server = None


def graceful_exit(signum, frame):
    logging.info("Shutdown signal received. Stopping threads.")
    shutdown_event.set()
    global api_server
    if api_server is not None:
        api_server.should_exit = True


def log_temperature():
    senseHat = SenseHat()
    sensor_manager = SensorManager(senseHat)
    influx_manager = InfluxDBManager(URL, TOKEN, ORG)

    try:
        while not shutdown_event.is_set():
            w_data = sensor_manager.get_w1_data()
            sensehat_data = sensor_manager.get_sensehat_data()
            data_points = w_data + sensehat_data

            if len(data_points) == 0:
                logging.error("No data points to write.")
                if shutdown_event.wait(SAMPLE_PERIOD):
                    break
                continue

            if not influx_manager.write_data(BUCKET, data_points):
                logging.error("Write failed.")
                if shutdown_event.wait(RECONNECT_INTERVAL):
                    break
                continue

            if shutdown_event.wait(SAMPLE_PERIOD):
                break

    except Exception as e:
        logging.exception(f"log_temperature encountered an error: {e}")
        shutdown_event.set()


def get_display_temperature(sensor_manager):
    if not DISPLAY_W1_SENSOR_NAME:
        return round(sensor_manager.senseHat.get_temperature(), 1)

    w_data = sensor_manager.get_w1_data()

    for data_point in w_data:
        sensor_name = None
        sensor_temperature = None

        tags = getattr(data_point, "_tags", {})
        fields = getattr(data_point, "_fields", {})

        if isinstance(tags, dict):
            sensor_name = tags.get("sensor")
        if isinstance(fields, dict):
            sensor_temperature = fields.get("value")

        if sensor_name == DISPLAY_W1_SENSOR_NAME and sensor_temperature is not None:
            return round(float(sensor_temperature), 1)

    return round(sensor_manager.senseHat.get_temperature(), 1)


def display_environmental_data_loop():
    senseHat = SenseHat()
    sensor_manager = SensorManager(senseHat)

    while not shutdown_event.is_set():
        try:
            temperature = get_display_temperature(sensor_manager)
            humidity = round(senseHat.get_humidity(), 1)
            DisplayManager.display_environmental_data(temperature, humidity, senseHat)
        except Exception as e:
            logging.exception(f"display_environmental_data_loop encountered an error: {e}")
            if shutdown_event.wait(1):
                break

    logging.info("Display loop stopped.")


def _point_to_response(data_point):
    measurement = getattr(data_point, "_name", None)
    tags = getattr(data_point, "_tags", {})
    fields = getattr(data_point, "_fields", {})
    return {
        "measurement": measurement,
        "tags": tags if isinstance(tags, dict) else {},
        "fields": fields if isinstance(fields, dict) else {}
    }


def run_api_loop():
    senseHat = SenseHat()
    sensor_manager = SensorManager(senseHat)
    app = FastAPI()

    @app.get("/w1")
    def get_w1_data():
        w_data = sensor_manager.get_w1_data()
        if len(w_data) == 0:
            return HTTPException(status_code=500, detail="No data available")
            
        return {"data": [_point_to_response(point) for point in w_data]}

    @app.get("/sensehat")
    def get_sensehat_data():
        sensehat_data = sensor_manager.get_sensehat_data()
        if len(sensehat_data) == 0:
            return HTTPException(status_code=500, detail="No data available")

        return {"data": [_point_to_response(point) for point in sensehat_data]}

    global api_server
    config = uvicorn.Config(app, host=API_HOST, port=API_PORT, log_level="info")
    api_server = uvicorn.Server(config)
    api_server.run()
    logging.info("API loop stopped.")

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, graceful_exit)
    signal.signal(signal.SIGINT, graceful_exit)

    log_thread = threading.Thread(target=log_temperature, name="log_temperature_thread")
    display_thread = threading.Thread(target=display_environmental_data_loop, name="display_loop_thread")
    api_thread = threading.Thread(target=run_api_loop, name="api_loop_thread")

    log_thread.start()
    display_thread.start()
    api_thread.start()

    try:
        while log_thread.is_alive() and display_thread.is_alive() and api_thread.is_alive():
            log_thread.join(timeout=0.5)
            display_thread.join(timeout=0.5)
            api_thread.join(timeout=0.5)
    except KeyboardInterrupt:
        graceful_exit(signal.SIGINT, None)
    finally:
        shutdown_event.set()
        if api_server is not None:
            api_server.should_exit = True
        log_thread.join()
        display_thread.join()
        api_thread.join()
        logging.info("Shutdown complete.")
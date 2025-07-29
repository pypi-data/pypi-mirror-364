# -*- coding: utf-8 -*-
from __future__ import annotations

from pioreactor.background_jobs.base import BackgroundJob
from pioreactor.whoami import get_unit_name, get_assigned_experiment_name
from pioreactor.utils import timing
from pioreactor.background_jobs.leader.mqtt_to_db_streaming import produce_metadata, register_source_to_sink, TopicToParserToTable
from pioreactor import types as pt
from pioreactor.config import config
from pioreactor.exc import HardwareNotFoundError

import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import click
import logging


def parser(topic: str, payload: pt.MQTTMessagePayload) -> dict:
    metadata = produce_metadata(topic)
    return {
        "experiment": metadata.experiment,
        "pioreactor_unit": metadata.pioreactor_unit,
        "timestamp": timing.current_utc_timestamp(),
        "measurement_type": "voc_ppm",
        "reading": float(payload),
    }


register_source_to_sink([
    TopicToParserToTable(
        "pioreactor/+/+/read_voc_sensor/voc_ppm",
        parser,
        "voc_sensor_readings",
    )
])


class ReadVOCSensor(BackgroundJob):
    job_name = "read_voc_sensor"

    published_settings = {
        "interval": {"datatype": "float", "settable": True, "unit": "s"},
        "voc_ppm": {"datatype": "float", "settable": False, "unit": "ppm"},
    }

    def __init__(self, unit: str, experiment: str):
        super().__init__(unit=unit, experiment=experiment)
        self.interval = config.getfloat(f"{self.job_name}.config", "interval")

        # Constants
        self.V_offset = 0.04      # Zero baseline voltage
        self.sensitivity = 0.625  # V per ppm

        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(i2c)
            self.ads.gain = 1
            self.chan = AnalogIn(self.ads, ADS.P0)
        except Exception:
            self.logger.error("ADS1115 not detected on I2C bus.")
            raise HardwareNotFoundError("ADS1115 not detected.")

        self.read_timer = timing.RepeatedTimer(self.interval, self.read_voc_sensor, run_immediately=True)
        self.read_timer.start()

    def set_interval(self, new_interval) -> None:
        self.read_timer.interval = new_interval
        self.interval = new_interval

    def read_voc_sensor(self) -> None:
        voltage = self.chan.voltage
        voc_ppm = max(0.0, (voltage - self.V_offset) / self.sensitivity)
        self.voc_ppm = voc_ppm
        self.logger.info(f"VOC reading: {voc_ppm:.3f} ppm")

    def on_sleeping(self):
        self.read_timer.pause()

    def on_sleeping_to_ready(self):
        self.read_timer.unpause()

    def on_disconnected(self):
        self.read_timer.cancel()


@click.command(name="read_voc_sensor")
def click_read_voc_sensor():
    unit = get_unit_name()
    experiment = get_assigned_experiment_name(unit)
    job = ReadVOCSensor(unit=unit, experiment=experiment)
    job.block_until_disconnected()


if __name__ == "__main__":
    click_read_voc_sensor()

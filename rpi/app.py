from dataclasses import dataclass
from ultralytics import YOLO
from picam import Camera
from detect import detect
from typing import Any
from time import sleep
from enum import Enum
from log import logger
import traceback
import requests
import json


class Application:
    class State(Enum):
        UNREGISTERED = 0
        IDLE = 1
        CAPTURING = 2

    @dataclass
    class ReadingData:
        reading: str = ''
        filename: str = ''
        timestamp: str = ''

    def __init__(self):
        self.config = json.loads(open('device.json', 'r').read())

        self.camera = Camera()
        self.model = YOLO(self.config['model']['path'], task='detect')

        self.state = Application.State.UNREGISTERED
        self.fetch_delay = self.config['server']['fetch_delay']
        self.last_reading = Application.ReadingData()
        self.send_image = False

        logger.info(f'delay: {self.fetch_delay}')

    def construct_url_params(self, url_params: dict[str, Any]):
        if url_params and len(url_params):
            return '?' + '&'.join([f'{k}={v}' for k, v in url_params.items()])
        return ''

    def construct_request_url(self, api: str, url_params: dict[str, Any] = None):
        return 'http://{}:{}{}{}'.format(
            self.config['server']['ip'],
            self.config['server']['port'],
            api,
            self.construct_url_params(url_params)
        )

    def get_reading(self) -> ReadingData:
        capture = self.camera.capture()
        logger.info(f'Capture: {capture.filename}')

        result = detect(
            capture.filename,
            self.model,
            self.config['model']['conf'],
            self.config['model']['imagesize'],
            self.config['model']['img_scale_method']
        )

        logger.info(f'Scan result: {result}')
        return Application.ReadingData(result, capture.filename, capture.timestamp)

    def send_reading(self, reading: ReadingData):
        logger.info(f'Send readings: "{reading.reading}" ({reading.timestamp})')
        requests.post(
            self.construct_request_url('/api/rpi/send_reading', {'id': self.config['device']['id']}),
            json={'reading': reading.reading, 'time': reading.timestamp},
        )

        if self.send_image:
            detect_filename = reading.filename.replace('.jpg', '_detect.jpg')
            logger.info(f'Send image: {detect_filename}')
            requests.post(
                self.construct_request_url('/api/rpi/send_detect_image'),
                files={'image': open(detect_filename, 'rb')}
            )

    def get_settings(self):
        logger.info('Requesting settings')

        response = requests.get(
            self.construct_request_url('/api/rpi/get_settings', {'id': self.config['device']['id']})
        )

        if response.status_code != 200:
            logger.error(f'[api/rpi/get_settings]: {response.status_code}')
            logger.debug(f'                        {response.text}')
            return

        payload = json.loads(response.text)

        logger.info('Received settings')
        self.fetch_delay = int(payload['timeout'])
        logger.info(f'New fetch_delay: {self.fetch_delay}s')

    def register(self):
        response = requests.get(
            self.construct_request_url('/api/rpi/register', {'id': self.config['device']['id']})
        )

        if response.status_code != 200:
            logger.error(f'[api/rpi/register]: {response.status_code}')
            logger.debug(f'                    {response.text}')
            return

        payload = json.loads(response.text)

        if 'status' in payload:
            if payload['status'] == 'registered':
                logger.info('Registered successfully')
                self.state = Application.State.IDLE
                self.get_settings()
            elif payload['status'] == 'unregistered':
                logger.info('Failed to register, retrying...')
            else:
                logger.info(f'Unknown status: {payload["status"]}')

    def idle(self):
        response = requests.get(self.construct_request_url('/api/rpi/fetch', {'id': self.config['device']['id']}))

        if response.status_code != 200:
            logger.error(f'[api/rpi/fetch]: {response.status_code}')
            logger.debug(f'                 {response.text}')
            return

        payload = json.loads(response.text)

        if 'command' in payload:
            if payload['command'] == 'idle':
                ...
            elif payload['command'] == 'get_reading':
                self.state = Application.State.CAPTURING
            elif payload['command'] == 'register':
                logger.warning('Unregistered')
                self.state = Application.State.UNREGISTERED
            elif payload['command'] == 'set_settings':
                logger.info('Receiving settings')
                self.fetch_delay = int(payload['timeout'])
                logger.info(f'New fetch_delay: {self.fetch_delay}s')
            elif payload['command'] == 'resend_last':
                logger.info('Resend last reading')
                self.send_reading(self.last_reading)
            else:
                logger.error(f'Unknown command: {payload["command"]}')

    def capture(self):
        logger.info('Start capturing')

        reading = self.get_reading()
        self.send_reading(reading)

        self.state = Application.State.IDLE

    def run(self):
        while True:
            try:
                if self.state == Application.State.IDLE:
                    self.idle()
                elif self.state == Application.State.UNREGISTERED:
                    self.register()
                elif self.state == Application.State.CAPTURING:
                    self.capture()
                else:
                    self.state = self.state == Application.State.UNREGISTERED
            except Exception as e:
                logger.error(f'Exception: {e}')
                print(traceback.format_exc())
            except KeyboardInterrupt:
                logger.info('Stop')
                return

            sleep(self.fetch_delay)

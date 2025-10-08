#!/usr/bin/env python3
from dataclasses import dataclass
from picamera2 import Picamera2
from datetime import datetime
import time


class Camera:
    @dataclass
    class Result:
        filename: str = ''
        timestamp: str = ''

    def __init__(self):
        self.camera = Picamera2()
        camera_config = self.camera.create_preview_configuration()

        self.camera.configure(camera_config)

        self.camera.start()

    def capture(self) -> Result:
        time.sleep(1)
        timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
        filename = f'captures/capture_{timestamp}.jpg'
        self.camera.capture_file(filename)
        return Camera.Result(filename, timestamp)


if __name__ == '__main__':
    camera = Camera()
    file, date = camera.capture()
    print(f'Capture: {file}')

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
from pydantic import BaseModel
from sqlalchemy import select
from database import open_db_session
from models import *
from log import logger

router = APIRouter()


class ReadingModel(BaseModel):
    reading: str
    time: str


def get_settings_response(device: Device) -> dict:
    return {
        'command': 'set_settings',
        'timeout': device.fetch_timeout_sec
    }


@router.get('/fetch')
def rpi_fetch(request: Request):
    if 'id' not in request.query_params:
        return JSONResponse({'status': 'error', 'message': 'Expected id in url params'}, 400)

    with open_db_session() as session:
        stmt = select(Device).where(Device.id == int(request.query_params['id'])).limit(1)
        device = session.scalars(stmt).one_or_none()

        if not device:
            return {'command': 'register'}

        device.last_online_time = datetime.now()
        session.add(device)
        session.commit()

        if device.capture_request:
            device.capture_request = False
            session.add(device)
            session.commit()
            return {'command': 'get_reading'}

        if device.set_settings:
            device.set_settings = False
            session.add(device)
            session.commit()
            return get_settings_response(device)

    return {'command': 'idle'}


@router.get('/get_settings')
def rpi_get_settings(request: Request):
    if 'id' not in request.query_params:
        return JSONResponse({'status': 'error', 'message': 'Expected id in url params'}, 400)

    with open_db_session() as session:
        stmt = select(Device).where(Device.id == int(request.query_params['id'])).limit(1)
        device = session.scalars(stmt).one_or_none()

        if not device:
            return {'command': 'register'}

        return get_settings_response(device)


@router.get('/register')
def rpi_register(request: Request):
    if 'id' not in request.query_params:
        return JSONResponse({'status': 'error', 'message': 'Expected id in url params'}, 400)

    with open_db_session() as session:
        stmt = select(Device).where(Device.id == int(request.query_params['id'])).limit(1)
        device = session.scalars(stmt).one_or_none()

        if device:
            return {'status': 'registered'}

    return {'status': 'unregistered'}


@router.post('/send_reading')
def rpi_send_reading(request: Request, payload: ReadingModel):
    if 'id' not in request.query_params:
        return JSONResponse({'status': 'error', 'message': 'Expected id in url params'}, 400)

    logger.info(f'Reading: {payload}')

    with open_db_session() as session:
        reading = Reading(
            device_id=int(request.query_params['id']),
            reading=payload.reading,
            time=payload.time,
        )

        print(f'{reading.device_id} {reading.reading} {reading.time}')
        session.add(reading)
        session.commit()

    return {'status': 'ok'}


@router.post('/send_image')
def rpi_send_image(request: Request):
    logger.info('TODO: Image')
    return {'status': 'ok'}

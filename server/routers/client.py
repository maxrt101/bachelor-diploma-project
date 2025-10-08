from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
from database import open_db_session
from sqlalchemy import select
from models import *

router = APIRouter()


@router.get('/get_readings')
def client_get_reading(request: Request):
    with open_db_session() as session:
        stmt = select(Reading)
        for attr, value in request.query_params.items():
            stmt = stmt.filter(getattr(Reading, attr).like("%%%s%%" % value))
        return {'readings': session.scalars(stmt).all()}


@router.get('/add_device')
def client_add_device(request: Request):
    if 'id' not in request.query_params or 'name' not in request.query_params:
        return JSONResponse({'status': 'error', 'message': 'Expected id and name'}, 400)

    with open_db_session() as session:
        device = Device(
            id=int(request.query_params['id']),
            name=request.query_params['name'],
            scenario=''
        )

        session.add(device)
        session.commit()

    return {'status': 'ok'}


@router.get('/get_device')
def client_get_device(request: Request):
    if 'id' not in request.query_params:
        return JSONResponse({'status': 'error', 'message': 'Expected id in url params'}, 400)

    with open_db_session() as session:
        stmt = select(Device).where(Device.id == int(request.query_params['id']))
        device = session.scalars(stmt).one_or_none()

    return device if device else JSONResponse({'status': 'error', 'message': 'no such device'}, 404)


@router.get('/del_device')
def client_del_device(request: Request):
    if 'id' not in request.query_params:
        return JSONResponse({'status': 'error', 'message': 'Expected id in url params'}, 400)

    with open_db_session() as session:
        stmt = select(Device).where(Device.id == int(request.query_params['id']))
        device = session.scalars(stmt).one_or_none()

        if device:
            session.delete(device)
            session.commit()

    return {'status': 'ok'} if device else JSONResponse({'status': 'error', 'message': 'no such device'}, 404)


@router.get('/get_devices')
def client_get_devices(request: Request):
    with open_db_session() as session:
        stmt = select(Device)
        return session.scalars(stmt).all()


@router.get('/request_reading')
def client_request_reading(request: Request):
    if 'id' not in request.query_params:
        return JSONResponse({'status': 'error', 'message': 'Expected id in url params'}, 400)

    with open_db_session() as session:
        stmt = select(Device).where(Device.id == int(request.query_params['id']))
        device = session.scalars(stmt).one_or_none()

        if device:
            device.capture_request = True
            session.add(device)
            session.commit()

            return {'status': 'ok'}

    return JSONResponse({'status': 'error', 'message': 'no such device'}, 404)


@router.get('/set_fetch_timeout')
def client_set_fetch_timeout(request: Request):
    if 'id' not in request.query_params or 'value' not in request.query_params:
        return JSONResponse({'status': 'error', 'message': 'Expected id in url params'}, 400)

    with open_db_session() as session:
        stmt = select(Device).where(Device.id == int(request.query_params['id']))
        device = session.scalars(stmt).one_or_none()

        if device:
            device.fetch_timeout_sec = int(request.query_params['value'])
            device.set_settings = True
            session.add(device)
            session.commit()

            return {'status': 'ok'}

    return JSONResponse({'status': 'error', 'message': 'no such device'}, 404)


@router.get('/set_online_timeout')
def client_set_online_timeout(request: Request):
    if 'id' not in request.query_params or 'value' not in request.query_params:
        return JSONResponse({'status': 'error', 'message': 'Expected id in url params'}, 400)

    with open_db_session() as session:
        stmt = select(Device).where(Device.id == int(request.query_params['id']))
        device = session.scalars(stmt).one_or_none()

        if device:
            device.online_timeout_sec = int(request.query_params['value'])
            device.set_settings = True
            session.add(device)
            session.commit()

            return {'status': 'ok'}

    return JSONResponse({'status': 'error', 'message': 'no such device'}, 404)
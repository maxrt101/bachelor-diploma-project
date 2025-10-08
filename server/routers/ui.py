from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import APIRouter, Request
from database import open_db_session
from models import *

router = APIRouter()


@router.get('/home', response_class=HTMLResponse, name='ui_home')
def ui_home(request: Request) -> Jinja2Templates.TemplateResponse:
    with open_db_session() as session:
        stmt = select(Device)

        return request.app.templates.TemplateResponse(
            request=request, name='home.html', context={
                'devices': session.scalars(stmt).all(), 'prod': request.app.prod
            }
        )


@router.get('/device/{device_id}', response_class=HTMLResponse, name='ui_device')
def ui_device(request: Request, device_id: int) -> Jinja2Templates.TemplateResponse:
    with open_db_session() as session:
        device_stmt = select(Device).where(Device.id == device_id)
        device = session.scalars(device_stmt).one_or_none()

        readings_stmt = select(Reading).where(Reading.device_id == device_id)
        readings = sorted(session.scalars(readings_stmt).all(), key=lambda r: r.time)

        if device:
            return request.app.templates.TemplateResponse(
                request=request, name='device.html', context={
                    'device': device, 'readings': readings, 'prod': request.app.prod
                }
            )

        return request.app.templates.TemplateResponse(
            request=request, name='device_not_found.html', context={
                'device_id': device_id, 'prod': request.app.prod
            }
        )


@router.get('/add_device', response_class=HTMLResponse, name='ui_add_device')
def ui_add_device(request: Request) -> Jinja2Templates.TemplateResponse:
    return request.app.templates.TemplateResponse(
        request=request, name='add_device.html', context={
            'prod': request.app.prod
        }
    )


from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from database import engine
from log import logger
import routers.client as client
import routers.rpi as rpi
import routers.ui as ui
import uvicorn
import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.templates = Jinja2Templates(directory="templates")
    models.Base.metadata.create_all(bind=engine)
    app.prod = True
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(client.router, prefix='/api/client')
app.include_router(rpi.router, prefix='/api/rpi')
app.include_router(ui.router, prefix='/ui')


@app.exception_handler(Exception)
def server_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f'Failed {request.method} at {request.url} with message: {exc!r}')
    return JSONResponse(
        status_code=500,
        content={
            'status': 'error',
            'message': f'{exc!r}',
            'context': f'{request.method} {request.url}'
        }
    )


@app.get('/api/set_server_options')
def api_set_server_options(request: Request):
    if 'prod' in request.query_params:
        request.app.prod = request.query_params['prod'] == 'true'

    return {'message': 'ok'}


@app.get("/")
def root():
    return RedirectResponse(app.url_path_for('ui_home'))


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
        reload_dirs='./',
        use_colors=True,
        root_path='./',
        app_dir='./'
    )

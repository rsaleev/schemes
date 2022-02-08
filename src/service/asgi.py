from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from src.config.service import Settings

from src.service.routes.schemes import router as r_schemes
from src.service.routes.validation import router as r_validation

settings = Settings()

app = FastAPI(docs_url=None, redoc_url=None, debug=settings.fastapi_app_debug)

app.title = settings.fastapi_app_title
app.version = settings.fastapi_app_version
app.contact = settings.fastapi_app_author
app.description = settings.fastapi_app_title


app.state.static_folder = "./src/service/static"
app.state.temp_folder = "./src/service/temp"


app.mount("/static", StaticFiles(directory=app.state.static_folder), name='static')
app.mount("/tmp",StaticFiles(directory=app.state.temp_folder), name='temp')


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

app.include_router(r_schemes)
app.include_router(r_validation)


@app.get("/health", include_in_schema=False)
async def get_status():
   return 1

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="static/swagger-ui-bundle.js",
        swagger_css_url="static/swagger-ui.css",
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


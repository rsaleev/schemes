from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from .routes import schemes


app = Starlette()

app.add_route('/schemes', schemes.get_schemes)
app.add_route('/scheme/{name}', schemes.get_schema)
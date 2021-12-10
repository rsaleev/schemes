from fastapi import FastAPI
from .routes import schemes, validation

app = FastAPI(debug=True)

app.include_router(schemes.router)
app.include_router(validation.router)



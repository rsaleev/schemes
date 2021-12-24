import os

from pathlib import Path


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .routes import schemes, validation



app = FastAPI(debug=bool(os.environ['FASTAPI_DEBUG']), docs_url='/documentation', version='0.1.1')

app.include_router(schemes.router)
app.include_router(validation.router)


# origins = [
#     "http://localhost.tiangolo.com",
#     "https://localhost.tiangolo.com",
#     "http://localhost",
#     "http://localhost:8080",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=False,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
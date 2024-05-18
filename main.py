from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from routers.auth import auth
from routers.users import users
from routers.data_transfer import data_transfer


app = FastAPI(
    title="Speax",
    description="Speax API",
    version="1.0",
    docs_url="/"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(data_transfer.router)

add_pagination(app)

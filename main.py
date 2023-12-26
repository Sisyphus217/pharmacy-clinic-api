from fastapi import FastAPI
from app.routers import beneficiary_routers
from app.routers import medication_routers

app = FastAPI()

app.include_router(beneficiary_routers.router)
app.include_router(medication_routers.router)
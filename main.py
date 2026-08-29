from fastapi import FastAPI, Request
from app.routes import router
from app.exceptions import AppException
from fastapi.responses import JSONResponse


app = FastAPI()

@app.exception_handler(AppException)
async def app_exeption_handler(request: Request, exc: AppException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app.include_router(router)
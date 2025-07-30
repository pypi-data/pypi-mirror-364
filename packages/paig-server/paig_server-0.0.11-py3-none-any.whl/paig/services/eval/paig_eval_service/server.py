import traceback
from http import HTTPStatus
from core.logging_init import set_logging
set_logging()
from typing import List
from fastapi import FastAPI, Request, status
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from core.middlewares.sqlalchemy_middleware import SQLAlchemyMiddleware
from core.exceptions import CustomException
from fastapi.responses import JSONResponse
from core import config
import logging
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def init_routers(app_: FastAPI) -> None:
    from routers import evaluation_router_paths
    app_.include_router(evaluation_router_paths, prefix="/eval-service", tags=["Evaluation"])


def init_listeners(app_: FastAPI) -> None:
    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        content = {"error_code": exc.error_code, "success": False, "message": exc.message}
        if exc.error_code == HTTPStatus.INTERNAL_SERVER_ERROR or exc.error_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            logger.error(f"Exception occurred({exc.error_code.name}): {exc}")
        return JSONResponse(
            status_code=exc.code,
            content=content
        )

    @app_.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        message = "Request validation failed"
        try:
            err = exc.errors()[0]
            message = f"{err['loc'][-1]}: {err['msg']}"
        except:
            pass
        return JSONResponse(content=jsonable_encoder({
            "error_code": 400,
            "success": False,
            "message": message
        }), status_code=status.HTTP_400_BAD_REQUEST)

    @app_.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        tb_str = traceback.format_exc()
        # Log the exception with the traceback
        logging.error(f"Unhandled exception occurred: {exc}\n{tb_str}")
        return JSONResponse(
            status_code=500,
            content={"error_code": 500, "success": False,
                     "message": "An unexpected error occurred. Please try again later."}
        )

    @app_.exception_handler(StarletteHTTPException)
    async def path_not_found_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return JSONResponse(content=jsonable_encoder({
                    "error_code": 404,
                    "success": False,
                    "message": "Path Not Found",
                    "path": request.url.path
                }), status_code=status.HTTP_404_NOT_FOUND)


def init_cache() -> None:
    pass


def init_settings() -> None:
    cnf = config.load_config_file()
    config.Config = cnf


def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(SQLAlchemyMiddleware)
    ]
    return middleware


def create_app() -> FastAPI:
    init_settings()
    app_ = FastAPI(
        title="Paig Eval Service",
        description="Paig Eval Service Application",
        version="1.0.0",
        docs_url="/docs",
        redoc_url=None,
        middleware=make_middleware()
    )

    init_routers(app_=app_)
    init_listeners(app_=app_)
    init_cache()
    print("Server is started")
    # Add startup events
    return app_


app = create_app()

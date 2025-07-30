from typing import List
from fastapi import APIRouter, Request, Response, Depends, Query
from core.controllers.paginated_response import Pageable
from core.utils import SingletonDepends
from ..controllers.eval_config_controller import EvaluationConfigController
from ..api_schemas.eval_config_schema import ConfigCreateRequest, ConfigUpdateRequest, IncludeQueryParams, QueryParamsBase, include_query_params, exclude_query_params
from core.middlewares.request_session_context_middleware import get_user

evaluation_config_router = APIRouter()

eval_config_controller_instance = Depends(SingletonDepends(EvaluationConfigController, called_inside_fastapi_depends=True))


@evaluation_config_router.get("", response_model=Pageable)
async def get_eval_config(
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        excludeQuery: QueryParamsBase = Depends(exclude_query_params),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        eval_config_controller: EvaluationConfigController = eval_config_controller_instance
)-> Pageable:
    return await eval_config_controller.get_all_eval_config(includeQuery, excludeQuery, page, size, sort)


@evaluation_config_router.post("")
async def save_eval_config(
        request: Request,
        response: Response,
        body_params: ConfigCreateRequest,
        eval_config_controller: EvaluationConfigController = eval_config_controller_instance
):
    body_params = body_params.model_dump()
    user: dict = get_user()
    body_params['owner'] = user['username']
    return await eval_config_controller.create_eval_config(body_params=body_params)


@evaluation_config_router.put("/{config_id}")
async def update_eval_target(
        request: Request,
        response: Response,
        config_id: int,
        body_params: ConfigUpdateRequest,
        eval_config_controller: EvaluationConfigController = eval_config_controller_instance
):
    return await eval_config_controller.update_eval_config(config_id = config_id, body_params=body_params.model_dump())

@evaluation_config_router.delete("/{config_id}")
async def delete_eval_target(
        request: Request,
        response: Response,
        config_id: int,
        eval_config_controller: EvaluationConfigController = eval_config_controller_instance
):
    return await eval_config_controller.delete_eval_config(config_id=config_id)

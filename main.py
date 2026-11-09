
from datetime import date
from pathlib import Path
import os
import time

import pandas as pd
from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    HTTPException,
    Header,
    Query,
    Depends,
    Request
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from task_service import (
    TaskIn,
    TaskOut,
    TaskNotFoundError,
    get_all_tasks,
    get_task,
    create_task,
    update_task,
    delete_task
)

from ai_service import ask_ai

from analysis_service import (
    get_user_statistics,
    get_performance_summary,
    get_low_performers,
    get_completion_pivot
)

load_dotenv()

API_KEY = os.getenv("APP_API_KEY")

app = FastAPI(title="Task Management API")


# CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# MIDDLEWARE

@app.middleware("http")
async def add_process_time(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time

    response.headers["X-Process-Time"] = str(process_time)

    print(
        f"{request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time:.4f}s"
    )

    return response


# DEPENDENCIES

def verify_api_key(
    key: str = Header(..., alias="X-API-Key")
):
    if not API_KEY or key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )


def get_pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    return {
        "page": page,
        "page_size": page_size
    }


# EXCEPTION HANDLERS

@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(
    request: Request,
    error: TaskNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={"detail": str(error)}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    error: RequestValidationError
):
    errors = error.errors()

    for item in errors:
        if "title" in str(item.get("loc", [])):
            return JSONResponse(
                status_code=400,
                content={"detail": "Title cannot be empty"}
            )

    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request data"}
    )


# HOME

@app.get("/")
def home():
    return {
        "message": "Python Final Project is running!"
    }


# TASK CRUD

@app.get("/tasks", response_model=list[TaskOut])
def read_tasks():
    return get_all_tasks()


@app.get("/tasks/overdue")
def get_overdue_tasks(
    _: None = Depends(verify_api_key)
):
    tasks = get_all_tasks()
    today = date.today()
    overdue = []

    for task in tasks:
        due_date = pd.to_datetime(
            task["due_date"],
            errors="coerce"
        )

        if (
            not task.get("done", False)
            and pd.notna(due_date)
            and due_date.date() < today
        ):
            task_copy = task.copy()
            task_copy["days_late"] = (
                today - due_date.date()
            ).days
            overdue.append(task_copy)

    return overdue


@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id: int):
    return get_task(task_id)


@app.post(
    "/tasks",
    response_model=TaskOut,
    status_code=201
)
def add_task(
    task: TaskIn,
    _: None = Depends(verify_api_key)
):
    return create_task(task)


@app.put("/tasks/{task_id}", response_model=TaskOut)
def edit_task(
    task_id: int,
    task: TaskIn,
    _: None = Depends(verify_api_key)
):
    return update_task(task_id, task)


@app.delete("/tasks/{task_id}")
def remove_task(
    task_id: int,
    _: None = Depends(verify_api_key)
):
    delete_task(task_id)

    return {
        "message": "Task deleted successfully"
    }


# STATISTICS

@app.get("/stats/users")
def stats_users(
    pagination: dict = Depends(get_pagination),
    sort_by: str = Query("completion_percentage"),
    order: str = Query("desc"),
    _: None = Depends(verify_api_key)
):
    statistics = get_user_statistics()

    if statistics is None:
        raise HTTPException(
            status_code=503,
            detail="Data source is unavailable"
        )

    page = pagination["page"]
    page_size = pagination["page_size"]

    if sort_by not in statistics.columns:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort_by field"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Order must be asc or desc"
        )

    statistics = statistics.sort_values(
        by=sort_by,
        ascending=(order == "asc")
    )

    total = len(statistics)
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": jsonable_encoder(
            statistics.iloc[start:end].to_dict(
                orient="records"
            )
        )
    }


@app.get("/stats/summary")
def stats_summary(
    _: None = Depends(verify_api_key)
):
    result = get_performance_summary()

    if result is None:
        raise HTTPException(
            status_code=503,
            detail="Data source is unavailable"
        )

    return result


@app.get("/stats/low-performers")
def stats_low_performers(
    _: None = Depends(verify_api_key)
):
    result = get_low_performers()

    if result is None:
        raise HTTPException(
            status_code=503,
            detail="Data source is unavailable"
        )

    return jsonable_encoder(
        result.to_dict(orient="records")
    )


@app.get("/stats/cities")
def stats_cities(
    _: None = Depends(verify_api_key)
):
    result = get_completion_pivot()

    if result is None:
        raise HTTPException(
            status_code=503,
            detail="Data source is unavailable"
        )

    return jsonable_encoder(
        result.to_dict(orient="records")
    )


# AI CHAT

class AIQuestion(BaseModel):
    prompt: str
    conversation_id: str


@app.post("/ai/ask")
def chat_with_ai(
    data: AIQuestion,
    _: None = Depends(verify_api_key)
):
    prompt = data.prompt.strip()
    conversation_id = data.conversation_id.strip()

    if not prompt:
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty"
        )

    if len(prompt) > 500:
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot exceed 500 characters"
        )

    if not conversation_id:
        raise HTTPException(
            status_code=400,
            detail="Conversation ID cannot be empty"
        )

    answer = ask_ai(
        prompt,
        conversation_id
    )

    return {
        "conversation_id": conversation_id,
        "answer": answer
    }


# AI LOG STATISTICS

@app.get("/ai/logs/stats")
def ai_logs_stats(
    _: None = Depends(verify_api_key)
):
    log_file = Path("ai_logs.csv")

    if not log_file.exists():
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "mock_requests": 0,
            "average_prompt_length": 0,
            "average_response_length": 0,
            "total_conversations": 0
        }

    try:
        logs = pd.read_csv(log_file)

        required_columns = [
            "conversation_id",
            "timestamp",
            "prompt_length",
            "response_length",
            "status"
        ]

        if not all(
            column in logs.columns
            for column in required_columns
        ):
            raise HTTPException(
                status_code=500,
                detail="AI log file has an invalid format"
            )

        logs["prompt_length"] = pd.to_numeric(
            logs["prompt_length"],
            errors="coerce"
        )

        logs["response_length"] = pd.to_numeric(
            logs["response_length"],
            errors="coerce"
        )

        return {
            "total_requests": int(len(logs)),

            "successful_requests": int(
                (logs["status"] == "success").sum()
            ),

            "failed_requests": int(
                (logs["status"] == "error").sum()
            ),

            "mock_requests": int(
                (logs["status"] == "mock").sum()
            ),

            "average_prompt_length": round(
                logs["prompt_length"].mean(), 2
            ) if logs["prompt_length"].notna().any() else 0,

            "average_response_length": round(
                logs["response_length"].mean(), 2
            ) if logs["response_length"].notna().any() else 0,

            "total_conversations": int(
                logs["conversation_id"].nunique()
            )
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not read AI logs"
        )

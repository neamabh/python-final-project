
import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


TASKS_FILE = Path("tasks.json")


class TaskIn(BaseModel):
    title: Optional[str] = None
    user_id: int
    due_date: str
    priority: int = Field(ge=1, le=3)
    done: bool = False
    notes: Optional[str] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value):
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Title cannot be empty")
        return value


class TaskOut(BaseModel):
    id: int
    title: Optional[str]
    user_id: int
    due_date: str
    priority: int
    done: bool


class TaskNotFoundError(Exception):
    pass


def load_tasks():
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, ensure_ascii=False, indent=4)


def get_all_tasks():
    return load_tasks()


def get_task(task_id: int):
    tasks = load_tasks()

    for task in tasks:
        if task["id"] == task_id:
            return task

    raise TaskNotFoundError(f"Task {task_id} was not found")


def create_task(task_data: TaskIn):
    tasks = load_tasks()

    new_id = max(
        (task["id"] for task in tasks),
        default=0
    ) + 1

    new_task = {
        "id": new_id,
        **task_data.model_dump()
    }

    tasks.append(new_task)
    save_tasks(tasks)

    return new_task


def update_task(task_id: int, task_data: TaskIn):
    tasks = load_tasks()

    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            updated_task = {
                "id": task_id,
                **task_data.model_dump()
            }

            tasks[index] = updated_task
            save_tasks(tasks)

            return updated_task

    raise TaskNotFoundError(f"Task {task_id} was not found")


def delete_task(task_id: int):
    tasks = load_tasks()

    for index, task in enumerate(tasks):
        if task["id"] == task_id:
            deleted_task = tasks.pop(index)
            save_tasks(tasks)
            return deleted_task

    raise TaskNotFoundError(f"Task {task_id} was not found")

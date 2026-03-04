"""
Розв'язки — FastAPI (Middle)
Запуск: uvicorn solution:app --reload
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator

app = FastAPI(title="TODO API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────── DB Stub ───────────────────────────────────────────────────────
_todos: dict[str, dict] = {}
_users: dict[str, dict] = {
    "user1": {"id": "user1", "role": "admin", "token": "admin-token"},
    "user2": {"id": "user2", "role": "user",  "token": "user-token"},
}

# ─────────────── Schemas ──────────────────────────────────────────────────────
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    priority: int = Field(1, ge=1, le=5)

class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    done: bool | None = None
    priority: int | None = Field(None, ge=1, le=5)

class TodoResponse(BaseModel):
    id: str
    title: str
    description: str
    done: bool
    priority: int
    created_at: str

class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError("Лише літери, цифри та _")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль повинен містити хоча б одну цифру")
        return v

    def model_post_init(self, __context) -> None:
        if self.password != self.password_confirm:
            raise ValueError("Паролі не збігаються")

# ─────────────── Auth Dependency ─────────────────────────────────────────────
def get_token(authorization: str | None = Query(None)) -> str:
    if authorization is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Не авторизовано")
    return authorization

def get_current_user(token: str = Depends(get_token)) -> dict:
    for user in _users.values():
        if user["token"] == token:
            return user
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Невірний токен")

def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Потрібна роль admin")
    return user

# ─────────────── Routes ───────────────────────────────────────────────────────
@app.get("/todos", response_model=list[TodoResponse])
def list_todos(
    done: bool | None = Query(None),
    priority: int | None = Query(None, ge=1, le=5),
    _user: dict = Depends(get_current_user),
):
    items = list(_todos.values())
    if done is not None:
        items = [t for t in items if t["done"] == done]
    if priority is not None:
        items = [t for t in items if t["priority"] == priority]
    return items

@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(body: TodoCreate, user: dict = Depends(get_current_user)):
    todo_id = str(uuid.uuid4())
    todo = {
        "id": todo_id,
        "title": body.title,
        "description": body.description,
        "done": False,
        "priority": body.priority,
        "owner_id": user["id"],
        "created_at": datetime.utcnow().isoformat(),
    }
    _todos[todo_id] = todo
    return todo

@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, body: TodoUpdate, user: dict = Depends(get_current_user)):
    todo = _todos.get(todo_id)
    if not todo:
        raise HTTPException(404, f"TODO #{todo_id} не знайдено")
    if todo["owner_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(403, "Недостатньо прав")
    updates = body.model_dump(exclude_none=True)
    todo.update(updates)
    return todo

@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: str, user: dict = Depends(get_current_user)):
    todo = _todos.get(todo_id)
    if not todo:
        raise HTTPException(404, "Не знайдено")
    if todo["owner_id"] != user["id"] and user["role"] != "admin":
        raise HTTPException(403, "Недостатньо прав")
    del _todos[todo_id]

@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: UserRegistration, _admin: dict = Depends(require_admin)):
    return {"message": f"Користувач {body.username} зареєстрований"}

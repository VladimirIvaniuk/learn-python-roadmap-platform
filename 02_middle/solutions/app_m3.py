"""
Рішення — Урок 3 (FastAPI)

Запуск: uvicorn solutions.app_m3:app --reload
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    name: str
    email: str
    age: int | None = None


users_db: dict[int, User] = {}
next_id = 1


@app.post("/users")
def create_user(user: User) -> User:
    global next_id
    users_db[next_id] = user
    next_id += 1
    return user


@app.get("/users/{user_id}")
def get_user(user_id: int) -> User:
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

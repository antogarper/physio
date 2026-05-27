from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import asyncpg
from db import get_db
from security import hash_password, verify_password, create_token

router = APIRouter()

class RegisterInput(BaseModel):
    clinic_name: str
    name:        str
    email:       str
    password:    str

@router.post("/register")
async def register(data: RegisterInput, db: asyncpg.Connection = Depends(get_db)):
    # Check if email already exists
    existing = await db.fetchrow("SELECT id FROM users WHERE email = $1", data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create clinic
    clinic = await db.fetchrow(
        "INSERT INTO clinics (name) VALUES ($1) RETURNING id",
        data.clinic_name
    )

    # Create admin user
    hashed = hash_password(data.password)
    user = await db.fetchrow(
        """INSERT INTO users (clinic_id, name, email, password, role)
           VALUES ($1, $2, $3, $4, 'admin')
           RETURNING id, name, email, role, clinic_id""",
        clinic["id"], data.name, data.email, hashed
    )

    token = create_token({
        "sub":       str(user["id"]),
        "clinic_id": str(user["clinic_id"]),
        "role":      user["role"]
    })

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":        str(user["id"]),
            "name":      user["name"],
            "email":     user["email"],
            "role":      user["role"],
            "clinic_id": str(user["clinic_id"])
        }
    }

@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db:   asyncpg.Connection        = Depends(get_db)
):
    user = await db.fetchrow("SELECT * FROM users WHERE email = $1", form.username)
    if not user or not verify_password(form.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token({
        "sub":       str(user["id"]),
        "clinic_id": str(user["clinic_id"]),
        "role":      user["role"]
    })

    return {
        "access_token": token,
        "token_type":   "bearer",
        "user": {
            "id":        str(user["id"]),
            "name":      user["name"],
            "email":     user["email"],
            "role":      user["role"],
            "clinic_id": str(user["clinic_id"])
        }
    }

@router.get("/me")
async def me(
    db:   asyncpg.Connection = Depends(get_db),
    user: dict               = Depends(get_current_user)
):
    row = await db.fetchrow(
        "SELECT id, name, email, role, clinic_id FROM users WHERE id = $1",
        user["sub"]
    )
    return dict(row)

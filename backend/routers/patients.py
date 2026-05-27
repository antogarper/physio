from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date
import asyncpg
from db import get_db
from security import get_current_user

router = APIRouter()

class PatientInput(BaseModel):
    name:       str
    birth_date: Optional[date] = None
    gender:     Optional[str]  = None
    email:      Optional[str]  = None
    phone:      Optional[str]  = None
    occupation: Optional[str]  = None
    notes:      Optional[str]  = None

@router.get("/")
async def list_patients(
    db:   asyncpg.Connection = Depends(get_db),
    user: dict               = Depends(get_current_user)
):
    rows = await db.fetch(
        """SELECT * FROM patients
           WHERE clinic_id = $1 AND active = TRUE
           ORDER BY name""",
        user["clinic_id"]
    )
    return [dict(r) for r in rows]

@router.post("/")
async def create_patient(
    data: PatientInput,
    db:   asyncpg.Connection = Depends(get_db),
    user: dict               = Depends(get_current_user)
):
    row = await db.fetchrow(
        """INSERT INTO patients
           (clinic_id, name, birth_date, gender, email, phone, occupation, notes)
           VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
           RETURNING *""",
        user["clinic_id"], data.name, data.birth_date, data.gender,
        data.email, data.phone, data.occupation, data.notes
    )
    return dict(row)

@router.get("/{patient_id}")
async def get_patient(
    patient_id: str,
    db:   asyncpg.Connection = Depends(get_db),
    user: dict               = Depends(get_current_user)
):
    row = await db.fetchrow(
        "SELECT * FROM patients WHERE id = $1 AND clinic_id = $2",
        patient_id, user["clinic_id"]
    )
    if not row:
        raise HTTPException(status_code=404, detail="Patient not found")
    return dict(row)

@router.put("/{patient_id}")
async def update_patient(
    patient_id: str,
    data: PatientInput,
    db:   asyncpg.Connection = Depends(get_db),
    user: dict               = Depends(get_current_user)
):
    row = await db.fetchrow(
        """UPDATE patients
           SET name=$1, birth_date=$2, gender=$3, email=$4,
               phone=$5, occupation=$6, notes=$7
           WHERE id=$8 AND clinic_id=$9
           RETURNING *""",
        data.name, data.birth_date, data.gender, data.email,
        data.phone, data.occupation, data.notes,
        patient_id, user["clinic_id"]
    )
    if not row:
        raise HTTPException(status_code=404, detail="Patient not found")
    return dict(row)

@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: str,
    db:   asyncpg.Connection = Depends(get_db),
    user: dict               = Depends(get_current_user)
):
    await db.execute(
        "UPDATE patients SET active = FALSE WHERE id = $1 AND clinic_id = $2",
        patient_id, user["clinic_id"]
    )
    return {"message": "Patient deleted"}

@router.get("/{patient_id}/assessments")
async def get_patient_assessments(
    patient_id: str,
    db:   asyncpg.Connection = Depends(get_db),
    user: dict               = Depends(get_current_user)
):
    rows = await db.fetch(
        """SELECT id, primary_diagnosis, confidence, body_area,
                  main_complaint, language, created_at
           FROM assessments
           WHERE patient_id = $1
           ORDER BY created_at DESC""",
        patient_id
    )
    return [dict(r) for r in rows]

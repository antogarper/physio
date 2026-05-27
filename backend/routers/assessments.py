from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncpg
import requests
import json
import os
from db import get_db
from security import get_current_user

router = APIRouter()

class AssessmentInput(BaseModel):
    patient_id:         str
    appointment_id:     Optional[str]   = None
    age:                int
    gender:             str
    weight:             float
    height:             float
    occupation:         Optional[str]   = None
    physical_activity:  Optional[str]   = None
    main_complaint:     str
    body_area:          str
    problem_duration:   Optional[str]   = None
    problem_onset:      Optional[str]   = None
    has_pain:           bool            = True
    pain_intensity:     int             = 0
    aggravating:        Optional[str]   = None
    relieving:          Optional[str]   = None
    previous_history:   Optional[str]   = None
    current_treatments: Optional[str]   = None
    additional_info:    Optional[str]   = None
    language:           str             = "English"

def call_ai(data: AssessmentInput) -> dict:
    prompt = f"""You are an expert physiotherapist assistant. Analyze the following patient data and return ONLY a valid JSON object, no extra text, no markdown, no backticks.

PATIENT PROFILE:
- Age: {data.age} | Gender: {data.gender}
- Weight: {data.weight} kg | Height: {data.height} cm
- Occupation: {data.occupation}
- Physical activity: {data.physical_activity}

MAIN COMPLAINT:
- Description: {data.main_complaint}
- Body area affected: {data.body_area}
- Duration: {data.problem_duration}
- Onset: {data.problem_onset}

SYMPTOMS:
- Pain present: {"Yes, intensity " + str(data.pain_intensity) + "/10" if data.has_pain else "No"}
- Aggravating factors: {data.aggravating}
- Relieving factors: {data.relieving}

CLINICAL HISTORY:
- Previous injuries / conditions: {data.previous_history}
- Current treatments / medications: {data.current_treatments}
- Additional information: {data.additional_info}

Return this exact JSON structure (all text in {data.language}):
{{
  "primary_diagnosis": "...",
  "diagnosis_reasoning": "2-3 sentences explaining why",
  "confidence": "High / Medium / Low",
  "differential_diagnoses": [
    {{"name": "...", "reason": "..."}},
    {{"name": "...", "reason": "..."}},
    {{"name": "...", "reason": "..."}}
  ],
  "red_flags": ["..."],
  "treatment": {{
    "acute":      {{"phase": "Acute Phase (Week 1-2)",    "goals": "...", "interventions": ["...","...","..."]}},
    "recovery":   {{"phase": "Recovery Phase (Week 3-6)", "goals": "...", "interventions": ["...","...","..."]}},
    "functional": {{"phase": "Functional Phase (Week 7+)","goals": "...", "interventions": ["...","...","..."]}}
  }},
  "home_exercises": [
    {{"name": "...", "description": "...", "frequency": "..."}},
    {{"name": "...", "description": "...", "frequency": "..."}},
    {{"name": "...", "description": "...", "frequency": "..."}},
    {{"name": "...", "description": "...", "frequency": "..."}}
  ],
  "referral": {{"needed": "Yes / No", "reason": "..."}},
  "follow_up": "..."
}}"""

    response = requests.post(
        url="https://dbc-c0c5e61a-9d9c.cloud.databricks.com/ai-gateway/mlflow/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['DATABRICKS_TOKEN']}",
            "Content-Type": "application/json"
        },
        json={
            "model": "databricks-gpt-oss-120b",
            "max_tokens": 3000,
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    result  = response.json()
    content = result["choices"][0]["message"]["content"]
    if isinstance(content, list):
        raw = " ".join(b["text"] for b in content if b.get("type") == "text")
    else:
        raw = content

    clean = raw.replace("```json", "").replace("```", "").strip()
    start = clean.find("{")
    end   = clean.rfind("}") + 1
    return json.loads(clean[start:end])

@router.post("/")
async def create_assessment(
    data: AssessmentInput,
    db:   asyncpg.Connection = Depends(get_db),
    user: dict               = Depends(get_current_user)
):
    # Verify patient belongs to this clinic
    patient = await db.fetchrow(
        "SELECT id FROM patients WHERE id = $1 AND clinic_id = $2",
        data.patient_id, user["clinic_id"]
    )
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Call AI
    ai = call_ai(data)

    # Save to database
    row = await db.fetchrow(
        """INSERT INTO assessments (
            patient_id, therapist_id, appointment_id,
            age, gender, weight, height, occupation, physical_activity,
            main_complaint, body_area, problem_duration, problem_onset,
            has_pain, pain_intensity, aggravating, relieving,
            previous_history, current_treatments, additional_info,
            primary_diagnosis, confidence, diagnosis_reasoning,
            red_flags, treatment_plan, home_exercises,
            referral_needed, referral_reason, follow_up, language
        ) VALUES (
            $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,
            $14,$15,$16,$17,$18,$19,$20,$21,$22,$23,
            $24,$25,$26,$27,$28,$29,$30
        ) RETURNING *""",
        data.patient_id, user["sub"], data.appointment_id,
        data.age, data.gender, data.weight, data.height,
        data.occupation, data.physical_activity,
        data.main_complaint, data.body_area,
        data.problem_duration, data.problem_onset,
        data.has_pain, data.pain_intensity,
        data.aggravating, data.relieving,
        data.previous_history, data.current_treatments, data.additional_info,
        ai.get("primary_diagnosis"), ai.get("confidence"),
        ai.get("diagnosis_reasoning"),
        json.dumps(ai.get("red_flags", [])),
        json.dumps(ai.get("treatment", {})),
        json.dumps(ai.get("home_exercises", [])),
        ai.get("referral", {}).get("needed") == "Yes",
        ai.get("referral", {}).get("reason"),
        ai.get("follow_up"), data.language
    )

    return {**dict(row), "ai_result": ai}

@router.get("/{assessment_id}")
async def get_assessment(
    assessment_id: str,
    db:   asyncpg.Connection = Depends(get_db),
    user: dict               = Depends(get_current_user)
):
    row = await db.fetchrow(
        "SELECT * FROM assessments WHERE id = $1",
        assessment_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return dict(row)

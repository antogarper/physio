from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import security, patients, assessments
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PhysioAI CRM")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,        prefix="/auth",        tags=["Auth"])
app.include_router(patients.router,    prefix="/patients",    tags=["Patients"])
app.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])

@app.get("/")
def health():
    return {"status": "PhysioAI CRM running"}

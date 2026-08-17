import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from huggingface_hub.errors import HfHubHTTPError
import uvicorn
from scripts.predict_api import predict
from scripts.chat_api import chat as run_chat


app = FastAPI()

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:5174", "http://127.0.0.1:5174",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    Age: float
    Semester: float
    CGPA: float
    Attendance_Percentage: float
    DSA_Score: float
    Programming_Score: float
    Database_Score: float
    WebDev_Score: float
    ML_Score: float
    Python_Skill: float
    JavaScript_Skill: float
    Project_Complexity: str
    Communication_Score: float
    Presentation_Score: float
    Problem_Solving_Score: float
    Leadership_Score: float
    Teamwork_Score: float
    Aptitude_Test_Score: float
    Projects_Count: float
    Certifications_Count: float
    Hackathons_Participated: float
    Internship_Experience: float
    GitHub_Repo_Count: float
    LinkedIn_Profile_Strength: float
    Volunteer_Activities: float
    Research_Papers: float
    Workshops_Attended: float
    Coding_Contest_Rating: float
    Mock_Interview_Score: float
    English_Proficiency_Score: float
    Technical_Skill_Index: float
    Soft_Skill_Index: float
    Experience_Index: float

@app.post("/predict")
def predict_career(input_data: InputData):
    input_dict = input_data.model_dump()
    result = predict(input_dict)
    return result


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatContext(BaseModel):
    employability_score: float
    recommended_career_path: str
    confidence: float
    career_probabilities: dict[str, float]


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    context: ChatContext


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    try:
        reply = run_chat(
            [m.model_dump() for m in request.messages],
            request.context.model_dump(),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HfHubHTTPError as e:
        raise HTTPException(status_code=502, detail=f"Hugging Face inference error: {e}")
    return {"reply": reply}

app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    candidate = FRONTEND_DIST / full_path
    if candidate.is_file():
        return FileResponse(candidate)
    return FileResponse(FRONTEND_DIST / "index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
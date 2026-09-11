import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import threading
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
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
    role: Literal["user", "assistant"]
    # Assistant replies (max_tokens=512 in chat_api) are resent as history, so this has to
    # fit them; the frontend input separately caps what a user can type at 1000.
    content: str = Field(min_length=1, max_length=3000)


class ChatContext(BaseModel):
    employability_score: float
    recommended_career_path: str = Field(max_length=100)
    confidence: float
    career_probabilities: dict[str, float] = Field(max_length=10)


class ChatRequest(BaseModel):
    # Matches CHAT_HISTORY_LIMIT in frontend/src/lib/api.js
    messages: list[ChatMessage] = Field(min_length=1, max_length=10)
    context: ChatContext


class RateLimiter:
    """At most `limit` hits per key in any `window`-second span. In-memory, so it resets
    on restart and assumes a single worker process (what the Dockerfile runs)."""

    def __init__(self, limit: int, window: float):
        self.limit = limit
        self.window = window
        self._hits: defaultdict[str, deque] = defaultdict(deque)
        self._lock = threading.Lock()  # sync endpoints run in a threadpool

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        with self._lock:
            if len(self._hits) > 10_000:  # drop idle keys so spoofed IPs can't grow this forever
                self._hits = defaultdict(
                    deque, {k: v for k, v in self._hits.items() if v and now - v[-1] < self.window}
                )
            hits = self._hits[key]
            while hits and now - hits[0] >= self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                return False
            hits.append(now)
            return True


# The per-client limit stops one visitor hogging the chat; the global daily cap is what
# actually bounds spend on the HF_TOKEN's free inference credits.
chat_client_limiter = RateLimiter(limit=8, window=60)
chat_daily_limiter = RateLimiter(limit=50, window=24 * 60 * 60)


def _client_key(request: Request) -> str:
    # On Render, request.client is the proxy; the visitor is the first X-Forwarded-For
    # entry. Clients can spoof that header, which is why the global cap exists too.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@app.post("/chat")
def chat_endpoint(request: ChatRequest, http_request: Request):
    if not chat_client_limiter.allow(_client_key(http_request)):
        raise HTTPException(
            status_code=429, detail="Too many messages. Please wait a minute and try again."
        )
    if not chat_daily_limiter.allow("all"):
        raise HTTPException(
            status_code=429,
            detail="The chat assistant has reached its daily limit. Please try again tomorrow.",
        )
    try:
        reply = run_chat(
            [m.model_dump() for m in request.messages],
            request.context.model_dump(),
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except HfHubHTTPError as e:
        if getattr(getattr(e, "response", None), "status_code", None) == 402:
            raise HTTPException(
                status_code=503,
                detail="The chat assistant is out of free credit for this month. "
                "Everything else on the page still works.",
            )
        raise HTTPException(status_code=502, detail=f"Hugging Face inference error: {e}")
    return {"reply": reply}

app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    candidate = (FRONTEND_DIST / full_path).resolve()
    # Only serve files inside dist — "../" segments or a leading "/" would otherwise
    # escape it (e.g. //proc/self/environ would leak HF_TOKEN).
    if candidate.is_file() and candidate.is_relative_to(FRONTEND_DIST):
        return FileResponse(candidate)
    return FileResponse(FRONTEND_DIST / "index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

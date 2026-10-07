"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Practice teamwork and compete in soccer matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": []
    },
    "Basketball Club": {
        "description": "Build shooting and ball-handling skills through drills and games",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 14,
        "participants": []
    },
    "Art Studio": {
        "description": "Explore drawing, painting, and mixed media projects",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": []
    },
    "Drama Club": {
        "description": "Develop acting, stage presence, and performance skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": []
    },
    "Debate Team": {
        "description": "Practice argumentation, speaking, and critical thinking",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": []
    },
    "Science Olympiad": {
        "description": "Solve engineering and science challenges through hands-on projects",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": []
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _get_activity(activity_name: str):
    activity_key = activity_name.strip()
    for name, activity in activities.items():
        if name.lower() == activity_key.lower():
            return name, activity
    return None, None


async def _get_email_from_request(request: Request, email: str | None) -> str:
    if email is not None:
        candidate = email
    else:
        candidate = ""
        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            payload = await request.json()
            candidate = payload.get("email", "")
        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            form = await request.form()
            candidate = form.get("email", "")

    candidate = str(candidate).strip()
    if not candidate or "@" not in candidate:
        raise HTTPException(status_code=400, detail="Valid email is required")

    return candidate


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
async def signup_for_activity(activity_name: str, request: Request, email: str | None = None):
    """Sign up a student for an activity"""
    email = await _get_email_from_request(request, email)
    normalized_email = _normalize_email(email)

    activity_name_key, activity = _get_activity(activity_name)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    if any(_normalize_email(participant) == normalized_email for participant in activity["participants"]):
        raise HTTPException(status_code=400, detail="Student already signed up for this activity")

    if len(activity["participants"]) >= activity["max_participants"]:
        raise HTTPException(status_code=400, detail="Activity is full")

    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name_key}"}


@app.delete("/activities/{activity_name}/unregister")
async def unregister_for_activity(activity_name: str, request: Request, email: str | None = None):
    """Remove a student from an activity"""
    email = await _get_email_from_request(request, email)
    normalized_email = _normalize_email(email)

    activity_name_key, activity = _get_activity(activity_name)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    for index, participant in enumerate(activity["participants"]):
        if _normalize_email(participant) == normalized_email:
            activity["participants"].pop(index)
            return {"message": f"Unregistered {participant} from {activity_name_key}"}

    raise HTTPException(status_code=404, detail="Student is not signed up for this activity")

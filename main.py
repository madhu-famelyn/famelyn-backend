import os
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json

import models
import schemas
from database import engine, get_db, warmup_db
from email_utils import send_confirmation_email, send_registration_email, send_meet_link_email

# Initialize database tables
try:
    models.Base.metadata.create_all(bind=engine)
    print("[DB] Tables initialized successfully.")
except Exception as e:
    print(f"[DB] Initial table creation failed: {e}")

app = FastAPI(
    title="Famelyn Lead Capture API",
    description="Backend API for capturing and storing Famelyn presence audits, roadmap requests, and inner circle signups.",
    version="1.0.0"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Wake up the database on API startup."""
    warmup_db()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Famelyn Lead Capture API!",
        "docs": "/docs"
    }

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Simple health check endpoint that verifies DB connectivity."""
    try:
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {str(e)}"
        )

@app.post("/api/contact", response_model=schemas.ContactSubmissionOut, status_code=status.HTTP_201_CREATED)
def submit_contact(payload: schemas.ContactSubmissionCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a new contact submission from one of the intake forms and trigger confirmation email."""
    try:
        new_submission = models.ContactSubmission(
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            linkedin=payload.linkedin,
            message=payload.message,
            submission_type=payload.submission_type
        )
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)

        # Queue sending the email in the background
        background_tasks.add_task(
            send_confirmation_email,
            recipient_email=payload.email,
            recipient_name=payload.name,
            submission_type=payload.submission_type
        )

        return new_submission
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during submission: {str(e)}"
        )

@app.get("/api/submissions", response_model=List[schemas.ContactSubmissionOut])
def get_submissions(db: Session = Depends(get_db)):
    """Get all submissions. Used for verification/admin view."""
    try:
        submissions = db.query(models.ContactSubmission).order_by(models.ContactSubmission.created_at.desc()).all()
        return submissions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error retrieving submissions: {str(e)}"
        )

@app.post("/api/register-course", response_model=schemas.CourseRegistrationOut, status_code=status.HTTP_201_CREATED)
def register_course(payload: schemas.CourseRegistrationCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Create a new course registration submission and trigger registration email in the background."""
    try:
        new_registration = models.CourseRegistration(
            name=payload.name,
            phone=payload.phone,
            email=payload.email,
            company_name=payload.company_name,
            designation=payload.designation,
            selected_slot=payload.selected_slot,
            attendance_reason=payload.attendance_reason,
            linkedin_challenge=payload.linkedin_challenge,
            linkedin_activity_level=payload.linkedin_activity_level,
            linkedin_goals=payload.linkedin_goals
        )
        db.add(new_registration)
        db.commit()
        db.refresh(new_registration)

        # Try to find the course details for the email template
        course_heading = "Enhancing Your LinkedIn Profile"
        course_sub_heading = "Build Your Brand. Unlock Opportunities."
        course_duration = "1 Hour"

        # Fallback check: try to find a course that has this slot in its timings JSON
        active_courses = db.query(models.Course).all()
        for c in active_courses:
            try:
                slots_data = json.loads(c.timings)
                for s in slots_data:
                    slot_str = s.get("slot") if isinstance(s, dict) else str(s)
                    if slot_str == payload.selected_slot:
                        course_heading = c.heading
                        course_sub_heading = c.sub_heading
                        course_duration = c.duration
                        break
            except Exception:
                pass

        # Queue sending the email in the background
        background_tasks.add_task(
            send_registration_email,
            recipient_email=payload.email,
            recipient_name=payload.name,
            selected_slot=payload.selected_slot,
            company_name=payload.company_name,
            designation=payload.designation,
            course_heading=course_heading,
            course_sub_heading=course_sub_heading,
            course_duration=course_duration
        )

        return new_registration
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during registration: {str(e)}"
        )

@app.get("/api/course-registrations", response_model=List[schemas.CourseRegistrationOut])
def get_course_registrations(db: Session = Depends(get_db)):
    """Get all course registrations. Used for verification/admin view."""
    try:
        registrations = db.query(models.CourseRegistration).order_by(models.CourseRegistration.created_at.desc()).all()
        return registrations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error retrieving course registrations: {str(e)}"
        )

import json

# Active course registration slots config (Fallback default slots)
ACTIVE_COURSE_SLOTS = [
    "1st July | 3:00 PM | Gowra Deccan.",
    "4th July | 11:00 AM | Online Session"
]

@app.get("/api/course-slots", response_model=List[str])
def get_course_slots(db: Session = Depends(get_db)):
    """Get the active list of Date & Time slots for the personal branding session."""
    active_course = db.query(models.Course).filter(models.Course.is_active == True).order_by(models.Course.created_at.desc()).first()
    if active_course:
        try:
            slots_data = json.loads(active_course.timings)
            if isinstance(slots_data, list):
                return [s.get("slot") if isinstance(s, dict) else str(s) for s in slots_data]
        except Exception as e:
            print(f"[DB] Error parsing course timings: {e}")
            
    return ACTIVE_COURSE_SLOTS

# ─── Admin Authentication ───────────────────────────────────────────────────

@app.post("/api/admin/login")
def admin_login(payload: schemas.AdminLoginRequest):
    """Validate admin credentials and return a simple auth token."""
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "famelyn@2026")

    if payload.username != admin_username or payload.password != admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password."
        )

    # Simple static token (sufficient for single-admin use)
    return {"token": "famelyn-admin-secret-token-2026", "message": "Login successful"}

# ─── Delete Endpoints ────────────────────────────────────────────────────────

@app.delete("/api/course-registrations/{record_id}", status_code=status.HTTP_200_OK)
def delete_course_registration(record_id: int, db: Session = Depends(get_db)):
    """Delete a course registration by ID."""
    record = db.query(models.CourseRegistration).filter(models.CourseRegistration.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Course registration not found.")
    db.delete(record)
    db.commit()
    return {"message": f"Course registration #{record_id} deleted successfully."}

@app.delete("/api/submissions/{record_id}", status_code=status.HTTP_200_OK)
def delete_submission(record_id: int, db: Session = Depends(get_db)):
    """Delete a contact submission by ID."""
    record = db.query(models.ContactSubmission).filter(models.ContactSubmission.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Contact submission not found.")
    db.delete(record)
    db.commit()
    return {"message": f"Submission #{record_id} deleted successfully."}

# ─── Send Meet Link to Online Registrants ───────────────────────────────────

@app.post("/api/send-meet-link", status_code=status.HTTP_200_OK)
def send_meet_link(payload: schemas.MeetLinkRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Send a Google Meet link email to all online session registrants (optionally filtered by a specific slot)."""
    all_registrations = db.query(models.CourseRegistration).all()
    
    if payload.selected_slot and payload.selected_slot != "all":
        # Target a specific slot
        online_registrants = [
            r for r in all_registrations
            if r.selected_slot == payload.selected_slot
        ]
    else:
        # Fallback to all online slots
        online_registrants = [
            r for r in all_registrations
            if "online" in r.selected_slot.lower()
        ]

    if not online_registrants:
        raise HTTPException(
            status_code=404,
            detail="No registrants found to send the link to matching the criteria."
        )

    # Send email to each online registrant in the background
    for registrant in online_registrants:
        background_tasks.add_task(
            send_meet_link_email,
            recipient_email=registrant.email,
            recipient_name=registrant.name,
            meet_link=payload.meet_link,
            selected_slot=registrant.selected_slot
        )

    return {
        "message": f"Meet link email queued for {len(online_registrants)} registrant(s).",
        "count": len(online_registrants),
        "recipients": [r.email for r in online_registrants]
    }

# ─── Course Management ──────────────────────────────────────────────────────

@app.get("/api/active-course")
def get_active_course(db: Session = Depends(get_db)):
    """Retrieve the details of the currently active course (latest)."""
    active_course = db.query(models.Course).filter(models.Course.is_active == True).order_by(models.Course.created_at.desc()).first()
    if not active_course:
        return None
    
    try:
        timings_list = json.loads(active_course.timings)
    except Exception:
        timings_list = []
        
    return {
        "id": active_course.id,
        "banner": active_course.banner,
        "heading": active_course.heading,
        "sub_heading": active_course.sub_heading,
        "description": active_course.description,
        "duration": active_course.duration,
        "timings": timings_list
    }

@app.get("/api/active-courses")
def get_active_courses(db: Session = Depends(get_db)):
    """Retrieve details of all currently active courses."""
    active_list = db.query(models.Course).filter(models.Course.is_active == True).order_by(models.Course.created_at.desc()).all()
    results = []
    for c in active_list:
        try:
            timings_list = json.loads(c.timings)
        except Exception:
            timings_list = []
        results.append({
            "id": c.id,
            "banner": c.banner,
            "heading": c.heading,
            "sub_heading": c.sub_heading,
            "description": c.description,
            "duration": c.duration,
            "timings": timings_list
        })
    return results

@app.get("/api/admin/courses", response_model=List[schemas.CourseOut])
def get_admin_courses(db: Session = Depends(get_db)):
    """Retrieve list of all courses for admin dashboard."""
    return db.query(models.Course).order_by(models.Course.created_at.desc()).all()

@app.post("/api/admin/courses", status_code=status.HTTP_201_CREATED)
def create_course(payload: schemas.CourseCreate, db: Session = Depends(get_db)):
    """Create a new course."""
    # Create the new course (starts active but does not deactivate others)
    new_course = models.Course(
        banner=payload.banner,
        heading=payload.heading,
        sub_heading=payload.sub_heading,
        description=payload.description,
        duration=payload.duration,
        timings=payload.timings,
        is_active=True
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return {"message": "Course created and activated successfully.", "course_id": new_course.id}

@app.post("/api/admin/courses/{course_id}/toggle-active")
def toggle_course_active(course_id: int, db: Session = Depends(get_db)):
    """Toggle a specific course active/inactive status."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    
    course.is_active = not course.is_active
    db.commit()
    return {"message": f"Course active status set to {course.is_active}."}

@app.post("/api/admin/courses/{course_id}/activate")
def activate_course(course_id: int, db: Session = Depends(get_db)):
    """Set a specific course to active."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
        
    course.is_active = True
    db.commit()
    return {"message": f"Course '{course.heading}' is now active."}

@app.delete("/api/admin/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course by ID."""
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    
    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully."}


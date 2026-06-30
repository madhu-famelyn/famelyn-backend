import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class ContactSubmissionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Full name of the contact")
    email: EmailStr = Field(..., description="Valid email address of the contact")
    phone: Optional[str] = Field(None, max_length=50, description="Optional phone number")
    linkedin: Optional[str] = Field(None, max_length=500, description="Optional LinkedIn profile URL")
    message: str = Field(..., min_length=1, description="Message content")
    submission_type: str = Field(..., max_length=100, description="Type of submission (e.g. inner_circle, student_roadmap, executive_audit)")

class ContactSubmissionOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    linkedin: Optional[str]
    message: str
    submission_type: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat()
        }

class CourseRegistrationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Full name of the applicant")
    phone: str = Field(..., min_length=1, max_length=50, description="Contact number")
    email: EmailStr = Field(..., description="Email address")
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    designation: str = Field(..., min_length=1, max_length=255, description="Current designation")
    selected_slot: str = Field(..., min_length=1, max_length=255, description="Selected date and time slot")
    attendance_reason: str = Field(..., min_length=1, description="Reason for attending")
    linkedin_challenge: str = Field(..., min_length=1, description="Biggest challenge faced on LinkedIn")
    linkedin_activity_level: str = Field(..., min_length=1, max_length=100, description="How active they are on LinkedIn")
    linkedin_goals: str = Field(..., min_length=1, max_length=500, description="What they want to achieve on LinkedIn")

class CourseRegistrationOut(BaseModel):
    id: int
    name: str
    phone: str
    email: EmailStr
    company_name: str
    designation: str
    selected_slot: str
    attendance_reason: str
    linkedin_challenge: str
    linkedin_activity_level: str
    linkedin_goals: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat()
        }

class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, description="Admin username")
    password: str = Field(..., min_length=1, description="Admin password")

class MeetLinkRequest(BaseModel):
    meet_link: str = Field(..., min_length=5, description="Google Meet or video call link to send to online registrants")
    selected_slot: Optional[str] = Field(None, description="Optional specific slot to filter recipients")

class CourseCreate(BaseModel):
    banner: Optional[str] = Field(None, description="Base64 encoded image or URL")
    heading: str = Field(..., min_length=1, max_length=255)
    sub_heading: str = Field(..., min_length=1, max_length=255)
    description: str = Field(...)
    duration: str = Field(..., min_length=1, max_length=100)
    timings: str = Field(..., description="JSON string representation of timings/slots")

class CourseOut(BaseModel):
    id: int
    banner: Optional[str]
    heading: str
    sub_heading: str
    description: str
    duration: str
    timings: str
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat()
        }


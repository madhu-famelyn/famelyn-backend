import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from database import Base

class ContactSubmission(Base):
    __tablename__ = "contact_submissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    linkedin = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    submission_type = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ContactSubmission id={self.id} name={self.name} type={self.submission_type}>"

class CourseRegistration(Base):
    __tablename__ = "course_registrations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    designation = Column(String(255), nullable=False)
    selected_slot = Column(String(255), nullable=False)
    attendance_reason = Column(Text, nullable=False)
    linkedin_challenge = Column(Text, nullable=False)
    linkedin_activity_level = Column(String(100), nullable=False)
    linkedin_goals = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<CourseRegistration id={self.id} name={self.name} slot={self.selected_slot}>"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    banner = Column(Text, nullable=True) # Base64 encoded image or URL
    heading = Column(String(255), nullable=False)
    sub_heading = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    duration = Column(String(100), nullable=False)
    timings = Column(Text, nullable=False) # JSON list storing timing/slot details
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Course id={self.id} heading={self.heading} is_active={self.is_active}>"

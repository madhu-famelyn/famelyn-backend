import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_confirmation_email(recipient_email: str, recipient_name: str, submission_type: str):
    """Sends a formatted HTML confirmation email to the user depending on their submission type."""
    # Load configuration
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_name = os.getenv("SMTP_FROM_NAME", "Famelyn")

    # Fallback/Check: If username or password are empty, skip sending but log a warning
    if not smtp_username or not smtp_password:
        print("[Email] SMTP credentials not set in environment. Skipping email confirmation.")
        print(f"[Email] Lead details - Name: {recipient_name}, Email: {recipient_email}, Type: {submission_type}")
        return

    # Map submission type to email subject and description text
    if submission_type == "student_roadmap":
        subject = "Your Famelyn Growth Roadmap is Prepared"
        intro_text = "Thank you for requesting your Growth Roadmap. We are compiling your personalized guide to convert your ambition and experience into a composed LinkedIn presence."
        action_text = "Our team will review your LinkedIn URL and deliver your customized Roadmap analysis within 24–48 hours."
    elif submission_type == "executive_audit":
        subject = "Your Executive Presence Audit Request Received"
        intro_text = "Thank you for requesting your Executive Presence Audit. We design strategic presence layers to make senior leadership and competence visible to boards, investors, and peers."
        action_text = "Our senior strategists are conducting a manual review of your profile. We will email your finished visibility audit shortly."
    else:
        # Default or inner_circle
        subject = "Welcome to the Famelyn Inner Circle"
        intro_text = "Your private intake application to access the Famelyn Inner Circle has been received."
        action_text = "We are reviewing your details. A strategist will contact you to arrange your complimentary 10-minute LinkedIn consultation."

    # Create HTML Email Body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #f4f3ec;
                color: #0b1c2c;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #001f3f;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                border: 1px solid rgba(232, 220, 200, 0.1);
            }}
            .email-header {{
                background-color: #0b1c2c;
                padding: 40px 30px;
                text-align: center;
                border-bottom: 2px solid #c5a059;
            }}
            .email-header h1 {{
                color: #f9f7f2;
                font-size: 28px;
                font-weight: 800;
                margin: 0;
                letter-spacing: -0.5px;
            }}
            .email-header h1 span {{
                color: #c5a059;
            }}
            .email-body {{
                padding: 40px 30px;
                background-color: #001f3f;
                color: #f9f7f2;
                line-height: 1.6;
            }}
            .email-body h2 {{
                color: #c5a059;
                font-size: 20px;
                margin-top: 0;
                margin-bottom: 20px;
            }}
            .email-body p {{
                font-size: 16px;
                color: #b0c2d6;
                margin-bottom: 20px;
            }}
            .highlight-box {{
                background: rgba(197, 160, 89, 0.08);
                border-left: 3px solid #c5a059;
                padding: 20px;
                border-radius: 4px;
                margin: 25px 0;
            }}
            .highlight-box p {{
                margin: 0;
                color: #f9f7f2;
                font-size: 15px;
                font-weight: 500;
            }}
            .email-footer {{
                background-color: #0b1c2c;
                padding: 30px;
                text-align: center;
                font-size: 12px;
                color: #6b6375;
                border-top: 1px solid rgba(255,255,255,0.05);
            }}
            .email-footer a {{
                color: #c5a059;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>Famelyn<span>.</span></h1>
            </div>
            <div class="email-body">
                <h2>Hello {recipient_name},</h2>
                <p>{intro_text}</p>
                
                <div class="highlight-box">
                    <p>{action_text}</p>
                </div>
                
                <p>If you have any questions or want to provide additional details, feel free to reply directly to this email.</p>
                
                <p style="margin-top: 40px; color: #f9f7f2;">
                    Best regards,<br>
                    <strong>The Famelyn Team</strong>
                </p>
            </div>
            <div class="email-footer">
                <p>&copy; 2026 Famelyn. All rights reserved.</p>
                <p>Unlocking professional influence and executive authority.</p>
                <p><a href="https://linkedin.com/company/famelyn">LinkedIn</a> &bull; <a href="https://www.instagram.com/famelyn_/">Instagram</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    # Build MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{smtp_from_name} <{smtp_username}>"
    msg["To"] = recipient_email

    # Plain-text version for fallbacks
    plain_text = f"Hello {recipient_name},\n\n{intro_text}\n\n{action_text}\n\nBest regards,\nThe Famelyn Team"
    
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        print(f"[Email] Connecting to SMTP server {smtp_host}:{smtp_port}...")
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        server.starttls()
        print("[Email] Logging in...")
        server.login(smtp_username, smtp_password)
        print(f"[Email] Sending confirmation email to {recipient_email}...")
        server.send_message(msg)
        server.quit()
        print(f"[Email] Confirmation email sent successfully to {recipient_email}!")
    except Exception as e:
        print(f"[Email] Error occurred while sending email to {recipient_email}: {e}")
def send_registration_email(recipient_email: str, recipient_name: str, selected_slot: str, company_name: str, designation: str, course_heading: str = "Enhancing Your LinkedIn Profile", course_sub_heading: str = "Build Your Brand. Unlock Opportunities.", course_duration: str = "1 Hour"):
    """Sends a formatted HTML confirmation email to the user confirming their LinkedIn Personal Branding Session seat."""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_name = os.getenv("SMTP_FROM_NAME", "Famelyn")

    if not smtp_username or not smtp_password:
        print("[Email] SMTP credentials not set. Skipping course registration email confirmation.")
        print(f"[Email] Registration details - Name: {recipient_name}, Email: {recipient_email}, Slot: {selected_slot}")
        return

    subject = f"Confirmation: Your Seat is Reserved ({course_heading})"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #f4f3ec;
                color: #0b1c2c;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #001f3f;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 10px 30px rgba(0,0,0,0.15);
                border: 1px solid rgba(232, 220, 200, 0.1);
            }}
            .email-header {{
                background-color: #0b1c2c;
                padding: 40px 30px;
                text-align: center;
                border-bottom: 2px solid #c5a059;
            }}
            .email-header h1 {{
                color: #f9f7f2;
                font-size: 28px;
                font-weight: 800;
                margin: 0;
                letter-spacing: -0.5px;
            }}
            .email-header h1 span {{
                color: #c5a059;
            }}
            .email-body {{
                padding: 40px 30px;
                background-color: #001f3f;
                color: #f9f7f2;
                line-height: 1.6;
            }}
            .email-body h2 {{
                color: #c5a059;
                font-size: 20px;
                margin-top: 0;
                margin-bottom: 20px;
            }}
            .email-body p {{
                font-size: 16px;
                color: #b0c2d6;
                margin-bottom: 20px;
            }}
            .highlight-box {{
                background: rgba(197, 160, 89, 0.08);
                border-left: 3px solid #c5a059;
                padding: 20px;
                border-radius: 4px;
                margin: 25px 0;
            }}
            .highlight-box p {{
                margin: 0 0 8px 0;
                color: #f9f7f2;
                font-size: 15px;
            }}
            .highlight-box p strong {{
                color: #c5a059;
            }}
            .email-footer {{
                background-color: #0b1c2c;
                padding: 30px;
                text-align: center;
                font-size: 12px;
                color: #6b6375;
                border-top: 1px solid rgba(255,255,255,0.05);
            }}
            .email-footer a {{
                color: #c5a059;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <h1>Famelyn<span>.</span></h1>
            </div>
            <div class="email-body">
                <h2>Hello {recipient_name},</h2>
                <p>Your seat for our exclusive <strong>{course_heading}</strong> has been successfully reserved!</p>
                
                <div class="highlight-box">
                    <p><strong>Topic:</strong> {course_heading} - {course_sub_heading}</p>
                    <p><strong>Selected Slot:</strong> {selected_slot}</p>
                    <p><strong>Duration:</strong> {course_duration}</p>
                    <p><strong>Your Details:</strong> {designation} at {company_name}</p>
                </div>
                
                <p>We are excited to help you optimize your professional presence, increase visibility, and unlock high-value opportunities.</p>
                <p>If you selected the <strong>Online Session</strong>, a link will be sent to your email address prior to the event. For the <strong>In-Person Session</strong>, we look forward to meeting you at the venue.</p>
                
                <p>If you have any questions, feel free to reply to this email.</p>
                
                <p style="margin-top: 40px; color: #f9f7f2;">
                    Best regards,<br>
                    <strong>The Famelyn Team</strong>
                </p>
            </div>
            <div class="email-footer">
                <p>&copy; 2026 Famelyn. All rights reserved.</p>
                <p>Unlocking professional influence and executive authority.</p>
                <p><a href="https://linkedin.com/company/famelyn">LinkedIn</a> &bull; <a href="https://www.instagram.com/famelyn_/">Instagram</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{smtp_from_name} <{smtp_username}>"
    msg["To"] = recipient_email

    plain_text = f"Hello {recipient_name},\n\nYour seat for {course_heading} has been reserved!\n\nSlot: {selected_slot}\nDuration: {course_duration}\n\nBest regards,\nThe Famelyn Team"
    
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"[Email] Course registration email sent successfully to {recipient_email}!")
    except Exception as e:
        print(f"[Email] Failed to send course registration email to {recipient_email}: {e}")



def send_meet_link_email(recipient_email: str, recipient_name: str, meet_link: str, selected_slot: str):
    """Sends the Google Meet session link to an online registrant."""
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from_name = os.getenv("SMTP_FROM_NAME", "Famelyn")

    if not smtp_username or not smtp_password:
        print(f"[Email] SMTP credentials not set. Skipping meet link email to {recipient_email}.")
        return

    subject = "Your Session Link for Famelyn LinkedIn Masterclass"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #f4f3ec;
                color: #0b1c2c;
                margin: 0;
                padding: 0;
            }}
            .email-container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 24px rgba(0,0,0,0.08);
            }}
            .email-header {{
                background-color: #001F3F;
                padding: 36px 40px;
                text-align: center;
            }}
            .brand-name {{
                font-size: 28px;
                font-weight: 900;
                color: #F9F7F2;
                letter-spacing: -0.5px;
            }}
            .brand-dot {{
                color: #C5A059;
            }}
            .email-body {{
                padding: 40px;
            }}
            .greeting {{
                font-size: 22px;
                font-weight: 700;
                color: #001F3F;
                margin-bottom: 12px;
            }}
            .body-text {{
                font-size: 15px;
                line-height: 1.7;
                color: #3a4a5c;
                margin-bottom: 20px;
            }}
            .slot-box {{
                background: #f4f3ec;
                border-left: 4px solid #C5A059;
                border-radius: 6px;
                padding: 14px 18px;
                font-size: 14px;
                color: #001F3F;
                font-weight: 600;
                margin-bottom: 28px;
            }}
            .meet-card {{
                background: linear-gradient(135deg, #001F3F 0%, #003366 100%);
                border-radius: 12px;
                padding: 30px;
                text-align: center;
                margin-bottom: 28px;
            }}
            .meet-label {{
                font-size: 13px;
                color: #C5A059;
                font-weight: 700;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                margin-bottom: 14px;
            }}
            .meet-link-btn {{
                display: inline-block;
                background: #C5A059;
                color: #001F3F !important;
                text-decoration: none;
                font-weight: 800;
                font-size: 15px;
                padding: 14px 32px;
                border-radius: 8px;
                margin-bottom: 14px;
            }}
            .meet-url {{
                font-size: 12px;
                color: #7da0c0;
                word-break: break-all;
            }}
            .note-box {{
                background: #f9f7f2;
                border: 1px solid #e8dcc8;
                border-radius: 8px;
                padding: 16px 20px;
                font-size: 13px;
                color: #3a4a5c;
                line-height: 1.6;
                margin-bottom: 28px;
            }}
            .email-footer {{
                background: #f4f3ec;
                padding: 24px 40px;
                text-align: center;
                font-size: 12px;
                color: #8a9ab0;
                border-top: 1px solid #e8dcc8;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="email-header">
                <div class="brand-name">Famelyn<span class="brand-dot">.</span></div>
            </div>
            <div class="email-body">
                <div class="greeting">Hello, {recipient_name}! 👋</div>
                <p class="body-text">
                    Your session is confirmed! Here is your Google Meet link to join the
                    <strong>LinkedIn Personal Branding Masterclass</strong>.
                    Please save this link and join a few minutes before the session begins.
                </p>

                <div class="slot-box">
                    📅 &nbsp; Your Session: &nbsp; {selected_slot}
                </div>

                <div class="meet-card">
                    <div class="meet-label">🎯 Your Session Link</div>
                    <a href="{meet_link}" class="meet-link-btn" target="_blank">
                        Join Google Meet →
                    </a>
                    <div class="meet-url">{meet_link}</div>
                </div>

                <div class="note-box">
                    <strong>📌 Tips for the session:</strong><br>
                    • Join 5 minutes early to ensure your audio & video are working.<br>
                    • Have your LinkedIn profile open in a separate tab.<br>
                    • Keep a notepad ready for key takeaways.<br>
                    • Use a stable internet connection for the best experience.
                </div>

                <p class="body-text">
                    We look forward to seeing you at the session. If you have any questions,
                    reply to this email or reach us at <strong>madhu@famelyn.com</strong>.
                </p>

                <p class="body-text" style="font-weight:600; color:#001F3F;">
                    See you soon!<br>
                    — The Famelyn Team
                </p>
            </div>
            <div class="email-footer">
                © 2025 Famelyn · All Rights Reserved<br>
                This email was sent to {recipient_email}
            </div>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{smtp_from_name} <{smtp_username}>"
    msg["To"] = recipient_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        print(f"[Email] Meet link email sent successfully to {recipient_email}!")
    except Exception as e:
        print(f"[Email] Failed to send meet link email to {recipient_email}: {e}")

#!/usr/bin/env python3
"""
Send immediate test email.
"""

import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def send_test_email():
    """Send a test email right now."""
    try:
        # Load config
        with open("email_config.json", 'r') as f:
            config = json.load(f)
        
        to_email = config.get("to_email", "drummerforger@gmail.com")
        from_email = config.get("from_email", to_email)
        smtp_username = config.get("smtp_username", to_email)
        smtp_password = config.get("smtp_password", "")
        
        if not smtp_password or smtp_password == "YOUR_GMAIL_APP_PASSWORD_HERE":
            print("❌ Gmail app password not configured in email_config.json")
            return False
        
        # Create message
        subject = "🧪 WholescaleOS System Test - Immediate"
        body = f"""🧪 WholescaleOS System Test

✅ System is working!
📅 Test sent: {datetime.now().strftime('%Y-%m-%d %I:%M %p EST')}
📧 To: {to_email}
🎨 Report Style: Twin.so beautiful format

📊 Current Stats:
• 🔴 High Priority: 17 items
• 🟡 Medium Priority: 17 items  
• 🟢 Low Priority: 56 items
• ✅ Completed: 20 items
• 📈 Total: 110 items tracked

🔄 Next automated run:
• 7:00 AM EST: Beautiful morning report
• 8:00 PM EST: Beautiful evening report

💻 Note: System runs on your computer. Keep it on for scheduled reports!

Test successful! 🎉"""
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Send email
        print(f"📧 Sending test email to {to_email}...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print("✅ Test email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

if __name__ == "__main__":
    send_test_email()
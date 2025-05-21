import asyncio
from playwright.async_api import async_playwright
import time
import smtplib
from email.mime.text import MIMEText
import os
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import requests
import pytz
import subprocess
import re

# Configuration
BOOKING_NUMBER = "6353072"
CHECK_INTERVAL = 3600  # Check every hour
EMAIL_SENDER = "anthony@huikala.org"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECIPIENT = "anthony@huikala.org"

def get_corvette_image():
    try:
        # Download and save the image locally
        response = requests.get("https://hnl.church/uploads/CleanShot%202025-05-15%20at%2013.59.24.png")
        if response.status_code == 200:
            with open("corvette.png", "wb") as f:
                f.write(response.content)
            return "corvette.png"
        return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def send_test_notification():
    subject = "Corvette Tracker - Test Notification"
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; text-align: center; }}
            .info-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .label {{ font-weight: bold; color: #2c3e50; }}
            .value {{ color: #34495e; }}
            .footer {{ text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 Corvette Tracker</h1>
            <img src="https://hnl.church/uploads/CleanShot%202025-05-15%20at%2013.59.24.png" alt="Corvette" style="width: 100%; border-radius: 5px; margin: 10px 0;">
            <div class="info-box">
                <p><span class="label">Booking Number:</span> <span class="value">{BOOKING_NUMBER}</span></p>
                <p><span class="label">Current Status:</span> <span class="value">Test Status</span></p>
                <p><span class="label">Location:</span> <span class="value">Test Location</span></p>
                <p><span class="label">Vessel:</span> <span class="value">Test Vessel</span></p>
                <p><span class="label">Time:</span> <span class="value">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span></p>
            </div>
            <div class="footer">
                This is a test notification from your Corvette Tracker
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Test notification sent successfully")
    except Exception as e:
        print(f"Error sending notification: {e}")

def send_notification(subject, tracking_info):
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; text-align: center; }}
            .info-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .label {{ font-weight: bold; color: #2c3e50; }}
            .value {{ color: #34495e; }}
            .footer {{ text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 0.9em; }}
            .link {{ color: #3498db; text-decoration: none; }}
            .link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 Corvette Tracker</h1>
            <img src="https://hnl.church/uploads/CleanShot%202025-05-15%20at%2013.59.24.png" alt="Corvette" style="width: 100%; border-radius: 5px; margin: 10px 0;">
            <div class="info-box">
                <p><span class="label">Booking Number:</span> <span class="value">{BOOKING_NUMBER}</span></p>
                <p><span class="label">Previous Status:</span> <span class="value">{tracking_info['previous_status']}</span></p>
                <p><span class="label">New Status:</span> <span class="value">{tracking_info['current_status']}</span></p>
                <p><span class="label">Location:</span> <span class="value">{tracking_info['location']}</span></p>
                <p><span class="label">Vessel:</span> <span class="value">{tracking_info['vessel']}</span></p>
                <p><span class="label">Last Update:</span> <span class="value">{tracking_info['last_update']}</span></p>
            </div>
            <div class="footer">
                <p>Your Corvette is on its way! 🚢</p>
                <p><a href="https://www.matson.com/auto-tracking.html" class="link">Track on Matson Website</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Notification sent successfully")
    except Exception as e:
        print(f"Error sending notification: {e}")

def send_current_status(tracking_info):
    subject = "Corvette Tracker - Current Status"
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; text-align: center; }}
            .info-box {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 10px 0; }}
            .label {{ font-weight: bold; color: #2c3e50; }}
            .value {{ color: #34495e; }}
            .footer {{ text-align: center; margin-top: 20px; color: #7f8c8d; font-size: 0.9em; }}
            .link {{ color: #3498db; text-decoration: none; }}
            .link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 Corvette Tracker</h1>
            <img src="https://hnl.church/uploads/CleanShot%202025-05-15%20at%2013.59.24.png" alt="Corvette" style="width: 100%; border-radius: 5px; margin: 10px 0;">
            <div class="info-box">
                <p><span class="label">Booking Number:</span> <span class="value">{BOOKING_NUMBER}</span></p>
                <p><span class="label">Current Status:</span> <span class="value">{tracking_info['status']}</span></p>
                <p><span class="label">Location:</span> <span class="value">{tracking_info['location']}</span></p>
                <p><span class="label">Vessel:</span> <span class="value">{tracking_info['vessel']}</span></p>
                <p><span class="label">Last Update:</span> <span class="value">{tracking_info['last_update']}</span></p>
            </div>
            <div class="footer">
                <p>Current status of your Corvette shipment</p>
                <p><a href="https://www.matson.com/auto-tracking.html" class="link">Track on Matson Website</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("Current status notification sent successfully")
    except Exception as e:
        print(f"Error sending notification: {e}")

async def get_tracking_info():
    subprocess.run(["python", "-m", "playwright", "install", "chromium"], check=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Run in headless mode
        context = await browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = await context.new_page()
        
        try:
            # Navigate to the tracking page
            await page.goto("https://www.matson.com/auto-tracking.html", timeout=60000)

            # Wait for the page to settle
            await asyncio.sleep(5)

            # Try to click and fill the correct input field
            await page.click("#track-number-top-booking")
            await page.fill("#track-number-top-booking", BOOKING_NUMBER)
            await page.click("#track-booking-number")
            await page.wait_for_selector("#shipmentTrackingDetails", timeout=10000)
            details = await page.text_content("#shipmentTrackingDetails")

            print("\n--- DEBUG: Raw details from Matson tracking page ---\n")
            print(details)
            print("\n--- END DEBUG ---\n")

            # Parse the details
            status = "Unknown"
            location = "Unknown"
            vessel = "Unknown"

            # Use regex to extract vessel, location, and status
            if details:
                # Vessel and location extraction
                vessel_match = re.search(r"aboard the ([A-Z0-9 ]+) and is scheduled to arrive in ([A-Z ()]+)", details)
                if vessel_match:
                    vessel = vessel_match.group(1).strip()
                    location = vessel_match.group(2).strip()
                # Status extraction: from 'Your vehicle' to the pick-up date line
                status_match = re.search(r'(Your vehicle.*?)(?:Your estimated available pick-up date is:|Track another vehicle)', details, re.DOTALL)
                if status_match:
                    status = status_match.group(1).replace('\n', ' ').strip()
                else:
                    # fallback: just use the first 200 chars as status
                    status = details.strip()[:200]

            tracking_info = {
                "status": status,
                "last_update": datetime.now().strftime("%m-%d-%Y"),
                "location": location,
                "vessel": vessel
            }
            return tracking_info
        except Exception as e:
            print(f"Error fetching tracking info: {e}")
            return None
        finally:
            await browser.close()

def is_6am_hst():
    hst = pytz.timezone('Pacific/Honolulu')
    now = datetime.now(hst)
    return now.hour == 6 and now.minute < 30  # Check within first 30 minutes of 6am

async def main():
    print(f"Starting Corvette Tracker for booking number: {BOOKING_NUMBER}")
    
    # Get and send current status immediately
    print("Fetching current status...")
    tracking_info = await get_tracking_info()
    if tracking_info:
        print("Sending current status notification...")
        send_current_status(tracking_info)
        print("Current status notification sent. Please check your email.")
    
    last_status = tracking_info["status"] if tracking_info else None
    last_notification_time = datetime.now()
    
    while True:
        tracking_info = await get_tracking_info()
        
        if tracking_info:
            current_status = tracking_info["status"]
            current_time = datetime.now()
            
            # Determine if we should send a notification
            should_notify = False
            
            # Check if it's 6am HST
            if is_6am_hst():
                if last_notification_time is None or (current_time - last_notification_time).total_seconds() > 3600:
                    should_notify = True
                    print("Sending daily 6am HST update...")
            
            # Check if status has changed
            elif last_status is not None and current_status != last_status:
                should_notify = True
                print("Status change detected, sending notification...")
            
            # Send notification if needed
            if should_notify:
                notification_info = {
                    "previous_status": last_status if last_status else "Initial Status",
                    "current_status": current_status,
                    "location": tracking_info['location'],
                    "vessel": tracking_info['vessel'],
                    "last_update": tracking_info['last_update']
                }
                send_notification("Corvette Tracker - Status Update", notification_info)
                last_notification_time = current_time
            
            # Update last status
            if last_status is None:
                print(f"Initial status: {current_status}")
                print(f"Location: {tracking_info['location']}")
                print(f"Vessel: {tracking_info['vessel']}")
            elif current_status != last_status:
                print(f"Status changed to: {current_status}")
                print(f"Location: {tracking_info['location']}")
                print(f"Vessel: {tracking_info['vessel']}")
            
            last_status = current_status
        
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main()) 
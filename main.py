# Directory: linkedin-lead-agent
# File: main.py
import os
import time
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PHANTOMBUSTER_API_KEY = os.getenv("PHANTOMBUSTER_API_KEY")
PHANTOMBUSTER_AGENT_ID = os.getenv("PHANTOMBUSTER_AGENT_ID")
EXPANDI_API_KEY = os.getenv("EXPANDI_API_KEY")  # Expandi API key
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FROM_ADDRESS = EMAIL_USERNAME

# Configuration
SEARCH_QUERY = "site:linkedin.com/in AND \"CEO\" AND \"tech startups\""
DAILY_BATCH_SIZE = 20  # Number of leads per run
EMAIL_SUBJECT = "Free 30-Min AI Consultation & Workflow Audit"
EMAIL_BODY_TEMPLATE = (
    "Hi {name},\n\n"
    "I'm reaching out from Plato-Group.ai. We specialize in AI agents that automate workflows, boost efficiency, and reduce costs.\n\n"
    "I’d like to offer you a complimentary 30-minute consultation and business audit to explore how AI-driven solutions can save your operations time and money. No obligations—just actionable insights.\n\n"
    "Book here: {calendly_link}\n\n"
    "Best regards,\n"
    "[Your Name]"  
)
CALENDLY_LINK = os.getenv("CALENDLY_LINK")


def fetch_leads():
    """Trigger the PhantomBuster LinkedIn agent and retrieve leads"""
    launch_url = f"https://api.phantombuster.com/api/v2/agents/{PHANTOMBUSTER_AGENT_ID}/launch"
    headers = {"X-Phantombuster-Key": PHANTOMBUSTER_API_KEY, "Content-Type": "application/json"}
    payload = {"args": [SEARCH_QUERY, DAILY_BATCH_SIZE]}
    resp = requests.post(launch_url, json=payload, headers=headers)
    resp.raise_for_status()
    job_id = resp.json()["data"]["batchId"]

    # Poll until finished
    status_url = f"https://api.phantombuster.com/api/v2/agents/{PHANTOMBUSTER_AGENT_ID}/status/{job_id}"
    while True:
        status = requests.get(status_url, headers=headers).json()["data"]["status"]
        if status in ("finished", "failed"):
            break
        time.sleep(5)

    # Download CSV
    results_url = f"https://phantombuster.s3.amazonaws.com/{job_id}/result.csv"
    lines = requests.get(results_url).text.splitlines()
    leads = []
    for row in lines[1:]:
        profile_url, name = row.split(",")[:2]
        leads.append({"name": name.strip(), "profile": profile_url.strip()})
    return leads


def extract_email_from_profile(profile_url):
    """Use Expandi API to enrich LinkedIn profile with email"""
    url = "https://api.expandi.io/profiles/enrich"
    headers = {"Authorization": f"Bearer {EXPANDI_API_KEY}", "Content-Type": "application/json"}
    payload = {"linkedin_url": profile_url}
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("email")
    return None


def send_email(to_address, recipient_name):
    """Send cold outreach via SMTP"""
    body = EMAIL_BODY_TEMPLATE.format(name=recipient_name, calendly_link=CALENDLY_LINK)
    msg = MIMEText(body)
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = FROM_ADDRESS
    msg["To"] = to_address

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()


def main():
    leads = fetch_leads()
    for lead in leads:
        email = extract_email_from_profile(lead["profile"])
        if not email:
            print(f"Skipping {lead['name']}: no email found.")
            continue
        try:
            send_email(email, lead["name"])
            print(f"Email sent to {lead['name']} <{email}>")
        except Exception as e:
            print(f"Error sending to {email}: {e}")

if __name__ == "__main__":
    main()


# File: .github/workflows/run_agent.yml
name: Run LinkedIn Lead Agent Daily

on:
  schedule:
    - cron: '0 9 * * *'  # every day at 09:00 UTC

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Dependencies
        run: |
          python -m venv venv
          source venv/bin/activate
          pip install -r requirements.txt
      - name: Run Lead Agent
        env:
          PHANTOMBUSTER_API_KEY: ${{ secrets.PHANTOMBUSTER_API_KEY }}
          PHANTOMBUSTER_AGENT_ID: ${{ secrets.PHANTOMBUSTER_AGENT_ID }}
          EXPANDI_API_KEY:      ${{ secrets.EXPANDI_API_KEY }}
          EMAIL_USERNAME:       ${{ secrets.EMAIL_USERNAME }}
          EMAIL_PASSWORD:       ${{ secrets.EMAIL_PASSWORD }}
          CALENDLY_LINK:        ${{ secrets.CALENDLY_LINK }}
        run: |
          source venv/bin/activate
          python main.py

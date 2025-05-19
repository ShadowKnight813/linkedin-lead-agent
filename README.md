# LinkedIn Lead Agent

An automated LinkedIn lead generation and outreach system that identifies potential clients and sends personalized cold outreach emails.

## Features

- Automated LinkedIn profile search using PhantomBuster
- Email enrichment using Expandi API
- Automated cold outreach via SMTP
- Daily scheduled runs via GitHub Actions
- Configurable search queries and email templates

## Prerequisites

- Python 3.10 or higher
- PhantomBuster API key and Agent ID
- Expandi API key
- SMTP server credentials (Gmail or other provider)
- Calendly link for scheduling consultations

## Setup

1. Clone the repository:
```bash
git clone https://github.com/ShadowKnight813/linkedin-lead-agent.git
cd linkedin-lead-agent
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your credentials:
```env
PHANTOMBUSTER_API_KEY=your_phantom_key
PHANTOMBUSTER_AGENT_ID=your_agent_id
EXPANDI_API_KEY=your_expandi_key
EMAIL_USERNAME=your_email
EMAIL_PASSWORD=your_password
CALENDLY_LINK=your_calendly_link
```

## Usage

Run the script manually:
```bash
python main.py
```

The script will:
1. Search LinkedIn for profiles matching your criteria
2. Enrich profiles with email addresses
3. Send personalized cold outreach emails
4. Log all activities

## Configuration

You can customize the following in `main.py`:
- `SEARCH_QUERY`: LinkedIn search query
- `DAILY_BATCH_SIZE`: Number of leads to process per run
- `EMAIL_SUBJECT`: Subject line for outreach emails
- `EMAIL_BODY_TEMPLATE`: Email template for outreach

## GitHub Actions

The script runs automatically every day at 09:00 UTC via GitHub Actions. Make sure to:
1. Add your secrets to GitHub repository settings
2. Enable GitHub Actions in your repository

## Security Notes

- Never commit your `.env` file
- Use app-specific passwords for email
- Regularly rotate API keys
- Monitor your API usage

## License

[Your License]

## Contributing

[Your contribution guidelines]

# LinkedIn CRM Automation

An automated LinkedIn connection and follow-up bot that manages networking leads using Google Sheets and Selenium (`undetected-chromedriver`).

## 📋 Features

- Reads leads (profiles to connect with) from a Google Sheet.
- Sends connection requests with optional personalized notes.
- Scrapes the "Recently Added" connections page to detect who accepted the connection request.
- Sends personalized follow-up messages to accepted connections.
- Respects daily action limits to keep your LinkedIn account safe.

---

## 🚀 Setup Guide

Because this bot requires sensitive credentials to run properly, several files are **ignored by Git** for your security. You MUST set them up manually before running the bot.

### 1. Install Dependencies
Ensure you have Python 3 installed.
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
*(If `requirements.txt` is missing, install: `gspread pandas oauth2client selenium undetected-chromedriver`)*

### 2. Google Sheets Setup (`credentials.json`)
The bot reads and writes to a Google Sheet named **`LinkedIn_Stealth_Bot`** (Worksheet: `Leads`).
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Sheets API** and **Google Drive API**.
3. Create a Service Account and download the **JSON Key**.
4. Rename the downloaded file strictly to **`credentials.json`** and place it in the root folder of this project.
5. Create a Google Sheet named exactly `LinkedIn_Stealth_Bot`.
6. Share this sheet with the service account email (found inside `credentials.json`) and give it **Editor** access.
7. Ensure the `Leads` worksheet has the following exact column headers:
   `Profile URL`, `First Name`, `State`, `Timestamp_Last_Action`

### 3. LinkedIn Authentication (`linkedin_cookies.pkl`)
LinkedIn heavily restricts automated logins. Instead of typing your password, the bot uses your existing browser session (cookies).

You have two ways to provide your cookies:

#### Option A: Use the Import Script (Recommended)
You can directly paste your browser cookies into the bot:
1. Log into LinkedIn in your normal browser (Chrome, Safari, Edge).
2. Open Developer Tools (F12 or Cmd+Shift+I) -> **Application** tab -> **Cookies** -> `https://www.linkedin.com`.
3. Find the values for `li_at` and `JSESSIONID`.
4. Run the helper script:
   ```bash
   python import_cookies.py
   ```
   Follow the prompts to paste your cookie values. It will generate `linkedin_cookies.pkl` automatically.

#### Option B: Manual Login Window
If no cookies are found, the bot will launch a Chrome window and give you a **60-second countdown** to log into LinkedIn manually. Once logged in, it will automatically save your session for future runs.

---

## 🤖 Running the Bot

There are two separate scripts depending on what you want the bot to do:

**1. Connection Outreach Bot**
Runs the main sweep: checks for newly accepted connections, then sends out new connection requests based on your Google Sheet.
```bash
python main.py
```

**2. Follow-Up Messaging Bot**
Targets leads marked as `Accepted` in your Google Sheet and sends them the configured follow-up message.
```bash
python main_messaging.py
```

---

## 🚫 Files Ignored by Git (Do Not Commit)
For security, the `.gitignore` prevents the following files from being uploaded to GitHub:
- `credentials.json` (Your Google Service Account secret)
- `linkedin_cookies.pkl` (Your active LinkedIn session)
- `venv/` (Python environment)
- `update_queue.json` (Local task queue cache)

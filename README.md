# LinkedIn-CRM-Automation
This project is a sophisticated LinkedIn CRM &amp; Network Automation System built with Python. It bridges the gap between frontend browser automation and backend data management by utilizing Google Sheets as a real-time database.
# 🤖 LinkedIn CRM & Network Automation System

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Selenium](https://img.shields.io/badge/Selenium-Web%20Automation-green)
![GSpread](https://img.shields.io/badge/Google%20Sheets-Database-yellow)

## Project Overview 📖
This project is a sophisticated **Browser Automation & CRM Tool** designed to streamline professional networking. It bridges the gap between **LinkedIn** (for frontend user interaction) and **Google Sheets** (as a backend database).

Unlike simple "bots," this system uses a "Controller Worker" architecture to manage connection limits, track state (Sent, Accepted, Failed), and perform intelligent follow-ups.

> **⚠️ Disclaimer:** This software is a Proof of Concept (PoC) for educational purposes, demonstrating capabilities in browser automation (Selenium) and API integration. It is not intended for spam or violating Terms of Service.

## Key Features ⚙️
* **Stealth Browser Control:** Uses `undetected_chromedriver` to mimic human behavior (random sleeps, scroll patterns) and bypass basic bot detection.
* **State-Machine Logic:** Tracks every lead in a database (Google Sheets) with states: `Idle` → `Sent` → `Accepted` → `Messaged`.
* **Hybrid Storage:**
    * *Google Sheets:* Acts as the master database for lead management.
    * *Local Pickle Files:* Manages session cookies to maintain login persistence without storing passwords in plain text.
* **Modular Architecture:** Separates logic into specific modules (`ghost` for browser, `controller` for logic, `database` for API).


## Technical Implementation Details 🚀

This system is architected around a **Controller-Worker pattern** to ensure robustness, scalability, and safety.

### 1. The Controller Logic (`controller.py`)
The "Brain" of the operation. Instead of a simple loop, the controller makes intelligent decisions based on the current state of the database and strict operational constraints.
* **Rate Limiting:** Implements a strict daily cap (e.g., `MAX_DAILY_CONNECTS = 20`) to stay within safe operational thresholds.
* **State Machine:** Manages the lifecycle of a lead through defined states:
    `Idle` → `Sent` → `Accepted` → `Messaged`.
* **Smart Scheduling:** Uses timestamp analysis to ensure follow-up checks (e.g., checking if someone accepted) only happen at defined intervals (e.g., every 12 hours), optimizing resource usage.

### 2. Stealth Browser Engine (`ghost.py`)
The "Worker" that interacts with the frontend.
* **Anti-Detection:** Built on `undetected_chromedriver` to patch standard Selenium WebDriver properties that trigger anti-bot systems.
* **Human Mimicry:** Implements randomized latency (jitter) between actions and non-linear scrolling patterns to mimic organic user behavior.
* **Session Persistence:** Utilizes Python's `pickle` module to serialize and store session cookies locally. This allows the bot to resume sessions without repeated logins, reducing suspicious login activity.

### 3. Database Layer (`database_manager.py`)
Acts as the interface between the Python runtime and the Google Sheets backend.
* **API Management:** Handles authentication via Google OAuth2 service accounts.
* **Data Normalization:** Automatically sanitizes input URLs (stripping tracking parameters and protocol prefixes) to ensure `O(1)` lookup efficiency and prevent duplicate entries.
* **Batch Processing:** Scrapes "Recently Added" connections in bulk to reconcile the database state with actual LinkedIn activity in a single pass.

---

## How to Run 🛠️

### Prerequisites
* Python 3.8+
* Google Cloud Service Account (JSON Key)
* Chrome Browser installed

### 1. Installation
Clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```
### 2. Setup Credentials:
* Rename credentials_example.json to credentials.json and add your Google Cloud Service Account keys.
* Share your Google Sheet with the Service Account email.

### 3. Run the Connection Bot:
```bash
python main.py
```
### 4. Run the Messaging Bot (Only messages 'Accepted' leads):
```bash
python main_messaging.py
```
## Future Improvements 🔮
[ ] Implement Headless Mode for server-side deployment.
[ ] Add OpenAI API integration to generate personalized connection notes based on profile bios.
[ ] Create a Flask UI to monitor bot status from a web dashboard.

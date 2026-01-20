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

## Project Structure 📂
```text
├── main.py                # Entry point for Connection Logic
├── main_messaging.py      # Entry point for Follow-up Messaging
├── controller.py          # The "Brain": Decides next action (Connect vs Check Status)
├── ghost.py               # Class for handling Connection browser actions
├── ghost_messaging.py     # Class for handling Messaging browser actions
├── database_manager.py    # Handles Google Sheets API (Read/Write)
├── credentials_example.json # Template for Google Cloud API keys
└── requirements.txt       # Project dependencies

import time
from datetime import datetime, timedelta
import pandas as pd
from database_manager import DatabaseManager

# --- ⚙️ USER SETTINGS ---
MAX_DAILY_CONNECTS = 20
MAX_DAILY_FOLLOWUPS = 15
BATCH_CHECK_SIZE = 5 
CHECK_INTERVAL_HOURS = 12  # Only re-check the same person every 12 hours

class BotController:
    def __init__(self):
        self.db = DatabaseManager()

    def check_daily_limits(self, df):
        """Counts actions taken today."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Filter for today's actions
        # We handle NaN/Empty values safely
        valid_dates = df['Timestamp_Last_Action'].astype(str)
        actions_today = df[valid_dates.str.contains(today_str, na=False)]
        
        connects_today = len(actions_today[actions_today['State'] == 'Sent'])
        followups_today = len(actions_today[actions_today['State'] == 'Completed'])

        print(f"📊 Status Today: {connects_today}/{MAX_DAILY_CONNECTS} Connects | {followups_today}/{MAX_DAILY_FOLLOWUPS} Follow-ups")
        
        return {
            "can_connect": connects_today < MAX_DAILY_CONNECTS,
            "can_followup": followups_today < MAX_DAILY_FOLLOWUPS
        }

    def get_next_job(self):
        """Decides the next action by RE-READING the database."""
        
        # 1. REFRESH DATA
        df = self.db.fetch_leads()
        
        # 2. Check Limits
        limits = self.check_daily_limits(df)

        # 3. PRIORITY 1: Check Acceptances (Timed)
        # We only want people who are 'Sent' AND haven't been checked recently
        sent_leads = df[df['State'] == 'Sent'].copy()
        
        if not sent_leads.empty:
            # Helper logic to parse timestamps
            def is_time_to_check(timestamp_str):
                try:
                    last_check = datetime.strptime(str(timestamp_str), "%Y-%m-%d %H:%M:%S")
                    # Return True if it's been more than CHECK_INTERVAL_HOURS
                    return datetime.now() - last_check > timedelta(hours=CHECK_INTERVAL_HOURS)
                except:
                    # If timestamp is empty or broken, check it immediately
                    return True

            # Filter the list
            eligible_to_check = sent_leads[sent_leads['Timestamp_Last_Action'].apply(is_time_to_check)]
            
            if not eligible_to_check.empty:
                # Return the top result
                target = eligible_to_check.iloc[0]
                return {
                    "type": "CHECK_ACCEPTANCE",
                    "target_url": target['Profile URL'],
                    "first_name": target['First Name']
                }
        
        accepted_leads = df[df['State'].str.strip().str.lower() == 'accepted']
        
        if not accepted_leads.empty:
            target = accepted_leads.iloc[0]
            print(f"   💌 Found {len(accepted_leads)} accepted profiles ready for messaging.")
            return {
                "type": "SEND_FOLLOWUP",
                "target_url": target['Profile URL'],
                "first_name": target['First Name']
            }
        
        if limits['can_connect']:
            new_leads = df[df['State'] == 'Idle']
            if not new_leads.empty:
                target = new_leads.iloc[0]
                return {
                    "type": "SEND_CONNECT",
                    "target_url": target['Profile URL'],
                    "first_name": target['First Name']
                }

        print("✅ No eligible jobs found (Limits reached or Queue empty).")
        return None

if __name__ == "__main__":
    bot = BotController()
    bot.get_next_job()

import time
import random
import pandas as pd
from database_manager import DatabaseManager
from ghost_messaging import GhostMessenger

# --- ⚙️ MESSAGE SETTINGS ---
# Use {name} where you want the person's first name to appear
FOLLOWUP_MESSAGE = "Hey {name}! Thanks for connecting. I noticed you're also in the tech space. I'm building a tool to automate LinkedIn networking—would love to hear your thoughts on it if you have a sec."
# ---------------------------

def run_messaging_bot():
    print("🤖 STARTING MESSAGING BOT...")
    print("👉 Only targeting users with Status: 'Accepted'")
    print("👉 Press 'Ctrl + C' to STOP safely.\n")

    db = DatabaseManager()
    
    # 1. Initialize Browser
    ghost = GhostMessenger()
    if not ghost.load_session():
        print("❌ Error: No cookies found. Run the main bot first to login!")
        ghost.kill()
        return

    # 2. Work Loop
    processed_count = 0
    
    try:
        while True:
            # A. Fetch Data
            df = db.fetch_leads()
            
            # B. Filter for 'Accepted' only
            accepted_leads = df[df['State'].str.strip().str.lower() == 'accepted']
            
            if accepted_leads.empty:
                print("🏁 No 'Accepted' profiles found to message. Exiting.")
                break

            # C. Pick the first one
            target = accepted_leads.iloc[0]
            
            # GET NAME AND PROFILE
            raw_name = str(target['First Name'])
            profile_url = target['Profile URL']
            
            print(f"\n💌 Mission {processed_count + 1}: Messaging -> {raw_name}")

            # D. Send Message (Pass the name now)
            status = ghost.send_message(profile_url, FOLLOWUP_MESSAGE, raw_name)
            
            # E. Update Database
            if status == "Messaged":
                db.queue_update(profile_url, "State", "Messaged")
                db.queue_update(profile_url, "Timestamp_Last_Action", str(time.strftime("%Y-%m-%d %H:%M:%S")))
            
            elif status == "Skipped":
                db.queue_update(profile_url, "State", "Skipped")
            
            elif status == "Failed":
                db.queue_update(profile_url, "Timestamp_Last_Action", str(time.strftime("%Y-%m-%d %H:%M:%S")))

            processed_count += 1
            
            # F. Human Pause
            wait_time = random.uniform(45, 120)
            print(f"☕ Taking a break for {int(wait_time)} seconds...")
            time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\n🛑 STOPPING BOT...")
    
    finally:
        ghost.kill()
        print("👋 Session Ended.")

if __name__ == "__main__":
    run_messaging_bot()
import os
import sys
from database_manager import DatabaseManager
from controller import BotController
from ghost import GhostBrowser, COOKIE_FILE
import time
import random
from selenium.common.exceptions import WebDriverException

# --- ⚙️ USER SETTINGS ---
SEND_WITH_NOTE = False  # Changed to False based on your previous logs
# -----------------------

def is_browser_alive(ghost):
    try:
        if len(ghost.driver.window_handles) > 0: return True
    except: return False
    return False

def run_bot():
    print(f"🤖 STARTING LINKEDIN BOT...")
    print("👉 Press 'Ctrl + C' to STOP.")
    
    db = DatabaseManager()
    controller = BotController()
    
    # 1. Start Ghost
    ghost = GhostBrowser()
    if not ghost.load_session():
        # Login logic (simplified for brevity, use full logic if needed)
        print("🛑 Cookies failed. Login manually.")
        ghost.login_manual()

    # --- 🧹 BATCH SWEEP (The Only Verification We Need) ---
    print("\n🧹 RUNNING BATCH ACCEPTANCE CHECK...")
    try:
        recent_urls = ghost.scan_recent_connections()
        if recent_urls:
            db.batch_update_accepted(recent_urls)
        else:
            print("   ⚠️ No recent connections found.")
    except Exception as e:
        print(f"   ❌ Sweep error: {e}")
    print("------------------------------------------------\n")

    jobs_processed = 0
    
    try:
        while True:
            if not is_browser_alive(ghost): break

            # 2. Get Job
            # controller.py will still serve 'CHECK_ACCEPTANCE' if we don't fix it,
            # so we handle it intelligently here.
            job = controller.get_next_job()
            
            if not job:
                print("🏁 No jobs available. Session Complete.")
                break
                
            print(f"\n⚔️ Mission {jobs_processed + 1}: {job['type']} -> {job.get('first_name', 'User')}")
            
            try:
                # --- A. SEND CONNECT (Priority) ---
                if job['type'] == "SEND_CONNECT":
                    status = ghost.connect_with_user(job['target_url'], job['first_name'], enable_note=SEND_WITH_NOTE)
                    
                    if status == "Sent":
                        db.queue_update(job['target_url'], "State", "Sent")
                        db.queue_update(job['target_url'], "Timestamp_Last_Action", str(time.strftime("%Y-%m-%d %H:%M:%S")))
                    elif status == "Failed":
                        db.queue_update(job['target_url'], "State", "Failed")

                # --- B. CHECK ACCEPTANCE (The Wasteful Loop Fix) ---
                elif job['type'] == "CHECK_ACCEPTANCE":
                    # Since we just ran the Batch Sweep, if this person is still 'Sent', 
                    # they really haven't accepted yet (or aren't in the top 40).
                    # We do NOT visit their profile to save time.
                    print(f"   ⏳ {job.get('first_name')} hasn't appeared in 'Recently Added' yet.")
                    print("   ⏭️ Skipping visit & updating timestamp to check later.")
                    
                    # Update timestamp so Controller doesn't pick them again for 12h
                    db.queue_update(job['target_url'], "Timestamp_Last_Action", str(time.strftime("%Y-%m-%d %H:%M:%S")))
                
                # --- C. SEND FOLLOWUP (Future Feature) ---
                elif job['type'] == "SEND_FOLLOWUP":
                    pass # Logic coming in next prompt

                jobs_processed += 1
                
                # 3. Human Pause
                wait_time = random.uniform(60, 180) 
                print(f"☕ Taking a break for {int(wait_time)} seconds...")
                time.sleep(wait_time)

            except Exception as e:
                print(f"🔥 Job Error: {e}")
                break

    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    
    finally:
        ghost.kill()

if __name__ == "__main__":
    run_bot()

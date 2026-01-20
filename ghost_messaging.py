import os
import time
import random
import pickle
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CONFIG
COOKIE_FILE = "linkedin_cookies.pkl"

class GhostMessenger:
    def __init__(self):
        print("👻 Summoning the Messaging Ghost...")
        options = uc.ChromeOptions()
        options.add_argument("--no-first-run")
        options.add_argument("--password-store=basic")
        self.driver = uc.Chrome(options=options, use_subprocess=True)

    def random_sleep(self, min_seconds=3, max_seconds=7):
        time.sleep(random.uniform(min_seconds, max_seconds))

    def load_session(self):
        if os.path.exists(COOKIE_FILE):
            print("🍪 Restoring shared session...")
            try:
                self.driver.get("https://www.linkedin.com/") 
                cookies = pickle.load(open(COOKIE_FILE, "rb"))
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.refresh()
                return True
            except Exception as e:
                print(f"⚠️ Cookie error: {e}")
        return False

    def kill(self):
        self.driver.quit()

    def send_message(self, profile_url, message_template, first_name="there"):
        print(f"💌 Visiting: {profile_url}")
        
        # --- NAME FORMATTING LOGIC ---
        # 1. Strip spaces
        # 2. Capitalize first letter, lower the rest (e.g. "RAHUL" -> "Rahul")
        clean_name = first_name.strip().capitalize()
        
        # 3. Create the final message
        final_message = message_template.format(name=clean_name)
        
        print(f"   📝 Formatting: '{first_name}' -> '{clean_name}'")
        # -----------------------------

        self.driver.get(profile_url)
        self.random_sleep(3, 5)
        
        try:
            # 1. CLICK MESSAGE BUTTON
            try:
                msg_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Message') and not(contains(@aria-label, 'locked'))]")
                self.driver.execute_script("arguments[0].click();", msg_btn)
                print("   👉 Clicked 'Message' button...")
            except:
                print("   ❌ 'Message' button missing.")
                return "Failed"

            # 2. WAIT FOR CHAT
            try:
                print("   ⏳ Waiting for chat window...")
                wait = WebDriverWait(self.driver, 10)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "msg-overlay-conversation-bubble")))
                input_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='textbox']")))
                print("   ✅ Chat window loaded.")
            except:
                print("   ⚠️ Chat window failed to load.")
                return "Failed"

            self.random_sleep(1, 2)

            # 3. HISTORY CHECK (Zero Tolerance)
            try:
                bubbles = self.driver.find_elements(By.CSS_SELECTOR, ".msg-s-event-listitem__message-bubble")
                if len(bubbles) == 0:
                     bubbles = self.driver.find_elements(By.CSS_SELECTOR, "li.msg-s-message-list__event")
                
                if len(bubbles) > 0:
                    print(f"   🛑 History detected ({len(bubbles)} msgs). Skipping.")
                    try:
                        close_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-test-icon='close-small']")
                        self.driver.execute_script("arguments[0].click();", close_btn)
                    except: pass
                    return "Skipped"
                
                print("   ✨ Chat is clean. Proceeding...")

            except Exception as e:
                print(f"   ⚠️ History check error: {e}")

            # 4. TYPE MESSAGE (Using Personalized Text)
            print("   ✍️ Typing message...")
            try:
                input_box.click()
                time.sleep(0.5)
                # SEND THE PERSONALIZED MESSAGE
                input_box.send_keys(final_message)
                time.sleep(1)
            except Exception as e:
                print(f"   ❌ Error typing: {e}")
                return "Failed"

            # 5. SEND
            try:
                send_btn = self.driver.find_element(By.CSS_SELECTOR, "button.msg-form__send-button")
                if send_btn.is_enabled():
                    self.driver.execute_script("arguments[0].click();", send_btn)
                    print(f"   📨 Message SENT to {clean_name}!")
                    self.random_sleep(1, 2)
                    try:
                        close_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-test-icon='close-small']")
                        self.driver.execute_script("arguments[0].click();", close_btn)
                    except: pass
                    return "Messaged"
                else:
                    return "Failed"
            except:
                 return "Failed"

        except Exception as e:
            print(f"   ❌ Critical Error: {e}")
            return "Failed"

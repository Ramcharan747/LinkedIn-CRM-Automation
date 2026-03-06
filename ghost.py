import os
import time
import random
import pickle
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# CONFIG
COOKIE_FILE = "linkedin_cookies.pkl"
CONNECT_NOTE = "Hi {name}, I saw your profile and would love to connect!"

class GhostBrowser:
    def __init__(self, headless=False):
        """
        Initializes the Stealth Browser.
        """
        print("👻 Summoning the Ghost Browser...")
        options = uc.ChromeOptions()
        # options.add_argument('--headless') # Keep commented for visibility
        options.add_argument("--no-first-run")
        options.add_argument("--password-store=basic")
        self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=145)

    def random_sleep(self, min_seconds=3, max_seconds=7):
        """Sleeps for a random amount of time."""
        sleep_time = random.uniform(min_seconds, max_seconds)
        print(f"   💤 Sleeping for {round(sleep_time, 1)}s...")
        time.sleep(sleep_time)

    def save_session(self):
        """Saves cookies to a file."""
        print("💾 Saving session cookies...")
        pickle.dump(self.driver.get_cookies(), open(COOKIE_FILE, "wb"))

    def load_session(self):
        """Loads cookies if they exist."""
        if os.path.exists(COOKIE_FILE):
            print("🍪 Restoring session...")
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

    def login_manual(self):
        """Opens LinkedIn and waits 60 seconds for user to log in manually."""
        print("🔐 Opening LinkedIn for manual login...")
        self.driver.get("https://www.linkedin.com/login")
        
        wait_seconds = 60
        print(f"⏳ You have {wait_seconds} seconds to log in. Go!")
        
        for remaining in range(wait_seconds, 0, -1):
            print(f"\r   ⏱️  {remaining}s remaining...", end="", flush=True)
            time.sleep(1)
        
        print("\n✅ Login window closed. Saving session...")
        self.save_session()

    def connect_with_user(self, profile_url, first_name, enable_note=False):
        """
        Visits a profile and sends a connection request.
        """
        print(f"🕵️ Visiting: {profile_url}")
        
        # DEBUG: Confirm Note Mode
        mode_status = "✅ ENABLED" if enable_note else "🚫 DISABLED"
        print(f"   ℹ️  Note Mode: {mode_status}")

        self.driver.get(profile_url)
        self.random_sleep(3, 5)
        self.driver.execute_script("window.scrollTo(0, 300);")
        time.sleep(1)

        # CHECK PENDING
        if len(self.driver.find_elements(By.XPATH, "//button[contains(., 'Pending')]")) > 0:
            print(f"   ⚠️ Connection is already Pending.")
            return "Sent"

        # --- STEP 1: EXTRACT URL ID ---
        try:
            clean_url = profile_url.rstrip("/")
            url_id = clean_url.split("/in/")[-1]
            print(f"   🆔 Extracted Profile ID: {url_id}")
        except:
            print("   ⚠️ Could not extract URL ID. Falling back to simple name.")
            url_id = "UNKNOWN"

        # --- STEP 2: FIND EXACT NAME VIA 'ABOUT THIS PROFILE' LINK ---
        official_name = None
        try:
            about_link = self.driver.find_element(By.XPATH, f"//a[contains(@href, '/overlay/about-this-profile/')]")
            official_name = about_link.get_attribute("aria-label")
            print(f"   👤 Extracted Official Name: '{official_name}'")
        except:
            print("   ⚠️ 'About This Profile' link not found. Falling back to H1.")
            try:
                official_name = self.driver.find_element(By.TAG_NAME, "h1").text.strip()
            except:
                official_name = first_name 

        # --- STEP 3: FIND CONNECT BUTTON (Magic Selector) ---
        magic_xpath = f"//*[contains(@aria-label, 'Invite {official_name} to connect')]"
        connect_btn = None

        try:
            # PHASE A: Direct Check
            try:
                btn = self.driver.find_element(By.XPATH, magic_xpath)
                if btn.is_displayed():
                    connect_btn = btn
                    print(f"   ✅ Found Direct Connect Button.")
            except:
                pass

            # PHASE B: More Menu
            if not connect_btn:
                print("   ⚠️ Direct button hidden. Opening 'More' menu...")
                try:
                    more_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'More actions')]")
                    self.driver.execute_script("arguments[0].click();", more_btn)
                    time.sleep(1.5)
                    connect_btn = self.driver.find_element(By.XPATH, magic_xpath)
                    print(f"   ✅ Found 'Invite' button inside More menu.")
                except Exception as e:
                    print(f"   ❌ 'More' menu strategy failed: {e}")

            # PHASE C: CLICK CONNECT
            if connect_btn:
                self.driver.execute_script("arguments[0].click();", connect_btn)
                self.random_sleep(2, 3)
            else:
                print(f"   ❌ Could not find button for '{official_name}'")
                return "Failed"

            # --- PHASE D: HANDLING THE NOTE LOGIC ---
            
            # CASE 1: Note ENABLED
            if enable_note:
                try:
                    add_note_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Add a note')]")
                    add_note_btn.click()
                    self.random_sleep(1, 2)
                    self.driver.find_element(By.ID, "custom-message").send_keys(CONNECT_NOTE.format(name=first_name))
                    print("   ✍️ Note typed.")
                    
                    # Click the "Send" button (Primary)
                    send_btn = self.driver.find_element(By.CSS_SELECTOR, "div.artdeco-modal__actionbar button.artdeco-button--primary")
                    self.driver.execute_script("arguments[0].click();", send_btn)
                except Exception as e:
                    print(f"   ⚠️ Note failed, trying generic send: {e}")
                    
            # CASE 2: Note DISABLED (Strict Generic Send)
            else:
                print("   ⏩ Note Disabled: Sending generic invite.")
                try:
                    # We specifically look for "Send" or "Send without a note" to avoid accidents
                    # This XPath finds a button labeled "Send now", "Send", or "Send without a note"
                    send_btn = self.driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Send')]")
                    self.driver.execute_script("arguments[0].click();", send_btn)
                except:
                    # Fallback to Primary Button if specific text isn't found
                    try:
                        send_btn = self.driver.find_element(By.CSS_SELECTOR, "div.artdeco-modal__actionbar button.artdeco-button--primary")
                        self.driver.execute_script("arguments[0].click();", send_btn)
                    except:
                        pass # Maybe it sent instantly

            print("   ✅ Connection Request Sent!")
            return "Sent"

        except Exception as e:
            print(f"   ❌ Critical Error: {e}")
            return "Failed"

    def scan_recent_connections(self):
        """
        Scrapes the 'Recently Added' connections page to find who accepted.
        Returns a list of profile URLs.
        Tries multiple URL patterns and selectors for resilience.
        """
        print("🕵️ Scanning 'Recently Added' Connections...")
        
        # Try multiple URL patterns (LinkedIn changes these)
        connection_urls = [
            "https://www.linkedin.com/mynetwork/invite-connect/connections/",
            "https://www.linkedin.com/mynetwork/connections/",
            "https://www.linkedin.com/search/results/people/?network=%5B%22F%22%5D&origin=MEMBER_PROFILE_CANNED_SEARCH&sortBy=%22R%22",
        ]
        
        accepted_profiles = []
        
        for url in connection_urls:
            print(f"   🔗 Trying: {url}")
            self.driver.get(url)
            self.random_sleep(3, 5)
            
            try:
                # Scroll down to load content
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1.5)
                
                # Try multiple XPath selectors (LinkedIn updates DOM frequently)
                selectors = [
                    "//a[contains(@href, '/in/') and not(contains(@href, '/overlay/'))]",
                    "//a[contains(@href, 'linkedin.com/in/')]",
                    "//span[contains(@class, 'entity-result__title')]//a",
                    "//a[contains(@class, 'mn-connection-card__link')]",
                    "//a[contains(@class, 'ember-view') and contains(@href, '/in/')]",
                ]
                
                for selector in selectors:
                    anchors = self.driver.find_elements(By.XPATH, selector)
                    if anchors:
                        print(f"   ✅ Selector matched: {len(anchors)} links found")
                        break
                
                if not anchors:
                    # Debug: Show what's on the page
                    print(f"   ⚠️ No links found with any selector on this URL.")
                    page_title = self.driver.title
                    print(f"   📄 Page title: '{page_title}'")
                    # Check if we're redirected to login
                    if "login" in self.driver.current_url.lower() or "checkpoint" in self.driver.current_url.lower():
                        print("   🔒 Redirected to login/checkpoint! Session may be expired.")
                    continue
                
                for a in anchors:
                    try:
                        href = a.get_attribute("href")
                        if href and "/in/" in href:
                            clean_url = href.split("?")[0].rstrip("/")
                            if clean_url not in accepted_profiles:
                                accepted_profiles.append(clean_url)
                    except:
                        continue
                
                if accepted_profiles:
                    print(f"   ✅ Successfully extracted {len(accepted_profiles)} unique recent connections.")
                    return accepted_profiles
                    
            except Exception as e:
                print(f"   ❌ Error with URL {url}: {e}")
                continue
        
        print(f"   ⚠️ All URL patterns tried. Found {len(accepted_profiles)} connections total.")
        return accepted_profiles

    def kill(self):
        """Gracefully quit the browser."""
        try:
            self.driver.quit()
            print("👻 Ghost Browser dismissed.")
        except:
            pass
if __name__ == "__main__":
    # Test Block
    bot = GhostBrowser()
    bot.load_session()
    time.sleep(5)
    bot.kill()
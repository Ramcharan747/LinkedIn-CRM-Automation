import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# CONFIG
SHEET_NAME = "LinkedIn_Stealth_Bot"
WORKSHEET_NAME = "Leads"
CREDENTIALS_FILE = "credentials.json"

class DatabaseManager:
    def __init__(self):
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
        
    def fetch_leads(self):
        """Reads data from Google Sheets."""
        # print("📥 Fetching data...") # Commented out to reduce noise
        data = self.sheet.get_all_records()
        return pd.DataFrame(data)

    def normalize_url(self, url):
        """Standardizes URL for comparison (removes slashes, https, www)."""
        if not isinstance(url, str): return ""
        # Remove trailing slash, https://, www.
        return url.strip().rstrip("/").replace("https://", "").replace("www.", "")

    def queue_update(self, profile_url, column_name, new_value):
        """
        Robust Update: Finds row by normalizing URLs first.
        """
        try:
            # 1. Fetch all data first (Efficient)
            records = self.sheet.get_all_records()
            target_clean = self.normalize_url(profile_url)
            
            row_index = -1
            
            # 2. Iterate to find match
            # gspread rows start at 2 (1 is header)
            for i, record in enumerate(records):
                sheet_url = self.normalize_url(record.get('Profile URL', ''))
                if sheet_url == target_clean:
                    row_index = i + 2 
                    break
            
            if row_index == -1:
                print(f"   ❌ URL not found in Sheet: {profile_url}")
                return

            # 3. Find Column Number
            headers = self.sheet.row_values(1)
            if column_name in headers:
                col_num = headers.index(column_name) + 1
                
                # 4. Update
                self.sheet.update_cell(row_index, col_num, new_value)
                print(f"   📝 Updated Row {row_index}: {column_name} -> {new_value}")
            else:
                print(f"   ⚠️ Column '{column_name}' missing.")
                
        except Exception as e:
            print(f"   ❌ DB Update Failed: {e}")

    def batch_update_accepted(self, accepted_urls):
        """
        Matches scraped URLs (accepted_urls) against 'Sent' rows in Sheet.
        """
        print("🔄 Reconciling connections...")
        
        # 1. Get current data
        df = self.fetch_leads()
        
        # Normalize the incoming list for fast lookup
        # We use a set for O(1) lookups
        accepted_clean_set = {self.normalize_url(u) for u in accepted_urls}
        
        updates_count = 0
        
        for index, row in df.iterrows():
            current_status = str(row['State']).strip()
            sheet_url_clean = self.normalize_url(row['Profile URL'])
            
            # CHECK MATCH
            if current_status == "Sent" and sheet_url_clean in accepted_clean_set:
                print(f"   🎉 MATCH: {row['First Name']} accepted! Updating status...")
                
                # Update Sheet
                self.queue_update(row['Profile URL'], "State", "Accepted")
                self.queue_update(row['Profile URL'], "Timestamp_Last_Action", str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                updates_count += 1
                
        print(f"   🏁 Reconciliation Complete. {updates_count} updated.")

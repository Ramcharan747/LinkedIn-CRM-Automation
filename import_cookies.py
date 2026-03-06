#!/usr/bin/env python3
"""
🍪 LinkedIn Cookie Importer
Paste your LinkedIn cookies here and they'll be saved for the bot.

HOW TO GET YOUR COOKIES:
1. Log into LinkedIn in your regular browser
2. Open DevTools (F12 or Cmd+Shift+I)
3. Go to Application tab → Cookies → https://www.linkedin.com
4. Copy the cookie values you need (especially: li_at, JSESSIONID)

USAGE:
  python import_cookies.py
"""

import pickle
import json

COOKIE_FILE = "linkedin_cookies.pkl"

def import_from_key_values():
    """Import cookies by pasting key=value pairs."""
    print("\n🍪 LinkedIn Cookie Importer")
    print("=" * 40)
    print("\nYou need at minimum these cookies from LinkedIn:")
    print("  • li_at (your login session token)")
    print("  • JSESSIONID (session ID)")
    print("\nYou can find them in Browser DevTools → Application → Cookies")
    print("=" * 40)
    
    cookies = []
    
    # Essential cookie: li_at
    li_at = input("\n📋 Paste your 'li_at' cookie value: ").strip().strip('"')
    if li_at:
        cookies.append({
            'name': 'li_at',
            'value': li_at,
            'domain': '.linkedin.com',
            'path': '/',
            'secure': True,
            'httpOnly': True,
        })
    
    # Essential cookie: JSESSIONID
    jsessionid = input("📋 Paste your 'JSESSIONID' cookie value: ").strip().strip('"')
    if jsessionid:
        cookies.append({
            'name': 'JSESSIONID',
            'value': jsessionid,
            'domain': '.linkedin.com',
            'path': '/',
            'secure': True,
        })
    
    # Optional: Add more cookies
    print("\n➕ Add more cookies? (Enter empty name to finish)")
    while True:
        name = input("   Cookie name (or Enter to skip): ").strip()
        if not name:
            break
        value = input(f"   Cookie value for '{name}': ").strip().strip('"')
        if value:
            cookies.append({
                'name': name,
                'value': value,
                'domain': '.linkedin.com',
                'path': '/',
                'secure': True,
            })
    
    return cookies


def import_from_json():
    """Import cookies from a JSON string (e.g., from EditThisCookie extension)."""
    print("\n📋 Paste your cookies as JSON (from EditThisCookie or similar).")
    print("   Press Enter twice when done:\n")
    
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    
    raw = "\n".join(lines)
    
    try:
        cookies = json.loads(raw)
        if isinstance(cookies, list):
            return cookies
        else:
            print("❌ Expected a JSON array of cookie objects.")
            return []
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return []


def import_from_header_string():
    """Import from a raw Cookie header string (key=value; key2=value2)."""
    print("\n📋 Paste your Cookie header string (from DevTools → Network → Request Headers):")
    raw = input().strip()
    
    cookies = []
    for pair in raw.split(";"):
        pair = pair.strip()
        if "=" in pair:
            name, value = pair.split("=", 1)
            cookies.append({
                'name': name.strip(),
                'value': value.strip(),
                'domain': '.linkedin.com',
                'path': '/',
                'secure': True,
            })
    
    return cookies


def main():
    print("🍪 LinkedIn Cookie Importer")
    print("=" * 40)
    print("\nHow do you want to import cookies?\n")
    print("  1. Paste key values (li_at, JSESSIONID)")
    print("  2. Paste JSON (from EditThisCookie extension)")
    print("  3. Paste raw Cookie header string")
    
    choice = input("\nChoice (1/2/3): ").strip()
    
    if choice == "1":
        cookies = import_from_key_values()
    elif choice == "2":
        cookies = import_from_json()
    elif choice == "3":
        cookies = import_from_header_string()
    else:
        print("❌ Invalid choice.")
        return
    
    if cookies:
        pickle.dump(cookies, open(COOKIE_FILE, "wb"))
        print(f"\n✅ Saved {len(cookies)} cookies to '{COOKIE_FILE}'")
        print("🚀 You can now run: python main.py")
    else:
        print("\n❌ No cookies to save.")


if __name__ == "__main__":
    main()

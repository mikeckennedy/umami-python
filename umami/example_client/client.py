import json
from pathlib import Path

import umami

file = Path(__file__).parent / 'settings.json'

settings = {}
if file.exists():
    settings = json.loads(file.read_text())

print(umami.user_agent)

url = settings.get('base_url') or input("Enter the base URL for your instance: ")
user = settings.get('username') or input("Enter the username for Umami: ")
password = settings.get('password') or input("Enter the password for ")

umami.set_url_base(url)
login = umami.login(user, password)
print(f"Logged in successfully as {login.user.username} : admin? {login.user.isAdmin}")
print()

print("Verify token:")
print(umami.verify_token())
print()

websites = umami.websites()
print(f"Found {len(websites):,} websites.")
print("First website in list:")
print(websites[0])
print()

if test_domain := settings.get('test_domain'):

    test_site = [w for w in websites if w.domain == test_domain][0]
    print(f"Using {test_domain} for testing events.")

    event_resp = umami.new_event(
        website_id=test_site.id,
        event_name='Umami-Test-Event3',
        title='Umami-Test-Event3',
        hostname=test_site.domain,
        url='/users/actions',
        custom_data={'client': 'umami-tester-v1'},
        referrer='https://talkpython.fm')

    print(f"Created new event: {event_resp}")
else:
    print("No test domain, skipping event creation.")
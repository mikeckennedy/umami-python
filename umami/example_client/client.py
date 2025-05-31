import json
from pathlib import Path
from typing import Any

import umami

file = Path(__file__).parent / 'settings.json'

settings: dict[str, Any] = {}
if file.exists():
    settings = json.loads(file.read_text())

print(umami.user_agent)

url = settings.get('base_url') or input('Enter the base URL for your instance: ')
user = settings.get('username') or input('Enter the username for Umami: ')
password = settings.get('password') or input('Enter the password for ')

umami.set_url_base(url)
print(f'Not currently logged in? {not umami.is_logged_in()}')

login = umami.login(user, password)
print(f'Logged in successfully as {login.user.username} : admin? {login.user.isAdmin}')
print(f'Currently logged in? {umami.is_logged_in()}')
print()

print('Verify token:')
print(umami.verify_token(check_server=False))
print(umami.verify_token())
print()

print('Checking heartbeat')
print(umami.heartbeat())
print()

websites = umami.websites()
print(f'Found {len(websites):,} websites.')
print('First website in list:')
print(websites[0])
print()

if test_domain := settings.get('test_domain'):
    test_site = [w for w in websites if w.domain == test_domain][0]
    print(f'Using {test_domain} for testing events.')

    # Set these once
    umami.set_hostname(test_site.domain)
    umami.set_website_id(test_site.id)

    # Demonstrate the new enable/disable functionality
    print('\n=== Demonstrating tracking enable/disable functionality ===')

    # Test with tracking enabled (default)
    print('1. Sending event with tracking enabled...')
    umami.new_event(
        event_name='Umami-Test-Event3',
        title='Umami-Test-Event3',
        url='/users/actions',
        custom_data={'client': 'umami-tester-v1'},
        referrer='https://talkpython.fm',
    )
    print('   ✓ Event sent to Umami')

    # Test with tracking disabled
    print('2. Disabling tracking...')
    umami.disable()
    print('   Tracking disabled. Now sending event (should not reach Umami)...')

    umami.new_event(
        event_name='This-Should-Not-Be-Sent',
        title='This event should not appear in Umami',
        url='/disabled-test',
        custom_data={'should_not_appear': True},
    )
    print('   ✓ Event call completed but no data sent to Umami')

    # Test page view with tracking disabled
    print('   Sending page view with tracking disabled...')
    umami.new_page_view('Disabled Test Page', '/disabled-page-view', ip_address='127.100.200.1')
    print('   ✓ Page view call completed but no data sent to Umami')

    # Re-enable tracking
    print('3. Re-enabling tracking...')
    umami.enable()
    print('   Tracking re-enabled. Sending final test event...')

    umami.new_event(
        event_name='Tracking-Re-Enabled',
        title='This event should appear in Umami',
        url='/re-enabled-test',
        custom_data={'tracking_restored': True},
    )
    print('   ✓ Event sent to Umami')

    print('\nSending event as if we are a browser user')
    umami.new_page_view('Account Details - Your App', '/account/details', ip_address='127.100.200.1')
else:
    print('No test domain, skipping event creation.')

print('\n=== Summary ===')
print('The new tracking control functions allow you to:')
print('• umami.disable() - Disable tracking for dev/test environments')
print('• umami.enable()  - Re-enable tracking (default state)')
print('• All API calls still work and validate parameters when disabled')
print('• No HTTP requests are made to Umami when tracking is disabled')

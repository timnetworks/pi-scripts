#!/usr/bin/python
import json
import os
import time
import subprocess
from datetime import datetime, timedelta

# Configurable parameters
PING_INTERVAL = 4

# Load data
with open('us.json', 'r') as file:
    data = json.load(file)

# ANSI Colors using tput
colors = {
    'UP': '\033[32m',           # Green
    'DOWN': '\033[31m',         # Red
    'WARNING': '\033[33m',      # Yellow
    'ISSUE': '\033[38;5;214m', # Orange
    'UNKNOWN': '\033[0m',      # Default Terminal Color
    'OTHER': '\033[34m',        # Blue
    'SPECIAL': '\033[36m',      # Teal
    'RESET': '\033[0m'
}

# Convert timestamps and handle missing data
def time_difference(checked_at):
    try:
        checked_time = datetime.strptime(checked_at, '%Y-%m-%dT%H:%M:%S.%fZ')
        delta = datetime.utcnow() - checked_time
        days, hours = divmod(delta.total_seconds(), 86400)
        hours, minutes = divmod(hours, 3600)
        minutes //= 60
        return f'{int(days)}:{int(hours):02}:{int(minutes):02}'
    except (ValueError, TypeError):
        return 'N/A'

# Perform connectivity checks
def check_ping(ip):
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

def check_dns(name):
    try:
        result = subprocess.run(['nslookup', name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

def get_status_color(item):
    if item.get('ip') and check_ping(item.get('ip')):
        return 'UP', colors['UP']
    elif item.get('name') and check_dns(item.get('name')):
        return 'UP', colors['UP']
    else:
        return 'DOWN', colors['DOWN']

def get_terminal_height():
    try:
        return int(subprocess.check_output(['tput', 'lines']).decode().strip()) - 6
    except Exception:
        return 20

def display_data(start_index, history):
    terminal_height = get_terminal_height()

    # Append new data
    end_index = start_index + 12
    rows_to_display = data[start_index:end_index]
    
    for item in rows_to_display:
        status, color = get_status_color(item)
        time_change = time_difference(item.get('checked_at', ''))
        dnssec_status = f"{colors['UP']}YES{colors['RESET']}" if item.get('dnssec', 'false') == 'true' else f"{colors['DOWN']}NO{colors['RESET']}"
        status_symbol = f"{colors['UP']}•{colors['RESET']}" if status == 'UP' else f"{colors['DOWN']}•{colors['RESET']}"
        formatted = (
            f"[ {str(item.get('ip', 'N/A'))[:32]:<32} ] "
            f"[ {str(item.get('name', 'N/A'))[:32]:<32} ] "
            f"[ {str(item.get('as_number', 'N/A'))[:7]:<7} ] "
            f"[ {str(item.get('as_org', 'N/A'))[:15]:<15} ] "
            f"[ {str(item.get('country_id', 'N/A'))[:2]:<2} ] "
            f"[ DNSSEC: {dnssec_status} ] "
            f"[ {time_change:<20} ] "
            f"[ {status_symbol} {status} ]"
        )
        history.append(f"{color}{formatted}{colors['RESET']}")
    
    # Ensure scrolling within bounds
    if len(history) > terminal_height:
        history = history[-terminal_height:]
    
    # Print history without clearing screen
    print('\033[H', end='')
    for line in history:
        print(line)

    # Print bottom footer
#    print('┌' + '─' * 178 + '┐')
    print(f"★ Last Ping: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} | Next Ping in {PING_INTERVAL}s {' ' * 127} ★")
#    print('└' + '─' * 178 + '┘')

    return history

# Main loop
start_index = 0
history = []
while True:
    history = display_data(start_index, history)
    start_index = (start_index + 10) % len(data)
    time.sleep(PING_INTERVAL)


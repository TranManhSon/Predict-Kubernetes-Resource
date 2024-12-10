import os
from datetime import datetime
import subprocess

# schedule: start hour, end hour and number of users
schedule_weekdays = [
    (2, 9, 20),
    (9, 12, 150),
    (12, 15, 280),
    (15, 20, 100),
    (20, 24, 350),
]

schedule_weekend = [
    (0, 10, 30),
    (10, 17, 300),
    (19, 24, 400),
    (0, 2, 150),
    (2, 10, 30),
]

def get_current_users():
    now = datetime.now()
    day_of_week = now.weekday()  # 0 = Monday, 6 = Sunday
    hour = now.hour

    if day_of_week in [5, 6]:  # Saturday, Sunday
        schedule = schedule_weekend
    else:  # Weekdays (Monday to Friday)
        schedule = schedule_weekdays

    for start, end, users in schedule:
        if start <= hour < end:
            return users

    return 20  # Default value if no schedule matches

def set_users_env(users):
    cmd = f"kubectl set env deployment/loadgenerator USERS={users}"
    subprocess.run(cmd, shell=True, check=True)
    print(f"Updated USERS to {users}")

if __name__ == "__main__":
    current_users = get_current_users()
    set_users_env(current_users)

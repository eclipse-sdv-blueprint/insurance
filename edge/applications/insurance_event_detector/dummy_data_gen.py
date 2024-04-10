import random
import time
import uuid
import numpy as np
import json
import logging

# List of vehicle ids
vehicleIds = []

# List of events:
event_type_list = [
    "speeding",  # event_definitions.speeding,
    "massive_speeding",  # event_definitions.massive_speeding,
    "cruise_control_activated",  # event_definitions.cruise_control_activated,
    "tcs_activated",  # event_definitions.tcs_activated,
    "esc_activated",  # event_definitions.esc_activated,
    "performance_mode_activated",  # event_definitions.performance_mode_activated,
    "autobahn",  # event_definitions.autobahn,
    "traffic_jam",  # event_definitions.traffic_jam,
    "no_seatbelt",  # event_definitions.no_seatbelt,
    "harsh_braking",  # event_definitions.harsh_braking,
    "harsh_acceleration",  # event_definitions.harsh_acceleration,
    "harsh_cornering",  # event_definitions.harsh_cornering,
]

# Converting list to numpy array
event_type_array = np.array(event_type_list)

# Generates a list of 10 vehicle ids
for i in range(10):
    vehicleId = str(uuid.uuid4())
    vehicleIds.append(vehicleId)

# Set the initial start date and time
import datetime

start_time = "2024-02-21T13:09:10.288+01:00"

# Add radom number of days to the start_ts
start_ts = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f%z")

logging.info(start_ts)
logging.info(type(start_ts))


def generate_sample_data(vehicleId, start_ts):
    data = []

    # Set the trip Id:
    tripId = str(uuid.uuid4())

    # Generate a random number of days between 1 and 30
    random_days = random.randint(1, 30)

    # Set the initial ts for the first iteration and create a new ramdon ts in the future for the next iterations
    initial_ts = start_ts + datetime.timedelta(days=random_days)
    current_ts = initial_ts

    for i in range(10):

        if i > 1:
            # Generate a random number of minutes between 1 and 10
            random_minutes = random.randint(1, 10)
            current_ts = current_ts + datetime.timedelta(minutes=random_minutes)

        riskEventData = {
            "tripId": tripId,
            "vehicleId": vehicleId,
            "name": np.random.choice(event_type_array),
            "eventId": str(uuid.uuid4()),
            "riskLevel": random.randint(1, 5),
            "timestamp": str(current_ts),
            "eventData": json.dumps(
                {"Vehicle_Speed_Speed": round(random.uniform(130, 150), 2)}
            ),
        }
        data.append(riskEventData)
    return data


# events to be generated
events = []

# Generates a list of events for each vehicle
for vehicleId in vehicleIds:
    for i in range(10):

        event = generate_sample_data(vehicleId, start_ts)
        events.append(event)

events_flat_list = [item for sublist in events for item in sublist]

for e in events_flat_list:
    logging.info(e)

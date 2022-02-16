#!/usr/bin/env python3
import json
import random
import time

rockets = {
    "falcon": {
        "current_pressure_percent": 100,
        "time_passed": 0.0,
        "relative_speed": 0,
        "current_state": "launching"
    },
    "bfr": {
        "current_pressure_percent": 100,
        "time_passed": 0.0,
        "relative_speed": 0,
        "current_state": "launching"
    },
}


def gen_messages(msgs_per_sec=1):
    msgs_so_far = 0
    while True:
        for rocket_id, state in rockets.items():
            print(rocket_id + ":" + json.dumps(state), flush=True)


            new_pressure = state["current_pressure_percent"] * random.uniform(0.9, 0.99)
            time_passed = state["time_passed"] + random.uniform(0.5, 1.9)
            relative_speed = state["relative_speed"]
            if time_passed < 30:
                relative_speed += random.uniform(10, 100)
            else:
                relative_speed *= random.uniform(0.9, 0.99)
            if time_passed < 15:
                current_state = "launching"
            elif time_passed < 30:
                current_state = "leaving_atmosphere"
            elif time_passed < 60:
                current_state = "left_atmosphere"
            elif time_passed < 75:
                current_state = "dispatching_satellite"
            else:
                current_state = "mission_successful"

            rockets[rocket_id] = {
                "current_pressure_percent": new_pressure,
                "time_passed": time_passed,
                "relative_speed": relative_speed,
                "current_state": current_state
            }

            msgs_so_far += 1
            if msgs_so_far >= msgs_per_sec:
                time.sleep(1)


gen_messages(1)

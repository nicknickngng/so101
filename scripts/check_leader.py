"""Check that every servo on the SO101 leader arm responds, then stream live positions.

Usage: uv run scripts/check_leader.py COM4
Move each joint by hand and watch its number change. Ctrl+C to stop.
"""

import sys
import time

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus

port = sys.argv[1] if len(sys.argv) > 1 else "COM4"

names = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
motors = {name: Motor(i, "sts3215", MotorNormMode.RANGE_M100_100) for i, name in enumerate(names, start=1)}
bus = FeetechMotorsBus(port=port, motors=motors)
bus.connect(handshake=False)

try:
    print(f"Pinging motors on {port}:")
    missing = []
    for name, motor in motors.items():
        found = bus.ping(motor.id, num_retry=2) is not None
        print(f"  id {motor.id} {name:<14} {'OK' if found else 'NO RESPONSE'}")
        if not found:
            missing.append(name)
    if missing:
        sys.exit(f"\nMissing: {', '.join(missing)}. Check the cable into that motor and the ones before it.")

    volts = bus.sync_read("Present_Voltage", normalize=False)
    temps = bus.sync_read("Present_Temperature", normalize=False)
    print(f"\nVoltage: {volts['shoulder_pan'] / 10:.1f} V   Max temp: {max(temps.values())} C")

    print("\nRaw positions (0-4095, ~2048 = center). Move the joints; Ctrl+C to stop.\n")
    print("  ".join(f"{n:>13}" for n in names))
    while True:
        pos = bus.sync_read("Present_Position", normalize=False)
        print("  ".join(f"{pos[n]:>13}" for n in names), end="\r")
        time.sleep(0.05)
except KeyboardInterrupt:
    print()
finally:
    bus.disconnect(disable_torque=False)

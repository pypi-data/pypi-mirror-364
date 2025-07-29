import numpy as np


def calculate_friction_torque(effort: np.ndarray, power: np.ndarray, efficiency: float) -> np.ndarray:
    index = 0
    friction_torque = []
    for pow in power:
        if pow >= 0:  # if forward driving
            friction_torque.append(effort[index] * (1 - efficiency))
        elif pow < 0:  # If backdriving
            friction_torque.append(effort[index] * (1 - 1 / efficiency))
        index += 1
    return np.array(friction_torque)

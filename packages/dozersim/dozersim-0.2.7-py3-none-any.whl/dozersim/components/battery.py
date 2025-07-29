from __future__ import annotations
from dataclasses import dataclass
import numpy as np

from dozersim.modelling import Settings
from dozersim.modelling import Model
from dozersim.path import Path
from dozersim.suppliers import BatteryTable
from dozersim import constraints


@dataclass(slots=True)
class BatterySetting(Settings):
    name: str = None
    peak_current: float = None
    voltage: float = None
    capacity: float = None
    mass_spec: float = None
    series: int = None
    parallel: int = None
    SystemPath: Path = None
    desired_life: float = None

    @property
    def mass(self):
        return self.mass_spec

    @property
    def supplier_table(self):
        return BatteryTable


def evaluate_battery(paths: tuple[Path], battery: BatterySetting, model: Model):
    path = paths[0]

    time = path.variables.time
    current_battery = np.zeros(time.shape)
    voltage_battery = np.zeros(time.shape)

    system_path = battery.SystemPath

    if system_path in paths:
        for path in paths:
            if path is not system_path:
                path.check('electrical')
                voltage = path.variables.effort
                voltage_battery = np.maximum(np.array(voltage), voltage_battery)
                system_path.variables.add('current', path.variables.current, model, f"{path.name} Current")
    else:
        raise Exception('The system paths specified in the settings is not found in the paths attached to the items')

    system_path.variables.add('voltage', voltage_battery, model, f"System Voltage")
    if battery.peak_current:
        model.constraints['peak_current'].evaluate(model=model, path=system_path)

    power = system_path.variables.power
    power_pos = np.max([power, np.zeros(power.shape)], axis=0)
    required_energy = np.trapz(power, time) / time[-1]
    life = battery.capacity / required_energy

    model.constraints['battery_life'].evaluate(model, path, life)


class Battery(Model):
    def __init__(self, name: str = 'linkage', settings: BatterySetting = BatterySetting(), eval_fun: callable = evaluate_battery):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
        self.add_constraint(constraints.PathConstraint(name='peak_current', settings=settings, ub='peak_current',
                                                       statistic='absmax', target='flow'))
        self.add_constraint(constraints.CustomConstraint(name='battery_life', settings=settings, lb='desired_life'))

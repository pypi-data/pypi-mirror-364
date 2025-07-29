from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from dozersim.modelling import Settings
from dozersim.modelling import Model
from dozersim.path import Path
from dozersim.results import Load
from dozersim import constraints
from dozersim.components import tools


@dataclass(slots=True)
class BallScrewSettings(Settings):
    name: str = None
    mass: float = None
    pitch: float = None
    nominal_diameter: float = None
    dynamic_load_rating: float = None
    static_load_rating: float = None
    efficiency: float = None
    inertia: float = None

    @property
    def speed_limit(self):
        return 50000 / (self.nominal_diameter * 10e-3)

    @property
    def supplier_table(self):
        return None


def evaluate_ball_screw(paths: list[Path], ballscrew: BallScrewSettings, model: Model):
    """
        Evaluates a ball screw spindle transmission

    Parameters
    ----------
    paths: Path that will be used for all operation on the variables
    ballscrew: Settings of the linkage mechanism
    model: used to leave a parent reference in variables

    Returns
    -------

    """
    path, = paths
    path.check('translational')

    forces_out = path.variables.efforts
    force_out_total = path.variables.torque
    stroke_out = path.variables.displacement - np.min(path.variables.displacement)
    velocity_out = path.variables.flow
    acceleration_out = path.variables.acceleration

    path.transform(var_type='rotational', name="Ball screw input")

    ratio = 2 * np.pi / ballscrew.pitch

    time = path.variables.time
    speed_in = velocity_out * ratio
    acceleration_in = acceleration_out * ratio
    torque_inertia = acceleration_in * ballscrew.inertia
    n_rotations = np.trapz(np.abs(speed_in) * 30 / np.pi, time)
    t_rotation = time[-1]
    rotation_per_hour = n_rotations/t_rotation * 60 * 60
    speed_in_max = np.max(np.abs(speed_in))
    load_cubic_mean = np.sum(np.abs(force_out_total) ** 3 * stroke_out) ** (1 / 3) / np.sum(stroke_out) ** (1 / 3)
    load_static = np.max(np.abs(force_out_total))

    life_rating_10 = (ballscrew.dynamic_load_rating/load_cubic_mean) ** 3
    life_rating_10h = 10e6 / rotation_per_hour * life_rating_10

    path.variables.add('flow', speed_in, model, "Ball screw input")

    for force_out in forces_out:
        path.variables.add('effort',force_out.data / ratio, model, force_out.name)

    friction_torque = tools.calculate_friction_torque(effort=path.variables.effort, power=path.variables.power,
                                                      efficiency=ballscrew.efficiency)

    path.variables.add(target='effort', values=np.array(friction_torque), parent=model, name="Ball screw friction")
    path.variables.add(target='effort', values=torque_inertia, parent=model, name="Ball screw inertia")
    model.constraints['static_force'].evaluate(model=model, path=path)
    model.constraints['max_speed'].evaluate(model=model, path=path)
    path.add_result_object(Load(parent=model, path=path,
                                force_radial=np.full(np.asarray(force_out_total).shape, 0),
                                force_axial=force_out_total))


class BallScrew(Model):

    def __init__(self, name: str = 'ballscrew', settings=BallScrewSettings(), eval_fun=evaluate_ball_screw):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
        self.add_constraint(constraints.PathConstraint(name='static_force', settings=settings, ub='static_load_rating',
                                                       statistic='absmax', target='effort'))
        self.add_constraint(constraints.PathConstraint(name='max_speed', settings=settings, ub='speed_limit',
                                                       statistic='absmax', target='effort'))

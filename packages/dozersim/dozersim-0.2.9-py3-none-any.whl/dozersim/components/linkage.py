from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from dozersim.path import Path
from dozersim.modelling import Model, Settings


@dataclass(slots=True)
class TriangleLinkageSettings(Settings):
    name: str = None
    length_lever: float = None
    length_base: float = None
    initial_angle: float = None
    direction: int = None

    @property
    def supplier_table(self):
        return None


def evaluate_triangle_linkage(paths: list[Path], linkage: TriangleLinkageSettings, model: Model):
    """
        Evaluates a triangular linkage mechanism (a, b, c) assuming that the lever link (b) and settings link (c) are of
        fixed length and the angle between b and c (alpha) is main the output variable, thus link a is of variable
        length and is the (translational) input variable.
        Note the all models are inverse and therefore for from output to input

    Parameters
    ----------
    paths: Path that will be used for all operation on the variables
    linkage: Settings of the linkage mechanism
    model: used to leave a parent reference in variables

    Returns
    -------

    """
    path, = paths
    path.check('rotational')

    angle_out = path.variables.displacement
    torques_out = path.variables.efforts
    path.transform(var_type='translational', name="Linkage translation")

    length_c = linkage.length_base
    length_b = linkage.length_lever

    initial_length = np.sqrt(length_c ** 2 + length_b ** 2 - 2 * length_c * length_b * np.cos(linkage.initial_angle))
    angle_bc = linkage.initial_angle + angle_out*linkage.direction
    length_a = np.sqrt(length_c ** 2 + length_b ** 2 - 2 * length_c * length_b * np.cos(angle_bc))
    angle_ba = np.arccos((length_b ** 2 + length_a ** 2 - length_c ** 2) / (2 * length_a * length_b))
    translation_in = length_a - initial_length
    ratio = np.sin(angle_ba) * length_b

    path.variables.add('displacement', translation_in, model, "Linkage input")
    # paths.add_result_object(analysis.Load())
    for torque_out in torques_out:
        path.variables.add('effort', torque_out.data / ratio, model, torque_out.name)


class TriangleLinkage(Model):

    def __init__(self, name: str = 'linkage', settings=TriangleLinkageSettings(), eval_fun=evaluate_triangle_linkage):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)


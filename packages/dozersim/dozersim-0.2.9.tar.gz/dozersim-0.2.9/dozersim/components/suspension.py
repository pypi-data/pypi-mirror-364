
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from dozersim.path import Path
from dozersim.modelling import Model, Settings
from dozersim.results import Load


@dataclass(slots=True)
class SuspensionSettings(Settings):
    suspension_width: float = None
    target_path: Path = None


def evaluate_suspension(paths: tuple[Path], suspension: SuspensionSettings, model: Model):
    """
        The suspension items simulates a bearing suspension
        that converts a pure moment of the perpendicular paths to a force load on the parallel paths
        It assumes the first paths carries the parallel axis and the remaining two the perpendicular


    """

    moments = []
    if suspension.target_path in paths:
        for path in paths:
            path.check('rotational')
            if path is not suspension.target_path:
                moments.append(path.variables.effort)
    else:
        raise Exception('The _target paths specified in the settings is not found in the paths attached to the items')

    moment = np.linalg.norm(moments, axis=0)

    radial_force = moment / suspension.suspension_width
    axial_force = np.full(np.asarray(moment).shape, 0)

    suspension.target_path.add_result_object(Load(parent=model, path=suspension.target_path,
                                                  force_radial=radial_force, force_axial=axial_force))


class Suspension(Model):
    def __init__(self, name: str = 'suspension', settings=SuspensionSettings(), eval_fun=evaluate_suspension):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)

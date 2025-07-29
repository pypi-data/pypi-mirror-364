from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from dozersim.modelling import Model, Settings
from dozersim.path import Path


@dataclass(slots=True)
class GaussiansFilterSettings(Settings):
    Target: str = None
    Points: list = None
    PeakValue: float = None
    Width: float = None


def evaluate_gaussian_filter(paths: tuple[Path], profile: GaussiansFilterSettings, model: Model):
    path, = paths

    time = path.variables.time
    y_values = []
    width = profile.Width  # 100
    nSamples = len(time)#profile.NumberOfSamples
    nPoints = len(profile.Points)
    kernel = np.arange(nPoints)
    omega = time[-1] * 2 * np.pi
    phis = np.arange(nSamples)/nSamples*omega
    points = np.array(profile.Points)

    for phi in phis:
        q, dq, ddq = gaussians(phi, omega, kernel, width, points)
        y_values.append(q)

    path.variables.add(profile.Target, y_values, model, "Profile")


def gaussians(phi: float, omega: float, kernel_i: np.ndarray, width: float, weights: np.ndarray) -> tuple[float, float, float]:
    """
    % This function implements a discretized version of the adaptive non-linear filter of the adaptive oscillator
    % for non-sinusoidal profiles

     inputs:
       phi: the phase of the signal
       omega: the frequency of the signal (rad/s)
       kernel: ndarray: indeces of the gaussians (e.g. 1:20 for 20 gaussians)
       width: the width of the gaussians
       weights: ndarray the weight factors of the gaussians
     outputs:
       est_pos: the estimated position
       est_vel: the estimated velocity
       est_acc: the estimated acceleration

    REF e.g.
    [1] A. Gams, A. J. Ijspeert, S. Schaal, and J. Lenar?i?, “On-line
    learning and modulation of periodic movements with nonlinear dynamical
    systems,” Auton. Robots, vol. 27, no. 1, pp. 3–23, 2009.
    """
    c_kernel = kernel_i/len(kernel_i)*2*np.pi

    psi = np.exp(width * (np.cos(np.tile(phi, (len(c_kernel), 1)) - c_kernel) - 1))
    dpsi = -psi * width * np.sin(np.tile(phi, (len(c_kernel), 1)) - c_kernel) * omega
    ddpsi = -dpsi * width * np.sin(np.tile(phi, (len(c_kernel), 1))
                                   - c_kernel) * omega - psi * width * np.cos(np.tile(phi, (len(c_kernel), 1))
                                                                              - c_kernel) * omega ** 2
    # -psi*h.*sin(long_phase)*0

    est_pos = np.sum(psi * weights) / np.sum(psi)
    est_vel = np.sum(dpsi * weights) / np.sum(psi)
    est_acc = np.sum(ddpsi * weights) / np.sum(psi)
    return est_pos, est_vel, est_acc



class GaussianFilter(Model):

    def __init__(self, name: str = 'gaussian filter', settings=GaussiansFilterSettings(), eval_fun=evaluate_gaussian_filter):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)

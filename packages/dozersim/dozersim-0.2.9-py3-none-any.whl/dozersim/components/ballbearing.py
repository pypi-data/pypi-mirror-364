from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from numpy import pi
from scipy import interpolate
from dozersim.modelling import Model, Settings
from dozersim.path import Path
from dozersim.results import Load
from dozersim.suppliers import BallBearingTable, GreaseTable
from dozersim import constraints


@dataclass(slots=True)
class BallBearingSettings(Settings):
    name: str = None
    built: str = None
    limitingSpeed: float = None
    boreDiameter: float = None
    outerDiameter: float = None
    width: float = None
    mass: float = None
    staticLoadRating: float = None
    dynamicLoadRating: float = None
    calculationFactor: float = None
    minimumLoadFactor: float = None
    preLoad: float = None
    grease: GreaseSettings = None
    desired_life = None
    ReplenishmentConstant = 6 * 10e-8  # replenishment/starvation constant for grease lubrication
    MovementFrictionCoeff = 0.15  # constant depending on movement


    @property
    def mean_diameter(self) -> float:
        return (self.outerDiameter + self.boreDiameter) / 2

    @property
    def supplier_table(self):
        return BallBearingTable


@dataclass(slots=True)
class GreaseSettings(Settings):
    name: str = None
    base: str = None
    viscosityAt40Deg: float = None
    viscosityAt100Deg: float = None
    operatingTemperature: float = None

    @property
    def Viscosity(self):
        v40 = self.viscosityAt40Deg
        v100 = self.viscosityAt100Deg
        TemperatureKelvin = self.operatingTemperature + 273
        C1 = (np.log10(np.log10(v100 + 0.7)) - np.log10(np.log10(v40 + 0.7))) / (
                    np.log10(40 + 273) - np.log10(100 + 273))
        C2 = np.log10(np.log10(v100 + 0.7)) + C1 * np.log10(100 + 273)
        return 10 ** (10 ** (C2 - C1 * np.log10(TemperatureKelvin))) - 0.7

    @property
    def supplier_table(self):
        return GreaseTable


def evaluate_ball_bearing(paths: list[Path], bearing: BallBearingSettings, model: Model):
    path = paths[0]

    path.check('rotational')
    speed = np.abs(path.variables.flow * 30 / pi)
    time = np.asarray(path.variables.time)

    # Add preload to bearing
    path.add_result_object(Load(parent=model, path=path,
                                force_radial=np.full(time.shape, 0),
                                force_axial=np.full(time.shape, bearing.preLoad)))

    # Extract bearing loads from paths
    loads = path.get_result_object(Load)
    forceRadial = sum(np.array(load.force_radial) for load in loads)
    forceAxial = sum(np.array(load.force_axial) for load in loads)

    grease = bearing.grease
    viscosity = grease.Viscosity
    if 'mineral' in grease.base:
        SlidingFrictionCoeff = 0.05
    elif 'synthetic' in grease.base:
        SlidingFrictionCoeff = 0.04

    calculator = calculator_dict[bearing.built]

    Grr, Gsl, Kz = calculator.GetFrictionVariables(bearing, forceRadial, forceAxial, speed)
    meanDiameter = bearing.mean_diameter
    boreDiameter = bearing.boreDiameter
    outerDiameter = bearing.outerDiameter

    ## Inlet shear heating reduction
    phi_ish = 1 / (1 + 1.84 * 10 ** (-9) * (np.abs(speed) * meanDiameter) ** 1.28 * viscosity ** 0.64)
    phi_ish = np.sign(speed) * phi_ish
    # Kinematic replenishment/starvation reduction factor
    phi_rs = 1 / np.exp(bearing.ReplenishmentConstant * viscosity * np.abs(speed) * (boreDiameter + outerDiameter)
                        * np.sqrt(np.abs(Kz) / (2 * (outerDiameter - boreDiameter))))
    phi_rs = np.sign(speed) * np.sign(Kz) * phi_rs
    MomentRollingFriction = phi_ish * phi_rs * Grr * (viscosity * speed) ** 0.6 * 1e-3

    phi_bl = 1 / (np.exp(2.6 * 10e-8 * (speed * viscosity) ** 1.4 * meanDiameter))

    mu_sl = phi_bl * bearing.MovementFrictionCoeff + (1 - phi_bl) * SlidingFrictionCoeff

    MomentSlidingFriction = Gsl * mu_sl * 10 ** (-3)

    FrictionMoment = (MomentRollingFriction + MomentSlidingFriction) * 2

    FrictionMoment = FrictionMoment * (speed >= 0) - FrictionMoment * (speed < 0)


    # Calculate static and dynamic bearing limits
    MinimumRadialLoad = bearing.minimumLoadFactor * (viscosity * np.mean(np.abs(speed)) / 1000) ** (2 / 3) * (
                meanDiameter / 100) ** 2

    P, P0 = calculator.GetEquivalentLoad(bearing, forceRadial, forceAxial)

    LifeRating10 = (bearing.dynamicLoadRating / P) ** 3
    NumberOfRotations = np.trapz(time, np.abs(speed) / 60)
    RotationTime = time[-1]
    RotationPerHour = NumberOfRotations / RotationTime * 60 * 60
    LifeRating10h = 10 ** 6 / RotationPerHour * LifeRating10

    path.variables.add('effort', FrictionMoment, model, 'Bearing friction')
    # Add contraints here
    model.constraints['bearing_life'].evaluate(model=model, path=path, value=LifeRating10)
    model.constraints['static_load'].evaluate(model=model, path=path, value=P0)


class BallBearingCalculator(ABC):
    @abstractmethod
    def GetFrictionVariables(self, settings: BallBearingSettings, ForceRadial, ForceAxial, Speed) -> tuple:
        pass

    @abstractmethod
    def GetEquivalentLoad(self, settings: BallBearingSettings, forceRadial, forceAxial) -> tuple:
        pass


class DeepGrooveCalculation(BallBearingCalculator):

    def __init__(self) -> None:
        # Creating table for e, X and Y
        AxialFactorTable = [0.175, 0.345, 0.689, 1.03, 1.38, 2.07, 3.45, 5.17, 6.86]
        LoadRatioLimitTable = [0.19, 0.22, 0.26, 0.28, 0.30, 0.34, 0.38, 0.42, 0.44, ]
        XFactorTable = [0.56, 0.56, 0.56, 0.56, 0.56, 0.56, 0.56, 0.56, 0.56]
        YFactorTable = [2.3, 1.99, 1.71, 1.55, 1.45, 1.31, 1.15, 1.04, 1.00]
        self.LoadRatioFunction = interpolate.interp1d(x=AxialFactorTable, y=LoadRatioLimitTable, kind='cubic',
                                                      fill_value='extrapolate')
        self.XFactorFunction = interpolate.interp1d(x=AxialFactorTable, y=XFactorTable, kind='cubic',
                                                    fill_value='extrapolate')
        self.YFactorFunction = interpolate.interp1d(x=AxialFactorTable, y=YFactorTable, kind='cubic',
                                                    fill_value='extrapolate')

    def GetFrictionVariables(self, settings: BallBearingSettings, ForceRadial, ForceAxial, Speed) -> tuple:
        ## Numbers based on 619 and 639 series bearing
        Kz = 3.1  # Geometric constant

        R1 = 4.3e-7  # Geometric constant
        R2 = 1.7  # Geometric constant

        # Sliding friction variable
        S1 = 4.75e-3  # Geometric constant
        S2 = 3.6  # Geometric constant

        if max(ForceAxial) == 0:
            Grr = R1 * settings.mean_diameter ** 1.97 * ForceRadial ** 0.54
            Gsl = S1 * settings.mean_diameter ** -0.26 * ForceRadial ** (5 / 3)
        else:
            F_a = np.abs(ForceAxial)
            alphaF = (24.6 * (F_a / settings.staticLoadRating) ** 0.24) * pi / 180
            Grr = R1 * settings.mean_diameter ** 1.97 * (ForceRadial + R2 / np.sin(alphaF) * F_a) ** 0.54
            Gsl = S1 * settings.mean_diameter ** -0.145 * (
                    ForceRadial ** 5 + S2 * settings.mean_diameter / np.sin(alphaF) * F_a ** 4) ** (1 / 3)

        return (Grr*np.sign(ForceAxial), Gsl*np.sign(ForceAxial), Kz*np.sign(ForceAxial))

    def GetEquivalentLoad(self, settings: BallBearingSettings, forceRadial, forceAxial) -> tuple:
        Fr = np.mean(np.abs(forceRadial))
        Fa = np.mean(np.abs(forceAxial))
        Fr0 = np.max(np.abs(forceRadial))
        Fa0 = np.max(np.abs(forceAxial))

        LoadRatio = Fa / Fr
        AxialFactor = settings.calculationFactor * Fa / settings.staticLoadRating

        if Fr < 0.1:  ## In case of 'pure' axial loads
            if settings.boreDiameter <= 12:
                X0 = 0
                Y0 = 4
            else:
                X0 = 0
                Y0 = 2
        else:
            X0 = 0.5
            Y0 = 0.6

        RatioLimit = self.LoadRatioFunction(AxialFactor)
        if LoadRatio <= RatioLimit:
            EquivalentDynamicLoad = Fr
        else:
            X = self.XFactorFunction(AxialFactor)
            Y = self.YFactorFunction(AxialFactor)
            EquivalentDynamicLoad = X * Fr + Y * Fa

        EquivalentStaticLoad = X0 * Fr0 + Y0 * Fa0
        if EquivalentStaticLoad < Fr0:
            EquivalentStaticLoad = Fr0

        return (EquivalentDynamicLoad, EquivalentStaticLoad)


class AngularContactCalculation(BallBearingCalculator):

    def GetFrictionVariables(self, settings: BallBearingSettings, ForceRadial, ForceAxial, Speed) -> tuple:
        Kz = 4.4  # Geometric constant

        # Rolling friction variable
        R1 = 5.03e-7  # Geometric constant
        R2 = 1.97  # Geometric constant
        R3 = 1.90e-12  # Geometric constant
        Fg = R3 * settings.mean_diameter ** 4 * Speed ** 2

        Grr = R1 * settings.mean_diameter ** 1.97 * (ForceRadial + Fg + R2 * ForceAxial) ** 0.54

        # Sliding friction variable
        S1 = 1.30e-2  # Geometric constant
        S2 = 0.68;  # Geometric constant
        S3 = 1.91e-12  # Geometric constant
        Fg = S3 * settings.mean_diameter ** 4 * Speed ** 2;  #
        Gsl = S1 * settings.mean_diameter ** 0.26 * ((ForceRadial + Fg) ** (4 / 3) + S2 * ForceAxial ** (4 / 3))

        return (Grr, Gsl, Kz)

    def GetEquivalentLoad(self, settings: BallBearingSettings, forceRadial, forceAxial) -> tuple:
        Fr = np.mean(np.abs(forceRadial))
        Fa = np.mean(np.abs(forceAxial))
        Fr0 = np.max(np.abs(forceRadial))
        Fa0 = np.max(np.abs(forceAxial))

        if 'B' in settings.name:  # For 40 deg contact angle (single)
            loadRatioLimit = 1.14
            factorX = 0.35
            factorY2 = 0.57
            factorY0 = 0.26
        elif 'AC' in settings.name:  # for 25 deg contact angle (single)
            loadRatioLimit = 0.68
            factorX = 0.41
            factorY2 = 0.87
            factorY0 = 0.38
        else:
            raise Exception('Bearing name should contain contact angle specification (B or AC)')

        LoadRatio = Fa / Fr
        if LoadRatio <= loadRatioLimit:
            EquivalentDynamicLoad = Fr
        else:
            X = factorX
            Y2 = factorY2
            EquivalentDynamicLoad = X * Fr + Y2 * Fa

        X0 = 0.5
        Y0 = factorY0
        EquivalentStaticLoad = X0 * Fr0 + Y0 * Fa0
        if EquivalentStaticLoad < Fr0:
            EquivalentStaticLoad = Fr0

        return (EquivalentDynamicLoad, EquivalentStaticLoad)


class SuperPrecisionCalculation(BallBearingCalculator):

    def __init__(self) -> None:
        # For contact angle 15 deg
        AxialFactorTable = [0.178, 0.357, 0.714, 1.07, 1.43, 2.14, 3.57, 5.35]
        LoadRatioLimitTable = [0.38, 0.4, 0.43, 0.46, 0.47, 0.50, 0.55, 0.56]
        X2FactorTable = [0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44, 0.44]
        Y2FactorTable = [1.47, 1.40, 1.3, 1.23, 1.19, 1.12, 1.02, 1.00]
        Y0FactorTable = [0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46, 0.46]
        self.LoadRatioFunction = interpolate.interp1d(x=AxialFactorTable, y=LoadRatioLimitTable, kind='cubic')
        self.X2FactorFunction = interpolate.interp1d(x=AxialFactorTable, y=X2FactorTable, kind='cubic')
        self.Y2FactorFunction = interpolate.interp1d(x=AxialFactorTable, y=Y2FactorTable, kind='cubic')
        self.Y0FactorFunction = interpolate.interp1d(x=AxialFactorTable, y=Y0FactorTable, kind='cubic')
        self.FrictionVariableFunction = AngularContactCalculation.GetFrictionVariables

    def GetFrictionVariables(self, settings: BallBearingSettings, ForceRadial, ForceAxial, Speed) -> tuple:
        return self.FrictionVariableFunction(self, settings, ForceRadial, ForceAxial, Speed)

    def GetEquivalentLoad(self, settings: BallBearingSettings, forceRadial, forceAxial) -> tuple:
        Fr = np.mean(np.abs(forceRadial))
        Fa = np.mean(np.abs(forceAxial))
        Fr0 = np.max(np.abs(forceRadial))
        Fa0 = np.max(np.abs(forceAxial))

        LoadRatio = Fa / Fr
        AxialFactor = settings.calculationFactor * Fa / settings.staticLoadRating
        X0 = 0.5
        if 'AC' in settings.name:
            # Contact angle 25 deg
            Y0 = 0.38
            X2 = 0.41
            Y2 = 0.87
            RatioLimit = 0.68
        else:
            # Contact angle 15 deg
            Y0 = self.Y0FactorFunction(AxialFactor)
            X2 = self.X2FactorFunction(AxialFactor)
            Y2 = self.Y2FactorFunction(AxialFactor)
            RatioLimit = self.LoadRatioFunction(AxialFactor)

        if LoadRatio <= RatioLimit:
            EquivalentDynamicLoad = Fr
        else:
            EquivalentDynamicLoad = X2 * Fr + Y2 * Fa

        EquivalentStaticLoad = X0 * Fr0 + Y0 * Fa0
        if EquivalentStaticLoad < Fr0:
            EquivalentStaticLoad = Fr0

        return (EquivalentDynamicLoad, EquivalentStaticLoad)


calculator_dict = {
        'deep groove': DeepGrooveCalculation(),
        'angular contact': AngularContactCalculation(),
        'super precision': SuperPrecisionCalculation()
        }


class BallBearing(Model):
    def __init__(self, name: str = 'ballbearing', settings=BallBearingSettings(), eval_fun=evaluate_ball_bearing):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)
        self.add_constraint(constraints.CustomConstraint(name='static_load', settings=settings, ub='staticLoadRating'))
        self.add_constraint(constraints.CustomConstraint(name='bearing_life', settings=settings, lb='desired_life'))

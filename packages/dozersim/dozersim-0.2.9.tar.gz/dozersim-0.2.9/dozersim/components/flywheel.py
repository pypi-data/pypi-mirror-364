from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from numpy import pi
from sympy import Matrix, sin, cos, symbols, lambdify, diag
from dozersim.path import Path
from dozersim.modelling import Model, Settings
from dozersim.components.materials import Material


@dataclass(slots=True)
class FlywheelSettings(Settings):
    Pressure: float = None
    Temperature: float = None
    AxialGap: float = None
    RadialGap: float = None
    Geometry: GeometryBase = None
    Material: Material = None
    GasConstant: float = 8.315  # [J/mol K] Universal gas constant
    MolecularDiameter: float = 3.68e-10  # [m] @20degC Effective molecular diameter
    BoltzConstant: float = 1.38e-23  # Boltzman constant
    AirMass: float = 4.782e-26  # [kg] Mass Air
    MolarMass: float = 0.0288  # [kg/mol] Air Molar mass
    EOMs: tuple = None

    def __post_init__(self):
        self.EOMs = get_eoms()


    @property
    def mass(self):
        return self.Geometry.calculate_mass(self.Material)

    @property
    def inertia(self):
        return self.Geometry.calculate_inertia(self.Material)


@dataclass(slots=True)
class GeometryBase(Settings):

    def calculate_inertia(self, material: Material) -> tuple:
        pass

    def calculate_mass(self, material: Material) -> tuple:
        pass


@dataclass(slots=True)
class SolidDiskGeometry(GeometryBase):
    Diameter: float = None
    Width: float = None

    def calculate_inertia(self, material: Material) -> tuple:
        Radius = self.Diameter / 2
        Mass, = self.calculate_mass(material)
        InertiaS = 1 / 2 * Mass * Radius ** 2
        InertiaTG = 1 / 12 * Mass * (3 * Radius ** 2 + self.Width ** 2)
        return InertiaS, InertiaTG

    def calculate_mass(self, material: Material) -> tuple:
        MaterialDensity = material.density
        Radius = self.Diameter / 2
        return MaterialDensity * (pi * self.Width * Radius),


@dataclass(slots=True)
class RimAndWebGeometry(GeometryBase):
    Diameter: float = None
    Width: float = None
    InnerDiameter: float = None
    WebWidth: float = None

    def calculate_inertia(self, material: Material) -> tuple:
        OuterRadius = self.Diameter / 2
        InnerRadius = self.InnerDiameter / 2

        TotalMass, RimMass, WebMass = self.calculate_mass(material)

        RimInertiaS = 1 / 2 * RimMass * (OuterRadius ** 2 + InnerRadius ** 2)
        RimInertiaTG = 1 / 12 * RimMass * (3 * (OuterRadius ** 2 + InnerRadius ** 2) + self.Width ** 2)
        WebInertiaS = 1 / 2 * WebMass * InnerRadius ** 2
        WebInertiaTG = 1 / 12 * WebMass * (3 * OuterRadius ** 2 + self.WebWidth ** 2)

        InertiaTG = WebInertiaTG + RimInertiaTG
        InertiaS = WebInertiaS + RimInertiaS  # wheel intertia w.r.t. the spinning axis

        return InertiaS, InertiaTG

    def calculate_mass(self, material: Material) -> tuple:
        MaterialDensity = material.density

        OuterRadius = self.Diameter / 2
        InnerRadius = self.InnerDiameter / 2

        RimVolume = pi * (OuterRadius ** 2 - InnerRadius ** 2) * self.WebWidth
        RimMass = RimVolume * MaterialDensity

        WebVolume = self.WebWidth * pi * InnerRadius ** 2
        WebMass = WebVolume * MaterialDensity

        TotalMass = WebMass + RimMass
        return TotalMass, RimMass, WebMass


def evaluate_flywheel(paths: tuple[Path, Path, Path], flywheel: FlywheelSettings, model: Model):

    WheelPath, FramePath, GimbalPath = paths

    MomentsSTG, MomentsUVW, VelocitiesSTG = flywheel.EOMs

    WheelVelocity = WheelPath.variables.velocity
    WheelAcceleration = WheelPath.variables.acceleration
    FrameVelocity = FramePath.variables.velocity
    FrameAcceleration = FramePath.variables.acceleration
    GimbalAngle = GimbalPath.variables.displacement
    GimbalVelocity = GimbalPath.variables.velocity
    GimbalAcceleration = GimbalPath.variables.acceleration
    InertiaS, InertiaTG = flywheel.Geometry.calculate_inertia(flywheel.Material)

    velocitySTG = VelocitiesSTG(WheelVelocity, WheelAcceleration, FrameVelocity, FrameAcceleration, GimbalAngle,
                                     GimbalVelocity, GimbalAcceleration, InertiaS, InertiaTG)
    momentsSTG = MomentsSTG(WheelVelocity, WheelAcceleration, FrameVelocity, FrameAcceleration, GimbalAngle,
                                 GimbalVelocity, GimbalAcceleration, InertiaS, InertiaTG)
    momentsUVW = MomentsUVW(WheelVelocity, WheelAcceleration, FrameVelocity, FrameAcceleration, GimbalAngle,
                                 GimbalVelocity, GimbalAcceleration, InertiaS, InertiaTG)

    WheelPath.variables.add('effort', momentsSTG[0][0], model, 'FlywheelSettings moments')
    FramePath.variables.add('effort', momentsSTG[1][0], model, 'FlywheelSettings moments')
    GimbalPath.variables.add('effort', momentsSTG[2][0], model, 'FlywheelSettings moments')

    OuterRadius = flywheel.Geometry.Diameter / 2
    Pressure_Pa = flywheel.Pressure * 1e5  # convert bar to pascal
    Temperature_degK = flywheel.Temperature + 273.15  # convert to kelvin

    OuterSurfaceRadius = flywheel.RadialGap + OuterRadius
    AirDensity = Pressure_Pa / (flywheel.GasConstant * Temperature_degK) * flywheel.MolarMass

    DynamicViscosity = (flywheel.BoltzConstant * flywheel.AirMass * Temperature_degK) ** 0.5 / (
                flywheel.MolecularDiameter ** 2 * pi ** (3 / 2))
    KinematicViscosity = DynamicViscosity / AirDensity
    GapRatio = flywheel.AxialGap / OuterRadius

    RadialMoment = []
    AxialMoment = []

    for velocity in WheelVelocity:
        if velocity == 0:
            Cm_a = 0
            Cm_r = 0
        else:
            ## Reynolds Number
            Re = AirDensity * OuterRadius ** 2 * velocity / DynamicViscosity
            Re_g = AirDensity * velocity * OuterRadius * flywheel.RadialGap / DynamicViscosity

            ## Axial Component
            if Re < 3e5:  # Laminar Flow
                delta = 5.5 * (KinematicViscosity / velocity) ** (0.5)
                #         delta = (nu/omega)**(0.5);
                if flywheel.AxialGap < delta:  # Merged Boundary Layers
                    # Regime 1
                    Cm_a = 2 * pi / (GapRatio * Re)
                #             disp('Regime 1')
                else:  # Separate Boundary Layers
                    # Regime 2
                    Cm_a = 3.7 * GapRatio ** (0.1) * Re ** (-0.5)
            #             disp('Regime 2')
            else:  # Turbulent
                #          delta = 0.526*ro*Re**(-0.2);
                delta = AirDensity ** (3 / 5) * (KinematicViscosity / velocity) ** (1 / 5)
                if flywheel.AxialGap < delta:  # Merged Boundary Layers
                    # Regime 3
                    Cm_a = 2 * 0.040 * GapRatio ** (-1 / 6) * Re ** (
                        -0.25)  # For Regime type 3 (Turbulent flow with merged boundary layers -> Small clearance)
                #             disp('Regime 3')
                else:  # Separate Boundary Layers
                    # Regime 4
                    Cm_a = 0.0102 * GapRatio ** (0.1) * Re ** (-1 / 5)
            #             disp('Regime 4')

            ## Radial Component
            if Re_g < 64:  # Laminar
                Cm_r = 8 * OuterSurfaceRadius ** 2 / Re_g * OuterRadius * (OuterRadius + OuterSurfaceRadius)
            elif (Re_g >= 64) and (Re_g < 500):  # Transitional flow
                Cm_r = 2 * (flywheel.RadialGap / OuterRadius) ** 0.3 * Re_g ** (-0.6)
            #         disp('Laminar')
            elif (Re_g >= 500) and (Re_g < 1e4):  # Transitional flow
                Cm_r = 1.03 * (flywheel.RadialGap / OuterRadius) ** 0.3 * Re_g ** -0.5
            #         disp('Turbulent transition')
            else:
                Cm_r = 0.065 * (flywheel.RadialGap / OuterRadius) ** 0.3 * Re_g ** -0.2
            #         disp('Turbulent')

        RadialMoment.append(0.5 * pi * AirDensity * velocity ** 2 * OuterRadius ** 4 * flywheel.Geometry.Width * Cm_r)
        AxialMoment.append(AirDensity * velocity ** 2 * OuterRadius ** 5 * Cm_a)

    Moment = np.array(RadialMoment) + np.array(AxialMoment)
    Moment = Moment * (WheelVelocity >= 0) - Moment * (WheelVelocity < 0)

    WheelPath.variables.add('effort', Moment, model, "Air friction")


def get_eoms():
    '''Symbolic equations of motion'''
    InertiaS, InertiaTG = symbols('InertiaS,InertiaTG', real=True)
    WheelAngle, WheelVelocity, WheelAcceleration = symbols('WheelAngle,WheelVelocity,WheelAcceleration', real=True)
    FrameAngle, FrameVelocity, FrameAcceleration = symbols('FrameAngle,FrameVelocity,FrameAcceleration', real=True)
    GimbalAngle, GimbalVelocity, GimbalAcceleration = symbols('GimbalAngle,GimbalVelocity,GimbalAcceleration',
                                                              real=True)

    GeneralizedAngles = Matrix([WheelAngle, FrameAngle, GimbalAngle])
    GeneralizedVelocities = Matrix([WheelVelocity, FrameVelocity, GimbalVelocity])
    GeneralizedAccelerations = Matrix([WheelAcceleration, FrameAcceleration, GimbalAcceleration])

    WheelInertia = diag(InertiaS, InertiaTG, InertiaTG)

    JacobianSTG = Matrix([[Matrix([0, 0, 0]), rotation_z(GimbalAngle) * Matrix([0, 1, 0]), Matrix([0, 0, 1])]])
    JacobianWheel = Matrix([[Matrix([1, 0, 0]), rotation_z(GimbalAngle) * Matrix([0, 1, 0]), Matrix([0, 0, 1])]])

    VelocitiesSTG: Matrix = JacobianSTG * GeneralizedVelocities
    VelocitiesWheel: Matrix = JacobianWheel * GeneralizedVelocities

    JacobianVelocities = VelocitiesWheel.jacobian(GeneralizedAngles)

    AccelerationsWheel = JacobianWheel * GeneralizedAccelerations + JacobianVelocities * GeneralizedVelocities

    MomentsSTG = WheelInertia * AccelerationsWheel + tilde(VelocitiesSTG) * WheelInertia * VelocitiesWheel
    MomentsSTG[0] = InertiaS * WheelAcceleration  # Overwrite wheel-axis moment to remove artifacts
    MomentsUVW = rotation_z(GimbalAngle) * MomentsSTG

    Variables = (
    WheelVelocity, WheelAcceleration, FrameVelocity, FrameAcceleration, GimbalAngle, GimbalVelocity, GimbalAcceleration,
    InertiaS, InertiaTG)
    MomentsSTG = lambdify(Variables, MomentsSTG, 'numpy')
    VelocitiesSTG = lambdify(Variables, VelocitiesSTG, 'numpy')
    MomentsUVW = lambdify(Variables, MomentsUVW, 'numpy')

    return MomentsSTG, MomentsUVW, VelocitiesSTG


def rotation_x(phi):
    """
    RX the rotation matrix for the x-axis
    Parameters
    ----------
    phi

    Returns
    -------
    This function uses the angle phi and returns a 3X3 rotation matrix
    """
    return Matrix([[1, 0, 0], [0, cos(phi), -sin(phi)], [0, sin(phi), cos(phi)]])


def rotation_y(phi):
    """
    RY the rotation matrix for the y-axis
    Parameters
    ----------
    phi

    Returns
    -------
    This function uses the angle phi and returns a 3X3 rotation matrix
    """
    return Matrix([[cos(phi), 0, sin(phi)], [0, 1, 0], [-sin(phi), 0, cos(phi)]])


def rotation_z(phi):
    """
    RZ the rotation matrix for the z-axis
    Parameters
    ----------
    phi

    Returns
    -------
    This function uses the angle phi and returns a 3X3 rotation matrix
    """
    return Matrix([[cos(phi), -sin(phi), 0], [sin(phi), cos(phi), 0], [0, 0, 1]])


def tilde(w):
    w1 = w[0]
    w2 = w[1]
    w3 = w[2]

    return Matrix([[0, -w3, w2], [w3, 0, -w1], [-w2, w1, 0]])


class FlyWheel(Model):
    def __init__(self, name: str = 'flywheel', settings=FlywheelSettings(), eval_fun=evaluate_flywheel):
        super().__init__(name=name, settings=settings, eval_fun=eval_fun)

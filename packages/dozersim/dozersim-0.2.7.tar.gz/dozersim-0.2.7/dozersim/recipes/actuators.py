from dozersim.components.spring import Spring
from dozersim.components.gearbox import Gearbox
from dozersim.components.electricmotor import ElectricMotor
from dozersim.components.servodrive import ServoDrive
from dozersim.components.ballbearing import BallBearing
from dozersim.modelling import Model


def create_actuator() -> list[Model]:
    return [Spring(),
            Gearbox(),
            ElectricMotor(),
            ServoDrive(),
            ]

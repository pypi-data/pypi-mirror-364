from __future__ import annotations
from sqlalchemy import Column, String, Integer, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, Query
from sqlalchemy.orm import sessionmaker
import os
import pathlib
file_path = pathlib.Path(__file__)
db_path = file_path.parent.absolute().joinpath('../data/supplier_data.db')

if db_path:
    engine = create_engine('sqlite:///'+str(db_path))
    Session = sessionmaker(bind=engine)
    session = Session()
    Base = declarative_base()
else:
    raise Exception('The supplier database was not found')


class BatteryTable(Base):
    """docstring for ElectricMotorSettings.Objects"""
    __tablename__ = 'batteryspecification'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    capacity = Column(Float)
    peak_current = Column(Float)
    voltage = Column(Float)
    mass_spec = Column(Float)


class MotorTable(Base):
    """docstring for ElectricMotorSettings.Objects"""
    __tablename__ = 'motorspecification'

    id = Column(Integer, primary_key=True)
    built = Column(String)
    name = Column(String)
    windingResistance = Column(Float)
    speedConstant = Column(Float)
    maxSpeed = Column(Float)
    ratedPower = Column(Float)
    peakPower = Column(Float)
    ratedCurrent = Column(Float)
    peakCurrent = Column(Float)
    windingVoltage = Column(Float)
    rotorInertia = Column(Float)
    mass = Column(Float)
    motorLength = Column(Float)
    motorDiameter = Column(Float)

    
class BallBearingTable(Base):
    __tablename__ = 'bearingspecifications'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    built = Column(String)
    limitingSpeed = Column(Float)
    boreDiameter = Column(Float)
    outerDiameter = Column(Float)
    width = Column(Float)
    mass = Column(Float)
    staticLoadRating = Column(Float)
    dynamicLoadRating = Column(Float)
    minimumLoadFactor = Column(Float)
    loadRatioLimit = Column(Float)
    factorX = Column(Float)
    factorY0 = Column(Float)
    factorY2 = Column(Float)   


class GreaseTable(Base):
    __tablename__ = 'greasespecifications'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    oilType = Column(String)
    viscosityAt40Deg = Column(Float)
    viscosityAt100Deg = Column(Float)


from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Material:
    name: str = None
    density: float = None
    youngsModulus: float = None
    yieldStrength: float = None
    poissonsRatio: float = None
    contactStrength: float = None
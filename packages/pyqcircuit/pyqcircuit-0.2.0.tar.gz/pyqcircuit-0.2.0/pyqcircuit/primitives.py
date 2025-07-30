from dataclasses import dataclass
from typing import Tuple, Union

Color = Union[
    str,
    Tuple[float, float, float],
    Tuple[float, float, float, float],
]


@dataclass(kw_only=True)
class PrimitiveBase:
    layer: int = 0


@dataclass
class Line(PrimitiveBase):
    x1: float
    y1: float
    x2: float
    y2: float
    width: float = 1.0
    color: Color = "black"


@dataclass
class Box(PrimitiveBase):
    x: float
    y: float
    width: float
    height: float
    face: Color = "#e0e0e0"
    edge: Color = "black"
    lw: float = 1.0


@dataclass
class Circle(PrimitiveBase):
    x: float
    y: float
    r: float
    fill: bool
    color: Color = "black"
    lw: float = 1.0


@dataclass
class Arc(PrimitiveBase):
    x: float
    y: float
    width: float
    height: float
    theta1: float
    theta2: float
    lw: float = 1.0
    color: Color = "black"


@dataclass
class Text(PrimitiveBase):
    x: float
    y: float
    s: str
    size: int = 10
    color: Color = "black"
    ha: str = "center"
    va: str = "center"


Primitive = Union[Line, Box, Circle, Arc, Text]

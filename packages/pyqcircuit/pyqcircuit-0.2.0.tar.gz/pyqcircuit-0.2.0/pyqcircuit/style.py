from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional
from pyqcircuit.primitives import Color


@dataclass
class GateStyle:
    facecolor: Optional[Color] = None
    edgecolor: Optional[Color] = None
    textcolor: Optional[Color] = None
    linewidth: Optional[float] = None
    fontsize: Optional[int] = None

    def merged(self, other: GateStyle) -> GateStyle:
        data = asdict(self)
        for key, val in asdict(other).items():
            if val is not None:
                data[key] = val
        return GateStyle(**data)


# Library‑wide defaults (can be replaced by user themes later).
default_gate_style = GateStyle()

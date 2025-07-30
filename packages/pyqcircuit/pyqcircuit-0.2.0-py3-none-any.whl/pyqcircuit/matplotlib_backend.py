from pyqcircuit.primitives import Line, Box, Circle, Arc, Text, Primitive
from pyqcircuit.graphics_target import GraphicsTarget

import matplotlib.pyplot as _plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Circle as MPLCircle, Arc as MPLArc


class MatplotlibTarget(GraphicsTarget):
    """Translate primitives into Matplotlib artists."""

    def __init__(self, columns: int, rows: int, figsize_factor: float = 0.8):
        size = ((columns + 2) * figsize_factor, (rows + 1) * figsize_factor)
        self.rows = rows
        self.cols = columns
        self.fig, self.ax = _plt.subplots(figsize=size)

    # ------------------------------------------------------------------
    def add(self, obj: Primitive) -> None:
        match obj:
            case Line(x1, y1, x2, y2, width, color):
                self.ax.add_line(
                    Line2D([x1, x2], [y1, y2], lw=width, color=color, zorder=obj.layer)
                )
            case Box(x, y, width, height, face, edge, lw):
                self.ax.add_patch(
                    Rectangle(
                        (x, y),
                        width,
                        height,
                        facecolor=face,
                        edgecolor=edge,
                        lw=lw,
                        zorder=obj.layer,
                    )
                )
            case Circle(x, y, r, fill, color, lw):
                self.ax.add_patch(
                    MPLCircle((x, y), r, fill=fill, color=color, lw=lw, zorder=obj.layer)
                )
            case Arc(x, y, width, height, theta1, theta2, lw, color):
                self.ax.add_patch(
                    MPLArc(
                        (x, y),
                        width,
                        height,
                        theta1=theta1,
                        theta2=theta2,
                        lw=lw,
                        color=color,
                        zorder=obj.layer,
                    )
                )
            case Text(x, y, s, size, color, ha, va):
                self.ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va, zorder=obj.layer)
            case _:
                raise TypeError(f"Unknown primitive {obj}")

    # ------------------------------------------------------------------
    def finalize(self):
        self.ax.set_axis_off()
        self.ax.set_aspect("equal")
        _plt.tight_layout()
        self.ax.set_xlim(-1, self.cols + 1.5)
        self.ax.set_ylim(-(self.rows - 1) - 1, 0.5)
        return self.fig, self.ax

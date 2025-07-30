import abc
from pyqcircuit.primitives import Primitive


class GraphicsTarget(abc.ABC):
    """Backend‑independent interface that receives drawing primitives."""

    @abc.abstractmethod
    def add(self, obj: Primitive) -> None:
        raise NotImplementedError

    # Back‑ends may override this to return (fig, ax) or similar.
    def finalize(self):
        return None

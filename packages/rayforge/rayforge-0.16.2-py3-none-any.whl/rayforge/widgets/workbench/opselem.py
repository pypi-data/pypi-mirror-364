import logging
import cairo
from typing import Optional
from ...config import config
from ...opsencoder.cairoencoder import CairoEncoder
from ...models.ops import Ops
from ...models.workpiece import WorkPiece
from .surfaceelem import SurfaceElement


logger = logging.getLogger(__name__)

OPS_MARGIN_PX = 10


class WorkPieceOpsElement(SurfaceElement):
    """
    Displays the generated Ops for a single WorkPiece.
    """

    def __init__(
        self, workpiece: WorkPiece, show_travel_moves: bool = False, **kwargs
    ):
        if not workpiece.size:
            raise AttributeError(
                f"attempt to add workpiece {workpiece.name} with no size"
            )
        super().__init__(
            0,
            0,
            0,
            0,
            data=workpiece,
            selectable=False,
            buffered=True,
            **kwargs,
        )
        self._accumulated_ops = Ops()
        self._ops_generation_id = -1
        self.show_travel_moves = show_travel_moves

        # Connect to specific signals instead of the generic 'changed' signal.
        workpiece.pos_changed.connect(self.allocate)
        workpiece.size_changed.connect(self.allocate)
        workpiece.angle_changed.connect(self.allocate)

    def allocate(self, force: bool = False):
        """
        Updates position and size. Triggers a re-render. If the workpiece's
        size in millimeters changes, the current ops are cleared. A simple
        canvas zoom will not clear the ops.
        """
        if not self.canvas or not self.parent:
            return

        x_mm, y_mm = self.data.pos or (0, 0)
        current_mm_size = self.data.get_current_size()

        if not current_mm_size:
            self.width, self.height = 0, 0
            self.width_mm, self.height_mm = 0.0, 0.0
            self.clear_ops()
            return

        # Check if the fundamental size in mm has changed by comparing against
        # the values stored in the parent class.
        mm_size_changed = (self.width_mm, self.height_mm) != current_mm_size

        px_per_mm_x = self.canvas.pixels_per_mm_x or 1
        px_per_mm_y = self.canvas.pixels_per_mm_y or 1
        width_px = round(current_mm_size[0] * px_per_mm_x)
        height_px = round(current_mm_size[1] * px_per_mm_y)

        new_width = width_px + 2 * OPS_MARGIN_PX
        new_height = height_px + 2 * OPS_MARGIN_PX
        pixel_size_changed = (
            self.width != new_width or self.height != new_height
        )

        x_mm_tl, y_mm_tl = x_mm, y_mm + current_mm_size[1]

        content_height_px = self.canvas.root.height
        x_px = x_mm_tl * px_per_mm_x
        y_px = content_height_px - y_mm_tl * px_per_mm_y

        self.set_pos(round(x_px) - OPS_MARGIN_PX, round(y_px) - OPS_MARGIN_PX)
        self.set_angle(self.data.angle)

        if not pixel_size_changed and not force:
            return

        # If the workpiece's actual mm size changed, the existing ops are
        # invalid and must be cleared. This will NOT trigger on a canvas zoom.
        if mm_size_changed:
            self.clear_ops()

        # Update the state in the parent class.
        self.width_mm, self.height_mm = current_mm_size
        self.width, self.height = new_width, new_height
        super().allocate(force)

    def clear_ops(self, generation_id: Optional[int] = None):
        """Clears ops. If a generation_id is provided, it is stored."""
        self._accumulated_ops = Ops()
        if generation_id is not None:
            self._ops_generation_id = generation_id
        self.clear_surface()
        self.trigger_update()

    def set_ops(self, ops: Optional[Ops], generation_id: Optional[int] = None):
        """Replaces all current ops, but only if generation_id is current."""
        if (
            generation_id is not None
            and generation_id < self._ops_generation_id
        ):
            logger.debug(
                f"Ignoring stale final ops (gen {generation_id}) for "
                f"'{self.data.name}', current is {self._ops_generation_id}"
            )
            return
        if generation_id is not None:
            self._ops_generation_id = generation_id
        self._accumulated_ops = ops or Ops()
        self.trigger_update()

    def add_ops(self, ops_chunk: Ops, generation_id: Optional[int] = None):
        """Adds a chunk of ops, but only if the generation_id is not stale."""
        if not ops_chunk:
            return
        # Only add chunk if it belongs to the current generation.
        if (
            generation_id is not None
            and generation_id != self._ops_generation_id
        ):
            logger.debug(
                f"Ignoring stale ops chunk (gen {generation_id}) for "
                f"'{self.data.name}', current is {self._ops_generation_id}"
            )
            return
        self._accumulated_ops += ops_chunk
        self.trigger_update()

    def set_show_travel_moves(self, show: bool):
        """
        Sets the travel move visibility and triggers a re-render if changed.
        """
        if self.show_travel_moves != show:
            self.show_travel_moves = show
            self.trigger_update()

    def render_to_surface(
        self, width: int, height: int
    ) -> Optional[cairo.ImageSurface]:
        """
        Renders the accumulated ops to a new surface. This runs in a
        background thread.
        """
        if width <= 0 or height <= 0:
            return None

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        ctx = cairo.Context(surface)
        ctx.set_source_rgba(*self.background)
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.paint()

        render_ops = self._accumulated_ops.copy()
        if not render_ops or not self.canvas:
            return surface

        px_per_mm_x = self.canvas.pixels_per_mm_x or 1
        px_per_mm_y = self.canvas.pixels_per_mm_y or 1
        pixels_per_mm = px_per_mm_x, px_per_mm_y

        margin_mm_x = OPS_MARGIN_PX / px_per_mm_x
        margin_mm_y = OPS_MARGIN_PX / px_per_mm_y
        render_ops.translate(margin_mm_x, margin_mm_y)

        encoder = CairoEncoder()
        encoder.encode(
            render_ops,
            config.machine,
            ctx,
            pixels_per_mm,
            show_travel_moves=self.show_travel_moves,
        )
        return surface

import logging
from typing import Optional, cast
from ...models.workpiece import WorkPiece
from ...models.workplan import WorkStep
from ...models.ops import Ops
from ..canvas import CanvasElement
from .opselem import WorkPieceOpsElement


logger = logging.getLogger(__name__)


class WorkStepElement(CanvasElement):
    """
    WorkStepElements display the result of a WorkStep on the
    WorkSurface. The output represents the laser path.
    """

    def __init__(
        self,
        workstep,
        x,
        y,
        width,
        height,
        show_travel_moves: bool = False,
        **kwargs,
    ):
        """
        Initializes a WorkStepElement with pixel dimensions.

        Args:
            workstep: The WorkStep data object.
            x: The x-coordinate (pixel) relative to the parent.
            y: The y-coordinate (pixel) relative to the parent.
            width: The width (pixel).
            height: The height (pixel).
            **kwargs: Additional keyword arguments for CanvasElement.
        """
        super().__init__(
            x, y, width, height, data=workstep, selectable=False, **kwargs
        )
        self.show_travel_moves = show_travel_moves
        workstep.changed.connect(self._on_workstep_changed)
        # Connect to the actual signals from WorkStep's async pipeline
        workstep.ops_generation_starting.connect(
            self._on_ops_generation_starting
        )
        # Note: There is no explicit 'cleared' signal in the async pipeline,
        # starting implies clearing for the UI representation.
        workstep.ops_chunk_available.connect(self._on_ops_chunk_available)
        workstep.ops_generation_finished.connect(
            self._on_ops_generation_finished
        )
        # Workpiece elements are added dynamically when ops chunks arrive

    def add_workpiece(self, workpiece) -> WorkPieceOpsElement:
        """
        Adds a WorkPieceOpsElement for the given workpiece if it doesn't exist.
        Returns the existing or newly created element.
        """
        elem = self.find_by_data(workpiece)
        if elem:
            elem.mark_dirty()
            return cast(WorkPieceOpsElement, elem)

        elem = WorkPieceOpsElement(
            workpiece,
            show_travel_moves=self.show_travel_moves,
            canvas=self.canvas,
            parent=self,
        )
        self.add(elem)
        return elem

    def set_show_travel_moves(self, show: bool):
        """Sets travel move visibility for all child Ops elements."""
        if self.show_travel_moves == show:
            return
        self.show_travel_moves = show
        for child in self.children:
            if isinstance(child, WorkPieceOpsElement):
                child.set_show_travel_moves(show)

    def _on_workstep_changed(self, step: WorkStep):
        # This signal is for changes to the WorkStep itself (e.g., visibility)
        # not changes to its workpieces or ops.
        # Workpiece additions/removals are handled by the ops generation
        # signals.
        # We just need to update visibility and redraw.
        assert self.canvas, (
            "Received ops_start, but element was not added to canvas"
        )
        self.set_visible(step.visible)
        if self.canvas:
            self.canvas.queue_draw()

    def _find_or_add_workpiece_elem(
        self, workpiece: WorkPiece
    ) -> WorkPieceOpsElement:
        """Finds the element for a workpiece, creating if necessary."""
        elem = cast(
            Optional[WorkPieceOpsElement], self.find_by_data(workpiece)
        )
        if not elem:
            logger.debug(f"Adding workpiece to step: {workpiece.name}")
            elem = self.add_workpiece(workpiece)
        return elem

    def _on_ops_generation_starting(
        self,
        sender: WorkStep,
        workpiece: WorkPiece,
        generation_id: int,
    ):
        """Called before ops generation starts for a workpiece."""
        logger.debug(
            f"WorkStepElem '{sender.name}': Received ops_generation_starting "
            f"for {workpiece.name}"
        )
        assert self.canvas, (
            "Received ops_start, but element was not added to canvas"
        )

        # If the workpiece is no longer part of the workstep, remove its
        # ops element.
        if workpiece not in sender.workpieces():
            elem = self.find_by_data(workpiece)
            if elem:
                elem.remove()
            return

        elem = self._find_or_add_workpiece_elem(workpiece)
        elem.clear_ops(generation_id=generation_id)

    def _on_ops_chunk_available(
        self,
        sender: WorkStep,
        workpiece: WorkPiece,
        chunk: Ops,
        generation_id: int,
    ):
        """Called when a chunk of ops is available for a workpiece."""
        logger.debug(
            f"WorkStepElem '{sender.name}': Received ops_chunk_available for "
            f"{workpiece.name} (chunk size: {len(chunk)}, pos={workpiece.pos})"
        )
        assert self.canvas, (
            "Received update, but element was not added to canvas"
        )

        # If the workpiece is no longer part of the workstep, remove its
        # ops element.
        if workpiece not in sender.workpieces():
            elem = self.find_by_data(workpiece)
            if elem:
                elem.remove()
            return

        elem = self._find_or_add_workpiece_elem(workpiece)
        elem.add_ops(chunk, generation_id=generation_id)

    def _on_ops_generation_finished(
        self,
        sender: WorkStep,
        workpiece: WorkPiece,
        generation_id: int,
    ):
        """
        Called when ops generation is finished. This handler ensures a final,
        guaranteed redraw of the element's complete state, ignoring stale
        results.
        """
        assert self.canvas, (
            "Received ops_finished, but element was not added to canvas"
        )

        # If the workpiece is no longer part of this workstep, its element
        # should be removed.
        if workpiece not in sender.workpieces():
            elem = self.find_by_data(workpiece)
            if elem:
                elem.remove()
            return

        elem = self._find_or_add_workpiece_elem(workpiece)
        final_ops = sender.get_ops(workpiece)
        elem.set_ops(final_ops, generation_id=generation_id)

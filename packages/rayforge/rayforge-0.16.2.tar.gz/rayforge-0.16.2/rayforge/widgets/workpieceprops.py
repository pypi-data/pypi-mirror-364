import logging
from gi.repository import Gtk, Adw, Gdk
from typing import Optional
from ..config import config
from ..models.workpiece import WorkPiece
from ..util.adwfix import get_spinrow_float


css = """
.workpiece-properties .boxed-list {
    margin: 0 0 12px 0;
    box-shadow: 0 8px 8px rgba(0, 0, 0, 0.1);
}
"""


logger = logging.getLogger(__name__)


class WorkpiecePropertiesWidget(Adw.PreferencesGroup):
    def __init__(self, workpiece: Optional[WorkPiece], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_css_class("workpiece-properties")
        self.apply_css()
        self.workpiece: Optional[WorkPiece] = workpiece
        self._in_update = False
        self.set_title(_("Workpiece Properties"))

        # X Position Entry
        self.x_row = Adw.SpinRow(
            title=_("X Position"),
            adjustment=Gtk.Adjustment.new(0, -10000, 10000, 1.0, 1, 0),
        )
        self.x_row.set_digits(2)
        self.x_row.connect("notify::value", self._on_x_changed)
        self.add(self.x_row)

        # Y Position Entry
        self.y_row = Adw.SpinRow(
            title=_("Y Position"),
            adjustment=Gtk.Adjustment.new(0, -10000, 10000, 1.0, 1, 0),
        )
        self.y_row.set_digits(2)
        self.y_row.connect("notify::value", self._on_y_changed)
        self.add(self.y_row)

        # Width Entry
        self.width_row = Adw.SpinRow(
            title=_("Width"),
            adjustment=Gtk.Adjustment.new(10, 1, 10000, 1.0, 1, 0),
        )
        self.width_row.set_digits(2)
        self.width_row.connect("notify::value", self._on_width_changed)
        self.add(self.width_row)

        # Height Entry
        self.height_row = Adw.SpinRow(
            title=_("Height"),
            adjustment=Gtk.Adjustment.new(10, 1, 10000, 1.0, 1, 0),
        )
        self.height_row.set_digits(2)
        self.height_row.connect("notify::value", self._on_height_changed)
        self.add(self.height_row)

        # Fixed Ratio Switch
        self.fixed_ratio_switch = Adw.SwitchRow(
            title=_("Fixed Ratio"), active=True
        )
        self.fixed_ratio_switch.connect(
            "notify::active", self._on_fixed_ratio_toggled
        )
        self.add(self.fixed_ratio_switch)

        # Natural Size Label
        self.natural_size_row = Adw.ActionRow(title=_("Natural Size"))
        self.natural_size_label = Gtk.Label(label=_("N/A"), xalign=0)
        self.natural_size_row.add_suffix(self.natural_size_label)
        self.add(self.natural_size_row)

        # Reset Size Button
        self.reset_row = Adw.ActionRow(title=_("Reset Size"))
        self.reset_button = Gtk.Button(label=_("Reset"))
        self.reset_button.set_halign(Gtk.Align.END)
        self.reset_button.set_valign(Gtk.Align.CENTER)
        self.reset_button.connect("clicked", self._on_reset_clicked)
        self.reset_row.add_suffix(self.reset_button)
        self.reset_row.activatable_widget = self.reset_button
        self.add(self.reset_row)

        # Angle Entry
        self.angle_row = Adw.SpinRow(
            title=_("Angle"),
            # FIX: The 6th argument (page_size) was missing. Added it here.
            adjustment=Gtk.Adjustment.new(0, -360, 360, 1, 10, 0),
            digits=2,
        )
        self.angle_row.connect("notify::value", self._on_angle_changed)
        self.add(self.angle_row)

        # Reset Angle Button
        self.reset_angle_row = Adw.ActionRow(title=_("Reset Angle"))
        self.reset_angle_button = Gtk.Button(label=_("Reset"))
        self.reset_angle_button.set_halign(Gtk.Align.END)
        self.reset_angle_button.set_valign(Gtk.Align.CENTER)
        self.reset_angle_button.connect(
            "clicked", self._on_reset_angle_clicked
        )
        self.reset_angle_row.add_suffix(self.reset_angle_button)
        self.reset_angle_row.activatable_widget = self.reset_angle_button
        self.add(self.reset_angle_row)

        if self.workpiece:
            self.workpiece.size_changed.connect(
                self._on_workpiece_size_changed
            )
            self.workpiece.pos_changed.connect(self._on_workpiece_pos_changed)
            self.workpiece.angle_changed.connect(
                self._on_workpiece_angle_changed
            )
        self._update_ui_from_workpiece()

    def apply_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_string(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _on_width_changed(self, spin_row, GParamSpec):
        logger.debug(f"Width changed to {spin_row.get_value()}")
        if self._in_update:
            return
        if not self.workpiece:
            return
        self._in_update = True
        try:
            new_width = get_spinrow_float(self.width_row)
            current_size = self.workpiece.size
            height_min = self.height_row.get_adjustment().get_lower()
            new_height = current_size[1] if current_size else height_min

            if self.fixed_ratio_switch.get_active():
                aspect_ratio = self.workpiece.get_current_aspect_ratio()
                if aspect_ratio and new_width is not None:
                    new_height = new_width / aspect_ratio
                    if new_height < height_min:
                        new_height = height_min
                        new_width = new_height * aspect_ratio
                    self.height_row.set_value(new_height)
                    self.width_row.set_value(new_width)

            if new_width is not None and new_height is not None:
                bounds = config.machine.dimensions
                old_pos = self.workpiece.pos or (0, 0)
                old_w, old_h = (
                    self.workpiece.get_current_size()
                    or self.workpiece.get_default_size(*bounds)
                )
                old_x, old_y = old_pos

                if self.workpiece.angle == 0:
                    # Resize from top-left for un-rotated
                    new_x = old_x
                    new_y = old_y + old_h - new_height
                else:
                    # Resize from center for rotated
                    new_x = old_x + (old_w - new_width) / 2
                    new_y = old_y + (old_h - new_height) / 2

                self.workpiece.set_pos(new_x, new_y)
                self.workpiece.set_size(new_width, new_height)
        finally:
            self._in_update = False

    def _on_height_changed(self, spin_row, GParamSpec):
        logger.debug(f"Height changed to {spin_row.get_value()}")
        if self._in_update:
            return
        if not self.workpiece:
            return
        self._in_update = True
        try:
            new_height = get_spinrow_float(self.height_row)
            current_size = self.workpiece.size
            width_min = self.width_row.get_adjustment().get_lower()
            new_width = current_size[0] if current_size else width_min

            if self.fixed_ratio_switch.get_active():
                aspect_ratio = self.workpiece.get_current_aspect_ratio()
                if aspect_ratio and new_height is not None:
                    new_width = new_height * aspect_ratio
                    if new_width < width_min:
                        new_width = width_min
                        new_height = new_width / aspect_ratio
                    self.width_row.set_value(new_width)
                    self.height_row.set_value(new_height)

            if new_width is not None and new_height is not None:
                bounds = config.machine.dimensions
                old_pos = self.workpiece.pos or (0, 0)
                old_w, old_h = (
                    self.workpiece.get_current_size()
                    or self.workpiece.get_default_size(*bounds)
                )
                old_x, old_y = old_pos

                if self.workpiece.angle == 0:
                    # Resize from top-left for un-rotated
                    new_x = old_x
                    new_y = old_y + old_h - new_height
                else:
                    # Resize from center for rotated
                    new_x = old_x + (old_w - new_width) / 2
                    new_y = old_y + (old_h - new_height) / 2

                self.workpiece.set_pos(new_x, new_y)
                self.workpiece.set_size(new_width, new_height)
        finally:
            self._in_update = False

    def _on_x_changed(self, spin_row, GParamSpec):
        logger.debug(f"X position changed to {spin_row.get_value()}")
        if self._in_update:
            return
        if not self.workpiece:
            return
        self._in_update = True
        try:
            new_x = get_spinrow_float(self.x_row)
            current_pos = self.workpiece.pos
            new_y = current_pos[1] if current_pos else 0.0
            if new_x is not None:
                self.workpiece.set_pos(new_x, new_y)
        finally:
            self._in_update = False

    def _on_y_changed(self, spin_row, GParamSpec):
        logger.debug(f"Y position changed to {spin_row.get_value()}")
        if self._in_update:
            return
        if not self.workpiece:
            return
        self._in_update = True
        try:
            new_y = get_spinrow_float(self.y_row)
            current_pos = self.workpiece.pos
            new_x = current_pos[0] if current_pos else 0.0
            if new_y is not None:
                self.workpiece.set_pos(new_x, new_y)
        finally:
            self._in_update = False

    def _on_angle_changed(self, spin_row, GParamSpec):
        if self._in_update or not self.workpiece:
            return
        self._in_update = True
        try:
            self.workpiece.set_angle(spin_row.get_value())
        finally:
            self._in_update = False

    def _on_fixed_ratio_toggled(self, switch_row, GParamSpec):
        logger.debug(f"Fixed ratio toggled: {switch_row.get_active()}")
        if self._in_update:
            return False
        if not self.workpiece:
            return False
        self._in_update = True
        try:
            if self.fixed_ratio_switch.get_active():
                new_width = get_spinrow_float(self.width_row)
                new_height = get_spinrow_float(self.height_row)

                aspect_ratio = self.workpiece.get_current_aspect_ratio()

                if aspect_ratio and new_width is not None:
                    # When ratio is toggled, prioritize width for calculation
                    new_height = new_width / aspect_ratio
                    self.height_row.set_value(new_height)
                    if new_width is not None and new_height is not None:
                        # Also need to adjust position here
                        bounds = config.machine.dimensions
                        old_pos = self.workpiece.pos or (0, 0)
                        old_w, old_h = (
                            self.workpiece.get_current_size()
                            or self.workpiece.get_default_size(*bounds)
                        )
                        old_x, old_y = old_pos

                        if self.workpiece.angle == 0:
                            new_x, new_y = old_x, old_y + old_h - new_height
                        else:
                            new_x, new_y = (
                                old_x + (old_w - new_width) / 2,
                                old_y + (old_h - new_height) / 2,
                            )

                        self.workpiece.set_pos(new_x, new_y)
                        self.workpiece.set_size(new_width, new_height)
        finally:
            self._in_update = False
        return False  # Allow the default handler to run

    def _on_reset_clicked(self, button):
        if not self.workpiece:
            return
        self._in_update = True
        bounds = config.machine.dimensions
        natural_width, natural_height = self.workpiece.get_default_size(
            *bounds
        )
        self.workpiece.set_size(natural_width, natural_height)
        self._in_update = False
        self._update_ui_from_workpiece()

    def _on_reset_angle_clicked(self, button):
        if self.workpiece:
            self.workpiece.set_angle(0.0)

    def _on_workpiece_size_changed(self, workpiece):
        if self._in_update:
            return
        logger.debug(f"Workpiece size changed: {workpiece.size}")
        self._update_ui_from_workpiece()

    def set_workpiece(self, workpiece: Optional[WorkPiece]):
        self._in_update = True
        if self.workpiece:
            self.workpiece.size_changed.disconnect(
                self._on_workpiece_size_changed
            )
            self.workpiece.pos_changed.disconnect(
                self._on_workpiece_pos_changed
            )
            self.workpiece.angle_changed.disconnect(
                self._on_workpiece_angle_changed
            )
        self.workpiece = workpiece
        if self.workpiece:
            self.workpiece.size_changed.connect(
                self._on_workpiece_size_changed
            )
            self.workpiece.pos_changed.connect(self._on_workpiece_pos_changed)
            self.workpiece.angle_changed.connect(
                self._on_workpiece_angle_changed
            )
        self._in_update = False
        self._update_ui_from_workpiece()

    def _on_workpiece_pos_changed(self, workpiece):
        if self._in_update:
            return
        logger.debug(f"Workpiece position changed: {workpiece.pos}")
        self._update_ui_from_workpiece()

    def _on_workpiece_angle_changed(self, workpiece):
        if self._in_update:
            return
        logger.debug(f"Workpiece angle changed: {workpiece.angle}")
        self._update_ui_from_workpiece()

    def _update_ui_from_workpiece(self):
        logger.debug(f"Updating UI for workpiece: {self.workpiece}")
        if not self.workpiece:
            return
        self._in_update = True
        bounds = config.machine.dimensions
        size = (
            self.workpiece.get_current_size()
            or self.workpiece.get_default_size(*bounds)
        )
        pos = self.workpiece.pos
        angle = self.workpiece.angle

        if size:
            width, height = size
            logger.debug(f"Updating UI: width={width}, height={height}")
            self.width_row.set_value(width)
            self.height_row.set_value(height)
            natural_width, natural_height = self.workpiece.get_default_size(
                *bounds
            )
            self.natural_size_label.set_label(
                f"{natural_width:.2f}x{natural_height:.2f}"
            )
        else:
            self.natural_size_label.set_label("N/A")
        if pos:
            x, y = pos
            logger.debug(f"Updating UI: x={x}, y={y}")
            self.x_row.set_value(x)
            self.y_row.set_value(y)

        logger.debug(f"Updating UI: angle={angle}")
        self.angle_row.set_value(angle)

        self._in_update = False

"""Unicode Braille Sparkline rendering component for high-resolution TUI graphs."""

from rich.text import Text
from textual.widgets import Static

# Braille dot map offsets for left and right columns
# Left col dots y=0..3: 7(0x40), 3(0x04), 2(0x02), 1(0x01)
LEFT_DOTS = [0x40, 0x04, 0x02, 0x01]
# Right col dots y=0..3: 8(0x80), 6(0x20), 5(0x10), 4(0x08)
RIGHT_DOTS = [0x80, 0x20, 0x10, 0x08]


def render_braille_line(
    data: list[float],
    width_chars: int,
    max_val: float = 100.0,
    min_val: float = 0.0,
) -> str:
    """Renders a single line of high-resolution braille graph representing data points.
    Each character cell contains 2 data points (left and right columns), each with 4 vertical dots.
    """
    if not data:
        return " " * width_chars

    # We need 2 * width_chars data points
    num_points = width_chars * 2
    if len(data) > num_points:
        sampled = data[-num_points:]
    else:
        # Pad left with min_val if fewer points than needed
        sampled = [min_val] * (num_points - len(data)) + list(data)

    val_range = max(1e-6, max_val - min_val)
    chars = []

    for i in range(0, num_points, 2):
        v_left = sampled[i]
        v_right = sampled[i + 1]

        # Convert values to 0..4 height level
        h_left = round(max(0.0, min(1.0, (v_left - min_val) / val_range)) * 4.0)
        h_right = round(max(0.0, min(1.0, (v_right - min_val) / val_range)) * 4.0)

        char_code = 0x2800

        # Fill left dots up to h_left
        for y in range(h_left):
            char_code |= LEFT_DOTS[y]

        # Fill right dots up to h_right
        for y in range(h_right):
            char_code |= RIGHT_DOTS[y]

        chars.append(chr(char_code))

    return "".join(chars)


class BrailleSparkline(Static):
    """Textual Widget that displays a braille sparkline chart."""

    def __init__(
        self,
        data: list[float] | None = None,
        max_val: float = 100.0,
        color: str = "#89b4fa",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.data: list[float] = data or []
        self.max_val: float = max_val
        self.chart_color: str = color

    def update_data(self, new_data: list[float], max_val: float | None = None) -> None:
        self.data = new_data
        if max_val is not None:
            self.max_val = max_val
        self.refresh()

    def render(self) -> Text:
        w = max(1, self.content_size.width)
        line = render_braille_line(self.data, width_chars=w, max_val=self.max_val)
        return Text(line, style=self.chart_color)

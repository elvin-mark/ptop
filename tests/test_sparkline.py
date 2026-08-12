from ptop.widgets.sparkline import render_braille_line


def test_render_braille_line_empty():
    res = render_braille_line([], width_chars=5)
    assert len(res) == 5
    assert res == "     "


def test_render_braille_line_values():
    data = [0.0, 50.0, 100.0, 25.0]
    res = render_braille_line(data, width_chars=2, max_val=100.0)
    assert len(res) == 2
    # Ensure braille character range 0x2800..0x28FF
    for char in res:
        assert 0x2800 <= ord(char) <= 0x28FF

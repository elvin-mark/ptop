from ptop.app import PtopApp


def test_ptop_app_init():
    app = PtopApp()
    assert app.active_theme is not None
    assert app.active_theme.name in [
        "catppuccin",
        "tokyonight",
        "nord",
        "dracula",
        "cyberpunk",
    ]

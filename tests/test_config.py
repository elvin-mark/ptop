from ptop.config import Config
from ptop.theme import get_theme


def test_default_config():
    cfg = Config()
    assert cfg.theme == "catppuccin"
    assert cfg.refresh_rate_ms == 1000
    assert cfg.show_cpu is True


def test_theme_retrieval():
    t_cat = get_theme("catppuccin")
    assert t_cat.name == "catppuccin"
    assert t_cat.primary != ""

    t_invalid = get_theme("nonexistent_theme")
    assert t_invalid.name == "catppuccin"

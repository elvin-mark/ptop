"""Theme configurations for ptop."""

from dataclasses import dataclass


@dataclass
class Theme:
    name: str
    label: str
    bg: str
    surface: str
    panel_bg: str
    border: str
    border_title: str
    primary: str
    secondary: str
    accent: str
    text: str
    text_muted: str
    cpu_color: str
    mem_color: str
    disk_color: str
    net_rx_color: str
    net_tx_color: str
    gpu_color: str
    warning: str
    error: str


THEMES: dict[str, Theme] = {
    "catppuccin": Theme(
        name="catppuccin",
        label="Catppuccin Mocha",
        bg="#1e1e2e",
        surface="#181825",
        panel_bg="#1e1e2e",
        border="#89b4fa",
        border_title="#cba6f7",
        primary="#89b4fa",
        secondary="#cba6f7",
        accent="#f5e0dc",
        text="#cdd6f4",
        text_muted="#6c7086",
        cpu_color="#89b4fa",
        mem_color="#a6e3a1",
        disk_color="#f9e2af",
        net_rx_color="#89dceb",
        net_tx_color="#f5c2e7",
        gpu_color="#fab387",
        warning="#f9e2af",
        error="#f38ba8",
    ),
    "tokyonight": Theme(
        name="tokyonight",
        label="Tokyo Night",
        bg="#1a1b26",
        surface="#16161e",
        panel_bg="#1a1b26",
        border="#7aa2f7",
        border_title="#bb9af7",
        primary="#7aa2f7",
        secondary="#bb9af7",
        accent="#7dcfff",
        text="#c0caf5",
        text_muted="#565f89",
        cpu_color="#7aa2f7",
        mem_color="#9ece6a",
        disk_color="#e0af68",
        net_rx_color="#7dcfff",
        net_tx_color="#f7768e",
        gpu_color="#ff9e64",
        warning="#e0af68",
        error="#f7768e",
    ),
    "nord": Theme(
        name="nord",
        label="Nord",
        bg="#2e3440",
        surface="#272c36",
        panel_bg="#2e3440",
        border="#88c0d0",
        border_title="#81a1c1",
        primary="#88c0d0",
        secondary="#81a1c1",
        accent="#eceff4",
        text="#d8dee9",
        text_muted="#4c566a",
        cpu_color="#88c0d0",
        mem_color="#a3be8c",
        disk_color="#ebcb8b",
        net_rx_color="#81a1c1",
        net_tx_color="#b48ead",
        gpu_color="#d08770",
        warning="#ebcb8b",
        error="#bf616a",
    ),
    "dracula": Theme(
        name="dracula",
        label="Dracula",
        bg="#282a36",
        surface="#21222c",
        panel_bg="#282a36",
        border="#bd93f9",
        border_title="#ff79c6",
        primary="#bd93f9",
        secondary="#ff79c6",
        accent="#f8f8f2",
        text="#f8f8f2",
        text_muted="#6272a4",
        cpu_color="#8be9fd",
        mem_color="#50fa7b",
        disk_color="#f1fa8c",
        net_rx_color="#8be9fd",
        net_tx_color="#ff79c6",
        gpu_color="#ffb86c",
        warning="#f1fa8c",
        error="#ff5555",
    ),
    "cyberpunk": Theme(
        name="cyberpunk",
        label="Cyberpunk",
        bg="#0d0f18",
        surface="#07080d",
        panel_bg="#0d0f18",
        border="#00f0ff",
        border_title="#ff0055",
        primary="#00f0ff",
        secondary="#ff0055",
        accent="#ffe600",
        text="#e0e6ed",
        text_muted="#4a5568",
        cpu_color="#00f0ff",
        mem_color="#00ff66",
        disk_color="#ffe600",
        net_rx_color="#00f0ff",
        net_tx_color="#ff0055",
        gpu_color="#ff9900",
        warning="#ffe600",
        error="#ff0055",
    ),
}

DEFAULT_THEME = "catppuccin"


def get_theme(name: str) -> Theme:
    return THEMES.get(name.lower(), THEMES[DEFAULT_THEME])

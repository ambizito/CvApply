"""Shared UI tokens and ttk style configuration."""
from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import Misc, ttk


@dataclass(frozen=True)
class ColorTokens:
    """Color palette shared across the application."""

    background: str = "#F7F9FC"
    surface: str = "#FFFFFF"
    primary_text: str = "#1B1B1F"
    secondary_text: str = "#4A4A55"
    accent: str = "#2D64BC"
    danger: str = "#C13245"


@dataclass(frozen=True)
class FontTokens:
    """Font definitions centralised for reuse."""

    heading: tuple[str, int, str] = ("Helvetica", 16, "bold")
    body: tuple[str, int] = ("Helvetica", 11)
    mono: tuple[str, int] = ("Courier New", 10)


@dataclass(frozen=True)
class SpacingTokens:
    """Standard spacing units used throughout the UI."""

    window_padding: int = 24
    section: int = 16
    inline: int = 8


@dataclass(frozen=True)
class UITokens:
    """Bundle of UI tokens available to every screen."""

    colors: ColorTokens
    fonts: FontTokens
    spacing: SpacingTokens


def configure_styles(root: Misc) -> UITokens:
    """Configure ttk styles and return the UI tokens."""

    colors = ColorTokens()
    fonts = FontTokens()
    spacing = SpacingTokens()

    style = ttk.Style(root)
    # Ensure deterministic base theme
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=colors.background)
    style.configure("Surface.TFrame", background=colors.surface)
    style.configure("TLabel", background=colors.background, foreground=colors.primary_text, font=fonts.body)
    style.configure("Secondary.TLabel", foreground=colors.secondary_text)
    style.configure("Heading.TLabel", font=fonts.heading, foreground=colors.primary_text)
    style.configure("Accent.TButton", foreground=colors.surface)
    style.map(
        "Accent.TButton",
        background=[("!disabled", colors.accent), ("disabled", colors.secondary_text)],
        relief=[("pressed", "sunken"), ("!pressed", "raised")],
    )

    return UITokens(colors=colors, fonts=fonts, spacing=spacing)

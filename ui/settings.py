from dataclasses import dataclass

@dataclass
class AppSettings:
    fullscreen: bool = False
    window_size: tuple[int, int] = (800, 600)
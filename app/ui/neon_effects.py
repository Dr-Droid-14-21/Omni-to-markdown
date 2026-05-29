from __future__ import annotations

import math
import time
import wave
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPropertyAnimation, Qt, QUrl
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QGraphicsDropShadowEffect, QPushButton, QWidget

from app.core.paths import get_cache_dir

try:
    from PySide6.QtMultimedia import QSoundEffect
except ImportError:  # pragma: no cover - depends on local Qt multimedia availability.
    QSoundEffect = None  # type: ignore[assignment]


class _ToneBank(QObject):
    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._effects: dict[str, QSoundEffect] = {}
        self._last_played: dict[str, float] = {}
        if QSoundEffect is None:
            return
        try:
            sound_dir = get_cache_dir() / "ui-sounds"
            sound_dir.mkdir(parents=True, exist_ok=True)
            tones = {
                "hover": (sound_dir / "neon-hover.wav", (880.0, 1320.0), 0.035, 0.08),
                "click": (sound_dir / "neon-click.wav", (220.0, 660.0), 0.07, 0.11),
                "start": (sound_dir / "neon-start.wav", (440.0, 880.0), 0.09, 0.11),
                "complete": (sound_dir / "neon-complete.wav", (660.0, 990.0), 0.12, 0.12),
                "warning": (sound_dir / "neon-warning.wav", (196.0, 392.0), 0.12, 0.12),
            }
            for name, (path, freqs, duration, volume) in tones.items():
                if not path.exists():
                    self._write_tone(path, freqs, duration, volume)
                effect = QSoundEffect(self)
                effect.setSource(QUrl.fromLocalFile(str(path)))
                effect.setLoopCount(1)
                effect.setVolume(volume)
                self._effects[name] = effect
        except OSError:
            self._effects.clear()

    def play(self, name: str) -> None:
        now = time.monotonic()
        if now - self._last_played.get(name, 0.0) < 0.06:
            return
        self._last_played[name] = now

        effect = self._effects.get(name)
        if effect is not None:
            effect.stop()
            effect.play()
            return
        if name in {"click", "start", "complete", "warning"}:
            QApplication.beep()

    def _write_tone(
        self,
        path: Path,
        frequencies: tuple[float, float],
        duration_seconds: float,
        volume: float,
    ) -> None:
        sample_rate = 44_100
        frame_count = int(sample_rate * duration_seconds)
        fade_count = max(1, int(sample_rate * 0.006))

        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            frames = bytearray()
            for index in range(frame_count):
                t = index / sample_rate
                fade_in = min(1.0, index / fade_count)
                fade_out = min(1.0, (frame_count - index) / fade_count)
                envelope = min(fade_in, fade_out)
                sample = sum(math.sin(2.0 * math.pi * freq * t) for freq in frequencies)
                sample = sample / len(frequencies) * envelope * volume
                pcm_sample = int(max(-1.0, min(1.0, sample)) * 32767)
                frames.extend(pcm_sample.to_bytes(2, "little", signed=True))
            wav.writeframes(bytes(frames))


class NeonUiEffects(QObject):
    """Installs hover/click sound and animated neon light on app buttons."""

    _ROLE_SETTINGS = {
        "primary": (QColor(21, 244, 255, 115), 20, 36),
        "hero": (QColor(21, 244, 255, 145), 24, 42),
        "secondary": (QColor(41, 190, 205, 72), 12, 22),
        "danger": (QColor(255, 76, 112, 110), 15, 28),
        "quiet": (QColor(95, 150, 160, 45), 8, 14),
    }

    def __init__(self, root: QWidget) -> None:
        super().__init__(root)
        self._root = root
        self._sounds = _ToneBank(self)
        self._effects: dict[QPushButton, QGraphicsDropShadowEffect] = {}
        self._animations: dict[QPushButton, QPropertyAnimation] = {}

    def install(self) -> None:
        for button in self._root.findChildren(QPushButton):
            self.register_button(button)

    def register_button(self, button: QPushButton) -> None:
        if button in self._effects:
            return
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        role = str(button.property("uiRole") or "secondary")
        color, idle_blur, _ = self._ROLE_SETTINGS.get(role, self._ROLE_SETTINGS["secondary"])
        effect = QGraphicsDropShadowEffect(button)
        effect.setOffset(0, 0)
        effect.setBlurRadius(idle_blur)
        effect.setColor(color)
        button.setGraphicsEffect(effect)
        button.installEventFilter(self)
        self._effects[button] = effect

    def play_sound(self, name: str) -> None:
        self._sounds.play(name)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if not isinstance(watched, QPushButton):
            return super().eventFilter(watched, event)
        if watched not in self._effects:
            return super().eventFilter(watched, event)

        if event.type() == QEvent.Type.Enter and watched.isEnabled():
            self._sounds.play("hover")
            self._animate_button(watched, "hover")
        elif event.type() == QEvent.Type.Leave:
            self._animate_button(watched, "idle")
        elif event.type() == QEvent.Type.MouseButtonPress and watched.isEnabled():
            self._sounds.play("click")
            self._animate_button(watched, "press")
        elif event.type() == QEvent.Type.MouseButtonRelease and watched.isEnabled():
            self._animate_button(watched, "hover")
        elif event.type() == QEvent.Type.EnabledChange:
            self._animate_button(watched, "idle" if watched.isEnabled() else "disabled")

        return super().eventFilter(watched, event)

    def _animate_button(self, button: QPushButton, state: str) -> None:
        effect = self._effects[button]
        role = str(button.property("uiRole") or "secondary")
        color, idle_blur, hover_blur = self._ROLE_SETTINGS.get(
            role,
            self._ROLE_SETTINGS["secondary"],
        )

        target_color = QColor(color)
        target_blur = idle_blur
        duration = 180
        if state == "hover":
            target_color.setAlpha(min(230, target_color.alpha() + 85))
            target_blur = hover_blur
            duration = 130
        elif state == "press":
            target_color.setAlpha(245)
            target_blur = hover_blur + 8
            duration = 70
        elif state == "disabled":
            target_color.setAlpha(18)
            target_blur = 4
            duration = 100

        current_animation = self._animations.get(button)
        if current_animation is not None:
            current_animation.stop()

        effect.setColor(target_color)
        animation = QPropertyAnimation(effect, b"blurRadius", self)
        animation.setStartValue(effect.blurRadius())
        animation.setEndValue(target_blur)
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        self._animations[button] = animation

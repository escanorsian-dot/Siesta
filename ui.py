from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QPen
from PyQt6.QtCore import Qt, QTimer
import math
import random


class Sphere(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Window
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.setGeometry(120, 120, 320, 320)

        self.phase = 0
        self.mode = "idle"

        self.bars = [random.randint(2, 20) for _ in range(24)]

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(40)

    def set_mode(self, mode):
        self.mode = mode
        self.update()

    def animate(self):
        self.phase += 0.18

        if self.mode == "speaking":
            self.bars = [random.randint(12, 48) for _ in range(24)]
        elif self.mode == "listening":
            self.bars = [random.randint(8, 32) for _ in range(24)]
        elif self.mode == "active":
            self.bars = [random.randint(6, 26) for _ in range(24)]
        else:
            self.bars = [random.randint(2, 16) for _ in range(24)]

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() // 2
        cy = self.height() // 2

        base_radius = 70

        if self.mode == "speaking":
            radius = int(base_radius + 8 * math.sin(self.phase * 1.1))
        elif self.mode == "listening":
            radius = int(base_radius + 10 * math.sin(self.phase * 1.4))
        elif self.mode == "active":
            radius = int(base_radius + 6 * math.sin(self.phase * 0.9))
        else:
            radius = int(base_radius + 4 * math.sin(self.phase))

        gradient = QRadialGradient(cx, cy, radius + 120)

        if self.mode == "idle":
            color = QColor(120, 140, 160)
        elif self.mode == "listening":
            color = QColor(120, 180, 255)
        elif self.mode == "active":
            color = QColor(255, 190, 90)
        else:
            color = QColor(90, 220, 200)

        gradient.setColorAt(0, color)
        gradient.setColorAt(0.35, QColor(color.red(), color.green(), color.blue(), 150))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

        # Outer rings
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if self.mode in ["listening", "speaking", "active"]:
            ring_color = QColor(color.red(), color.green(), color.blue(), 110)

            for i in range(4):
                wave = int(radius + 18 + 10 * i + 8 * math.sin(self.phase + i))
                painter.setPen(QPen(ring_color, 2))
                painter.drawEllipse(cx - wave, cy - wave, wave * 2, wave * 2)

        # Audio bars
        painter.setPen(Qt.PenStyle.NoPen)
        bar_color = QColor(color.red(), color.green(), color.blue(), 180)
        painter.setBrush(bar_color)

        bar_count = len(self.bars)
        angle_step = (2 * math.pi) / bar_count

        for i, bar in enumerate(self.bars):
            angle = i * angle_step + self.phase * 0.35
            inner = radius + 18
            outer = inner + bar

            x1 = cx + inner * math.cos(angle)
            y1 = cy + inner * math.sin(angle)
            x2 = cx + outer * math.cos(angle)
            y2 = cy + outer * math.sin(angle)

            painter.setPen(QPen(bar_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
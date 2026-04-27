from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QRect

class LoosePickIsland(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.ctrl = controller

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._collapsed_width = 220
        self._expanded_width = 400
        self._height = 50
        self.setFixedHeight(self._height)
        self.setFixedWidth(self._collapsed_width)

        # Main Container
        self.container = QWidget(self)
        self.container.setStyleSheet("""
            background: rgba(20, 20, 20, 0.9);
            border-radius: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        """)
        self.container.setFixedSize(self._collapsed_width, self._height)

        # Use a distinct name to avoid shadowing QWidget.layout()
        self.hbox = QHBoxLayout(self.container)

        # Info Label
        self.info_label = QLabel("Loose Pick")
        self.info_label.setStyleSheet("color: white; font-weight: bold;")

        # Buttons (hidden by default, shown on hover)
        self.btn_play = QPushButton("⏯")
        self.btn_next = QPushButton("⏭")
        for b in [self.btn_play, self.btn_next]:
            b.setStyleSheet("color: white; background: none; border: none; font-size: 16px;")
            b.hide()

        self.hbox.addWidget(self.info_label)
        self.hbox.addWidget(self.btn_play)
        self.hbox.addWidget(self.btn_next)

        # Connect Buttons
        self.btn_play.clicked.connect(self.ctrl.play_pause)
        self.btn_next.clicked.connect(self.ctrl.next_track)

        # Animation for the outer window width
        self._anim = QPropertyAnimation(self, b"minimumWidth")
        self._anim.setDuration(200)

    def enterEvent(self, event):
        self.info_label.setText(self.ctrl.get_current_track())
        self.btn_play.show()
        self.btn_next.show()
        self._resize_to(self._expanded_width)

    def leaveEvent(self, event):
        self.info_label.setText("Loose Pick")
        self.btn_play.hide()
        self.btn_next.hide()
        self._resize_to(self._collapsed_width)

    def _resize_to(self, width: int):
        """Animate the island width and keep container in sync."""
        self._anim.stop()
        self._anim.setStartValue(self.width())
        self._anim.setEndValue(width)
        self._anim.start()
        self.container.setFixedWidth(width)
        self.setFixedWidth(width)

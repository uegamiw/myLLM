from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QSizeGrip
from PySide6.QtGui import QKeyEvent
from PySide6.QtCore import Qt

class TextEditWithZoom(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.defaultFontSize = self.font().pointSize()

    def keyPressEvent(self, event: QKeyEvent):
        if event.modifiers() == Qt.ControlModifier:
            if event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
                self.zoomIn()
                return
            elif event.key() == Qt.Key_Minus:
                self.zoomOut()
                return
        super().keyPressEvent(event)

    def zoomIn(self, range=1):
        font = self.font()
        font.setPointSize(font.pointSize() + range)
        self.setFont(font)

    def zoomOut(self, range=1):
        font = self.font()
        newSize = font.pointSize() - range
        if newSize > 0:  # Prevent the font size from becoming negative or too small
            font.setPointSize(newSize)
            self.setFont(font)

    def append_text(self, text, deliminator=None):
        if deliminator:
            # self.moveCursor(Qt.CursorMovement.End)
            self.insertPlainText(f"{text}{deliminator}")
        else:
            # self.moveCursor(Qt.CursorMovement.End)
            self.insertPlainText(text)

class ResizableTextEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text_edit = TextEditWithZoom(self)
        self.size_grip = QSizeGrip(self)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_edit)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.size_grip.move(self.width() - self.size_grip.width(),
                            self.height() - self.size_grip.height())

    # def sizeHint(self):
    #     return QSize(300, 200)  # デフォルトサイズを設定

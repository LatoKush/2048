import sys

import random

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGridLayout, QWidget, QAction, QDialog, QVBoxLayout, \
    QHBoxLayout, QTextBrowser, QPushButton, QSizePolicy, QMessageBox,  QComboBox

class Tile(QLabel): # определяем плитки игрового поля
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("border: 1px solid black; font-size: 30px; font-weight: bold;")

    def setValue(self, value):
        self.setText(str(value))

    def isEmpty(self):
        return not bool(self.text())

class Game(QWidget): # логика игры
    def __init__(self, size=4):
        super().__init__()
        self.size = size
        self.grid = QGridLayout() # сетка для плит
        self.tiles = [[Tile(self) for j in range(size)] for i in range(size)] # двумерный список объектов Tile
        self.tiles[0][0].setValue(1024)
        self.tiles[1][1].setValue(1024)
        self.initUI()

    def initUI(self): # добавляем плитки на сетку
        self.grid.setSpacing(10)
        for i in range(self.size):
            for j in range(self.size):
                self.grid.addWidget(self.tiles[i][j], i, j)
        self.setLayout(self.grid)

    def addTile(self): # в рандомную пустую ячейку добавляем 2
        emptyTiles = [(i, j) for i in range(self.size) for j in range(self.size) if self.tiles[i][j].isEmpty()]
        if emptyTiles:
            i, j = random.choice(emptyTiles)
            self.tiles[i][j].setValue(2)

    def move(self, dx, dy):
        moved = False # был ли ход?
        for i in range(self.size):
            for j in range(self.size):
                x, y = i + dx, j + dy # меняет положение
                if 0 <= x < self.size and 0 <= y < self.size and not self.tiles[i][j].isEmpty(): # двигаем плитки до упора в направлении пока не столкнёмся с другой плиткой или не достигнем границы игрового поля.
                    while 0 <= x < self.size and 0 <= y < self.size and self.tiles[x][y].isEmpty():
                        self.tiles[x][y].setValue(self.tiles[x - dx][y - dy].text())
                        self.tiles[x - dx][y - dy].clear()
                        x += dx
                        y += dy
                        moved = True
                    if 0 <= x < self.size and 0 <= y < self.size and self.tiles[x][y].text() == self.tiles[x - dx][
                        y - dy].text():
                        value = int(self.tiles[x][y].text()) * 2
                        self.tiles[x][y].setValue(value)
                        self.tiles[x - dx][y - dy].clear()
                        moved = True
                        if value == 2048:
                            self.gameWonDialog()
                            return
        if moved:
            self.addTile()
        if self.gameOver:
            self.gameOverDialog()

    def reset(self):
        for i in range(self.size):
            for j in range(self.size):
                self.tiles[i][j].clear()
        self.tiles[0][0].setValue(2)
        self.tiles[1][1].setValue(4)

    @property
    def gameOver(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.tiles[i][j].isEmpty():
                    return False
                if i > 0 and self.tiles[i][j].text() == self.tiles[i - 1][j].text():
                    return False
                if j > 0 and self.tiles[i][j].text() == self.tiles[i][j - 1].text():
                    return False
        return True

    def gameOverDialog(self):
        msgBox = QMessageBox()
        msgBox.setText("Game over!")
        msgBox.exec_()
        self.reset()

    def gameWonDialog(self):
        msgBox = QMessageBox()
        msgBox.setText("Победа!")
        msgBox.exec_()
        self.reset()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.move(-1, 0)
        elif key == Qt.Key_Right:
            self.move(1, 0)
        elif key == Qt.Key_Up:
            self.move(0, -1)
        elif key == Qt.Key_Down:
            self.move(0, 1)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2048")
        self.setGeometry(100, 100, 400, 400)
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        mainLayout = QVBoxLayout(centralWidget)

        self.gameSize = 4
        self.game = Game(self.gameSize)
        mainLayout.addWidget(self.game)
        self.game.setFocusPolicy(Qt.StrongFocus)
        self.game.keyPressEvent = self.keyPressEventGame

        restartButton = QPushButton("Новая игра", self)
        restartButton.clicked.connect(self.restartGame)
        mainLayout.addWidget(restartButton)

        menuBar = self.menuBar()
        newGameAction = QAction("Новая игра", self)

        rulesButton = QPushButton("Правила игры", self)
        rulesButton.clicked.connect(self.showRules)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(restartButton)
        buttonLayout.addWidget(rulesButton)

        sizeLabel = QLabel("Размер поля:")
        sizeComboBox = QComboBox()
        sizeComboBox.addItems(["2x2", "3x3", "4x4", "5x5", "6x6", "7x7", "8x8", "9x9"])
        sizeComboBox.setCurrentIndex(2)
        sizeComboBox.currentIndexChanged.connect(self.changeGameSize)
        sizeLayout = QHBoxLayout()
        sizeLayout.addWidget(sizeLabel)
        sizeLayout.addWidget(sizeComboBox)
        mainLayout.addLayout(sizeLayout)
        mainLayout.addLayout(buttonLayout)

    def restartGame(self):
        self.game.reset()

    def keyPressEventGame(self, event):
        game = self.centralWidget().layout().itemAt(0).widget()
        key = event.key()
        if key == Qt.Key_Left:
            game.move(0, -1)
        elif key == Qt.Key_Right:
            game.move(0, 1)
        elif key == Qt.Key_Up:
            game.move(-1, 0)
        elif key == Qt.Key_Down:
            game.move(1, 0)

    def startNewGame(self):
        self.game.reset()

    def changeGameSize(self, index):
        self.gameSize = index + 2
        self.game.setParent(None)
        self.game = Game(self.gameSize)
        self.centralWidget().layout().insertWidget(1, self.game)
        self.game.setFocusPolicy(Qt.StrongFocus)
        self.game.keyPressEvent = self.keyPressEventGame
        self.game.addTile()
        self.game.addTile()

    def showRules(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Правила игры")
        dialog.setFixedSize(400, 400)
        textBrowser = QTextBrowser(dialog)
        textBrowser.setOpenExternalLinks(True)
        textBrowser.setHtml("<h1 style='text-align: center;'>Правила игры 2048</h1>"
                            "<p>Игра 2048 представляет собой игровое поле размером 4x4, на котором в каждый момент "
                            "времени находится несколько плиток с числами, каждая из которых может быть пустой или иметь "
                            "значение 2 или 4. Цель игры заключается в том, чтобы сложить плитки с одинаковыми числами, "
                            "получая при этом новые плитки с большими числами. Игра заканчивается в случае, если на "
                            "игровом поле не останется свободных ячеек или если невозможно сложить плитки.</p>"
                            "<p>Для перемещения плиток используйте клавиши со стрелками на клавиатуре.</p>"
                            "<p>Удачи!</p>")
        textBrowser.move(75, 75)
        closeButton = QPushButton("Закрыть", dialog)
        closeButton.setFixedSize(150, 40)
        closeButton.move(120, 330)
        closeButton.clicked.connect(dialog.close)

        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Game()
    window = Window()
    window.show()
    sys.exit(app.exec_())
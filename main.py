import jarengine as JE


MINESWIPE: JE.Games.JEGame
WINDOW_SIZE: JE.Systems.JEVector2D
GRID_SIZE: JE.Systems.JEVector2D
CELL_SIZE: JE.Systems.JEVector2D


class Cell(JE.Widgets.UI.JEButton):
    def __init__(self, x, y):

        position = (CELL_SIZE.x * x, CELL_SIZE.y * y)

        super().__init__(position=position, size=CELL_SIZE, outline_color=(0, 0, 0), outline_size=1)
        self.x = x
        self.y = y
        self.mine = JE.JEFalse
        self.revealed = JE.JEFalse
        self.flagged = JE.JEFalse
        self.number = 0
        MINESWIPE.add_entity(self)
        board[self.y].add(self)


board: JE.Systems.JEContainer[JE.Systems.JEContainer[Cell]]


def main():
    global MINESWIPE, WINDOW_SIZE, GRID_SIZE, CELL_SIZE, board

    JE.init("/home/jarjarbin/Desktop/python/JarEngine-Games/JarMineSwipe")

    WINDOW_SIZE = JE.Systems.JEVector2D(
        JE.Interns.Config.get("window", "WINDOW", "width", int),
        JE.Interns.Config.get("window", "WINDOW", "height", int)
    )
    GRID_SIZE = JE.Systems.JEVector2D(20, 20)
    CELL_SIZE = JE.Systems.JEVector2D((WINDOW_SIZE.x / GRID_SIZE.x), (WINDOW_SIZE.y / GRID_SIZE.y))

    MINESWIPE = JE.Games.JEGame()
    MINESWIPE.set_window(JE.Games.JEWindow())

    JE.Games.Systems.JERenderSystem(MINESWIPE)

    board = JE.Systems.JEContainer(JE.Systems.JEContainer, JE.JETrue)
    for y in range(int(GRID_SIZE.y)):
        board.add(JE.Systems.JEContainer(Cell, JE.JETrue))
        for x in range(int(GRID_SIZE.x)):
            Cell(x, y)

    MINESWIPE.event.add(JE.Events.Event.JEEventWatcher(JE.JEEvtQuit, lambda g, e: MINESWIPE.close()))

    MINESWIPE.refresh()

    while MINESWIPE.is_open:
        MINESWIPE.update()
        MINESWIPE.display()

    JE.quit()


if __name__ == "__main__":
    main()

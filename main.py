from enum import Enum
from random import randint
from time import time

import jarengine as JE


MINESWIPE: JE.Games.JEGame
WINDOW_SIZE: JE.Systems.JEVector2D
CELL_SIZE: JE.Systems.JEVector2D
GRID_OFFSET: JE.Systems.JEVector2D
FONT: JE.Resources.JEFont
board: list
FLAGS_TEXT: JE.Widgets.Graphics.JEText
MINES_TEXT: JE.Widgets.Graphics.JEText
TIME_TEXT: JE.Widgets.Graphics.JEText
NEW_GAME_BUTTON: JE.Widgets.UI.JEButton
RESET_TEXT: JE.Widgets.Graphics.JEText
RESET_BUTTON_TEXT: JE.Widgets.Graphics.JEText
WIN_TEXT: JE.Widgets.Graphics.JEText
MINE_AMOUNT = int
GRID_SIZE = tuple[int, int]

RESETTING = False
FLAGS_PLACED = 0
GAME_STARTED = False
GAME_TIME = 0
START_TIME = 0
NUMBER_COLORS = (
    (40, 40, 40),      # 0
    (0, 0, 255),       # 1
    (0, 128, 0),       # 2
    (255, 0, 0),       # 3
    (0, 0, 128),       # 4
    (128, 0, 0),       # 5
    (0, 128, 128),     # 6
    (0, 0, 0),         # 7
    (120, 120, 120),   # 8
)
MINES_GENERATED = False
GAME_OVER = False
GAME_WON = False


class CellState(Enum):
    HIDDEN = 0
    REVEALED = 1
    FLAGGED = 2


class Cell(JE.Widgets.UI.JEButton):

    def __init__(self, x, y):
        position = JE.Systems.JEVector2D(
            GRID_OFFSET.x + CELL_SIZE.x * x + 2,
            GRID_OFFSET.y + CELL_SIZE.y * y + 2
        )

        super().__init__(
            position=position,
            size=(CELL_SIZE.x - 4, CELL_SIZE.y - 4),
            outline_color=(0, 0, 0),
            outline_size=1
        )

        self.x = x
        self.y = y

        self.mine = JE.JEFalse
        self.number = 0

        self.state = CellState.HIDDEN

        self.set_callback(self.reveal, self.toggle_flag)

        self.label = JE.Widgets.Graphics.JEText(
            "",
            FONT,
            position=(position + (CELL_SIZE / 4)),
            size=CELL_SIZE,
            color=(0, 0, 0, 255),
            visibility=JE.JEFalse
        )

        self.refresh()

        MINESWIPE.add_entity(self)
        MINESWIPE.add_entity(self.label)

        board[self.y].append(self)

    def refresh(self):
        if self.state == CellState.HIDDEN:
            self.set_outline_color((0, 0, 0))
            self.label.set_visibility(JE.JEFalse)

        elif self.state == CellState.FLAGGED:
            self.set_outline_color((255, 0, 0))
            self.label.set_visibility(JE.JETrue)
            self.label.set_text("?")
            self.label.set_color((220, 0, 0))

        elif self.state == CellState.REVEALED:
            self.set_outline_color((200, 200, 200))

            if self.mine:
                self.label.set_visibility(JE.JETrue)
                self.label.set_text("*")
                self.label.set_color((255, 0, 0))

            elif self.number == 0:
                self.label.set_visibility(JE.JEFalse)

            else:
                self.label.set_visibility(JE.JETrue)
                self.label.set_text(str(self.number))
                self.label.set_color(NUMBER_COLORS[self.number])

    def get_neighbors(self):
        neighbors = []

        for y in range(self.y - 1, self.y + 2):
            for x in range(self.x - 1, self.x + 2):

                if x == self.x and y == self.y:
                    continue

                if 0 <= y < len(board) and 0 <= x < len(board[y]):
                    neighbors.append(board[y][x])

        return neighbors

    def reveal(self):
        global MINES_GENERATED, GAME_OVER, GAME_STARTED, START_TIME

        if GAME_OVER:
            return

        if self.state != CellState.HIDDEN:
            return

        if not GAME_STARTED:
            GAME_STARTED = True
            START_TIME = time()

        if not MINES_GENERATED:
            generate_mines(self)

        self.state = CellState.REVEALED
        self.refresh()

        if self.mine:
            reveal_all_mines()
            GAME_OVER = True
            self.set_color((100, 100, 100))
            return

        check_win()

        if self.number != 0:
            return

        for neighbor in self.get_neighbors():
            neighbor.reveal()

        check_win()

    def hide(self):
        self.state = CellState.HIDDEN
        self.refresh()

    def toggle_flag(self):
        global GAME_OVER, FLAGS_PLACED

        if GAME_OVER:
            return

        if self.state == CellState.HIDDEN:
            self.state = CellState.FLAGGED
            FLAGS_PLACED += 1

        elif self.state == CellState.FLAGGED:
            self.state = CellState.HIDDEN
            FLAGS_PLACED -= 1

        update_ui()
        self.refresh()


def reveal_all_mines():
    for row in board:
        for cell in row:
            cell.state = CellState.REVEALED
            cell.refresh()


def check_win():
    global GAME_OVER, GAME_WON

    for row in board:
        for cell in row:
            if not cell.mine and cell.state != CellState.REVEALED:
                return

    GAME_WON = True
    GAME_OVER = True

    for row in board:
        for cell in row:
            if cell.mine:
                cell.state = CellState.FLAGGED
                cell.refresh()

    WIN_TEXT.set_visibility(JE.JETrue)


def calculate_numbers():
    for row in board:
        for cell in row:
            if cell.mine:
                continue

            cell.number = sum(
                1
                for neighbor in cell.get_neighbors()
                if neighbor.mine
            )


def generate_cells():
    global MINESWIPE, board

    board = []

    for y in range(int(GRID_SIZE[1])):
        board.append([])
        for x in range(int(GRID_SIZE[0])):
            Cell(x, y)

    for row in board:
        for cell in row:
            cell.refresh()


def generate_mines(first_cell):
    global MINES_GENERATED

    while sum(
        1
        for row in board
        for cell in row
        if cell.mine
    ) < MINE_AMOUNT:

        x = randint(0, GRID_SIZE[0] - 1)
        y = randint(0, GRID_SIZE[1] - 1)

        cell = board[y][x]

        if cell.mine:
            continue

        # Avoid first clicked cell
        if abs(cell.x - first_cell.x) <= 1 and abs(cell.y - first_cell.y) <= 1:
            continue

        cell.mine = JE.JETrue

    calculate_numbers()

    for row in board:
        for cell in row:
            cell.refresh()

    MINES_GENERATED = True


def reset_game():
    global RESETTING

    RESETTING = True
    RESET_TEXT.set_visibility(JE.JETrue)
    WIN_TEXT.set_visibility(JE.JEFalse)


def execute_reset():
    global MINES_GENERATED, GAME_OVER, FLAGS_PLACED, GAME_STARTED, GAME_TIME, START_TIME, RESETTING, GAME_WON

    for row in board:
        for cell in row:
            MINESWIPE.entities.rm(instance=cell)
            MINESWIPE.entities.rm(instance=cell.label)

    MINES_GENERATED = False
    GAME_OVER = False
    FLAGS_PLACED = 0
    GAME_STARTED = False
    GAME_TIME = 0
    START_TIME = 0

    generate_cells()

    RESET_TEXT.set_visibility(JE.JEFalse)

    update_ui()

    MINESWIPE.refresh()

    RESETTING = False


def create_ui():
    global FLAGS_TEXT, MINES_TEXT, TIME_TEXT, NEW_GAME_BUTTON, RESET_TEXT, RESET_BUTTON_TEXT, WIN_TEXT

    FLAGS_TEXT = JE.Widgets.Graphics.JEText(
        "Flags: 0 / 80",
        FONT,
        position=(20, 20),
        size=(200, 40),
        color=(255, 255, 255)
    )

    MINES_TEXT = JE.Widgets.Graphics.JEText(
        "Mines: 80",
        FONT,
        position=(20, 60),
        size=(200, 40),
        color=(255, 255, 255)
    )

    TIME_TEXT = JE.Widgets.Graphics.JEText(
        "Time: 0s",
        FONT,
        position=(20, 100),
        size=(200, 40),
        color=(255, 255, 255)
    )


    NEW_GAME_BUTTON = JE.Widgets.UI.JEButton(
        position=(20, 150),
        size=(150, 40)
    )

    RESET_TEXT = JE.Widgets.Graphics.JEText(
        "Resetting...",
        FONT,
        position=(20, 200),
        size=(200, 40),
        color=(255, 255, 0),
        visibility=JE.JEFalse
    )

    RESET_BUTTON_TEXT = JE.Widgets.Graphics.JEText(
        "RESET",
        FONT,
        position=(40, 155),
        size=(100, 30),
        color=(0, 0, 0)
    )

    WIN_TEXT = JE.Widgets.Graphics.JEText(
        "You won!",
        FONT,
        position=(20, 250),
        size=(200, 40),
        color=(0, 255, 0),
        visibility=JE.JEFalse
    )

    NEW_GAME_BUTTON.set_callback(reset_game)

    MINESWIPE.add_entity(FLAGS_TEXT)
    MINESWIPE.add_entity(MINES_TEXT)
    MINESWIPE.add_entity(TIME_TEXT)
    MINESWIPE.add_entity(NEW_GAME_BUTTON)
    MINESWIPE.add_entity(RESET_BUTTON_TEXT)
    MINESWIPE.add_entity(RESET_TEXT)
    MINESWIPE.add_entity(WIN_TEXT)


def update_ui():
    FLAGS_TEXT.set_text(
        f"Flags: {FLAGS_PLACED} / {MINE_AMOUNT}"
    )

    MINES_TEXT.set_text(
        f"Mines: {MINE_AMOUNT}"
    )

    if GAME_STARTED:
        TIME_TEXT.set_text(
            f"Time: {int(time() - START_TIME)}s"
        )


def main():
    global MINESWIPE, WINDOW_SIZE, GRID_SIZE, CELL_SIZE, FONT, GRID_OFFSET, MINE_AMOUNT

    JE.init("/home/jarjarbin/Desktop/python/JarEngine-Games/JarMineSwipe")

    WINDOW_SIZE = JE.Systems.JEVector2D(
        JE.Interns.Config.get("window", "WINDOW", "width", int),
        JE.Interns.Config.get("window", "WINDOW", "height", int)
    )
    GRID_SIZE = tuple([int(n) for n in JE.Interns.Config.get("project", "MINESWIPE", "size", str).split(",")])
    MINE_AMOUNT = JE.Interns.Config.get("project", "MINESWIPE", "mines", int)
    cell_size = min(
        WINDOW_SIZE.x / GRID_SIZE[0],
        WINDOW_SIZE.y / GRID_SIZE[1]
    )
    CELL_SIZE = JE.Systems.JEVector2D(
        cell_size,
        cell_size
    )
    GRID_OFFSET = JE.Systems.JEVector2D(
        (WINDOW_SIZE.x - CELL_SIZE.x * GRID_SIZE[0]) / 2,
        (WINDOW_SIZE.y - CELL_SIZE.y * GRID_SIZE[1]) / 2
    )
    FONT = JE.Resources.JEFont("FontDefault", "Nasalization.otf", 20)

    JE.Interns.Helpers.assertion(GRID_SIZE[0] <= 20, "Configuration Invalid: y too big (<=20)", True)
    JE.Interns.Helpers.assertion(GRID_SIZE[1] <= 20, "Configuration Invalid: y too big (<=20)", True)
    JE.Interns.Helpers.assertion(MINE_AMOUNT <= (GRID_SIZE[0] * GRID_SIZE[1]) / 3, f"Configuration Invalid: Too many mines (<={(GRID_SIZE[0] * GRID_SIZE[1]) / 3})", True)

    MINESWIPE = JE.Games.JEGame()
    MINESWIPE.set_window(JE.Games.JEWindow())

    JE.Games.Systems.JERenderSystem(MINESWIPE)

    MINESWIPE.resources.font.add(FONT)

    generate_cells()
    create_ui()
    update_ui()

    MINESWIPE.event.add(JE.Events.Event.JEEventWatcher(JE.JEEvtQuit, lambda g, e: MINESWIPE.close()))

    MINESWIPE.refresh()

    while MINESWIPE.is_open:
        MINESWIPE.update()

        if RESETTING:
            MINESWIPE.update()
            MINESWIPE.display()
            execute_reset()
            continue

        if GAME_STARTED and not GAME_OVER:
            update_ui()

        MINESWIPE.display()


    return JE.quit()


if __name__ == "__main__":
    JE.run(main)

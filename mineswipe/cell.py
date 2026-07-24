from enum import Enum
from random import randint

import jarengine as JE


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
MINE_AMOUNT = 80
MINES_GENERATED = False
GAME_OVER = False


class CellState(Enum):
    HIDDEN = 0
    REVEALED = 1
    FLAGGED = 2


class Cell(JE.Widgets.UI.JEButton):

    def __init__(self, x, y, grid_offset, cell_size, grid_size, font):
        position = JE.Systems.JEVector2D(
            grid_offset.x + cell_size.x * x + 2,
            grid_offset.y + cell_size.y * y + 2
        )

        super().__init__(
            position=position,
            size=(cell_size.x - 4, cell_size.y - 4),
            outline_color=(0, 0, 0),
            outline_size=1
        )

        self.x = x
        self.y = y

        self.mine = JE.JEFalse
        self.number = 0

        self.state = CellState.HIDDEN

        self.grid_size = grid_size

        self.set_callback(self.reveal, self.toggle_flag)

        self.label = JE.Widgets.Graphics.JEText(
            "",
            font,
            position=(position + (cell_size / 4)),
            size=cell_size,
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
        global MINES_GENERATED, GAME_OVER

        if GAME_OVER:
            return

        if self.state != CellState.HIDDEN:
            return

        if not MINES_GENERATED:
            generate_mines(self, self.grid_size)

        self.state = CellState.REVEALED
        self.refresh()

        if self.mine:
            reveal_all_mines()
            GAME_OVER = True
            self.set_color((100, 100, 100))
            return

        if self.number != 0:
            return

        for neighbor in self.get_neighbors():
            neighbor.reveal()

    def hide(self):
        self.state = CellState.HIDDEN
        self.refresh()

    def toggle_flag(self):
        global GAME_OVER

        if GAME_OVER:
            return

        if self.state == CellState.HIDDEN:
            self.state = CellState.FLAGGED

        elif self.state == CellState.FLAGGED:
            self.state = CellState.HIDDEN

        self.refresh()


def reveal_all_mines():
    for row in board:
        for cell in row:
            cell.state = CellState.REVEALED
            cell.refresh()


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


def generate_cells(grid_size):
    board = []

    for y in range(grid_size[1]):
        board.append([])
        for x in range(grid_size[0]):
            Cell(x, y)

    for row in board:
        for cell in row:
            cell.refresh()


def generate_mines(first_cell, grid_size):
    global MINES_GENERATED

    while sum(
        1
        for row in board
        for cell in row
        if cell.mine
    ) < MINE_AMOUNT:

        x = randint(0, grid_size[0] - 1)
        y = randint(0, grid_size[1] - 1)

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

from dataclasses import dataclass

from . import deltemp, getchar
from .dot import Dot


@dataclass
class Player:
    x: int
    y: int

    def __iter__(self):
        yield self.x
        yield self.y


@dataclass
class Actiwall:
    pos: tuple[
        int, int
    ]  # original position also to return to when return pressure plate activated
    goto: tuple[int, int]
    plate: Dot
    retplate: Dot
    activated: bool = False


class EntMan:
    """entity manager"""

    def __init__(self, levels, chars) -> None:
        self.lvls = levels
        self._entities = {}

        def retTable(matrix: list[list[str | tuple]]):
            out = {}
            player_char = getchar(chars, "player")[0]
            actiwall_char = getchar(chars, "actiwall")[0]
            actiwalls: list[Actiwall] = []
            for y, row in enumerate(matrix):
                for x, char in enumerate(row):
                    if char == player_char:
                        out["player"] = Player(x, y)
                    elif isinstance(char, tuple) and char[0] == actiwall_char:
                        actiwalls.append(char[1])
            out["actiwalls"] = actiwalls
            return out

        for lvl, lmap in levels.items():
            self._entities[lvl] = retTable(lmap)

    def get(self, lvl: int, entity: str):
        return self._entities[lvl][entity]


def handlemove(chars, clvl, cmap: list, entman: EntMan, move: str, movement):
    x, y = entman.get(clvl, "player")
    U, D, L, R = movement
    move_offsets = {U: (0, -1), L: (-1, 0), D: (0, 1), R: (1, 0)}
    dx, dy = move_offsets.get(move, (0, 0))
    nx, ny = x + dx, y + dy

    if not (0 <= ny < len(cmap) and 0 <= nx < len(cmap[0])):
        return

    player_char = getchar(chars, "player")[0]
    space_char = getchar(chars, "space")[0]
    exit_char = getchar(chars, "exit")[0]
    actiwall_char = getchar(chars, "actiwall")[0]
    target = cmap[ny][nx]

    if target in (space_char, exit_char):
        cmap[y][x] = space_char
        cmap[ny][nx] = player_char
        entman._entities[clvl]["player"].x, entman._entities[clvl]["player"].y = nx, ny
        if target == exit_char:
            return "ESCAPE"

    for actiwall in entman.get(clvl, "actiwalls"):
        _gty, _gtx = actiwall.goto
        _posy, _posx = actiwall.pos
        if (  # activate actiwall
            (ny, nx) == actiwall.plate.pos
            and move == actiwall.plate.dir
            and not actiwall.activated
        ):
            actiwall.activated = True
            cmap[_gty][_gtx] = actiwall_char
            cmap[_posy][_posx] = space_char
            deltemp()
        elif (
            (ny, nx) == actiwall.retplate.pos
            and move == actiwall.retplate.dir
            and actiwall.activated
        ):
            actiwall.activated = False
            cmap[_gty][_gtx] = space_char
            cmap[_posy][_posx] = actiwall_char

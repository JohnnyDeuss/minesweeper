""" A minesweeper implementation. The functionality is exactly the same as the good ol' Windows Minesweeper: timer,
    mines, flags, question marks, auto-open when a zero is hit and auto-open when a number is clicked and the same
    number of neighbors have been flagged.
"""
from random import sample
from itertools import chain, product
from collections import namedtuple
import time
from threading import Timer
from math import ceil


class Minesweeper:
    """ A class that represents a minesweeper game.

        Attributes:
            _listeners    A list of callables that will be called when the timer changes.
            _final_time    The final timer time when the game ended, None if the game didn't end.
            _mines        The ground truth of mines; a 2D nested list of boolean values, where True marks where a mines is located.
            num_mines    The number of mines a game starts with when it's reset (for the number of mines left, see `mines_left`).
            _start_time    The time at which the first square was opened (for the timer value, see `time`), None if no square was opened yet.
            _timer        A `threading.Timer` object to update observers about timer changes.
            difficulty    The set difficulty setting, must be either 'beginner', 'intermediate', 'expert' or 'custom'.
            done        Whether the game has ended.
            height        The number of squares along the height.
            mines_left    The number of mines that are left unmarked in the game.
            state        A 2D list of the game's state, which is public to the user. The following states are possible
                        for individual squares: None for an unopened square, an integer (0-8) for open squares, 'flag'
                        for squares with a flag placed on them, 'mine_hit' for a square that was opened with a mine
                        under it, 'mine' for any unflagged squares with a mine under them after losing and 'flag_wrong'
                        for a flag that was placed on the wrong square. 'mine', 'mine_hit' and 'flag_wrong' will only
                        appear if you've lost the game.
            width        The number of squares along the width.
    """
    def __init__(self):
        """ Start a minesweeper instance. A default instance will be generated with difficulty='intermediate' and
            first_never_mine=True.
        """
        self._timer = None      # The timer used to update observers about timer changes.
        self._listeners = []    # The listeners that will get updated about timer changes.
        self._mines = None      # Will hold the ground truth for mine locations as a 2D nested list of booleans.
        self.set_config('intermediate', first_never_mine=True)

    def set_config(self, difficulty=None, width=None, height=None, num_mines=None, first_never_mine=None):
        """ Set the difficulty to one of three presets: 'beginner', 'intermediate' and 'expert'. It's also possible to
            set the difficulty to 'custom', where you can, and have to, specify the width height and the number of mines
            yourself.
        """
        if difficulty is not None:
            if difficulty == 'beginner':
                width, height, num_mines = 8, 8, 10
            elif difficulty == 'intermediate':
                width, height, num_mines = 16, 16, 40
            elif difficulty == 'expert':
                width, height, num_mines = 30, 16, 99
            elif difficulty == 'custom':
                if not (0 < num_mines < width*height):
                    raise ValueError("The number of mines doesn't make sense")
            else:
                raise ValueError('Invalid difficulty setting!')
            self.difficulty = difficulty
            self.height = height            # The height of each game.
            self.width = width              # The width of each game.
            self.num_mines = num_mines      # The number of mines to place on the board.
        if first_never_mine is not None:
            self.first_never_mine = first_never_mine
        self.reset()

    def reset(self):
        """ Starts a new game. """
        # Generate an empty state.
        self._mines = None
        self.state = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.done = False
        self.mines_left = self.num_mines
        self._start_time = None
        self._final_time = None

    def _setup_mines(self, safe_square=None):
        """ Setup the mines, not the state. The safe square allows generating a mine pattern that provides the
            `first_never_mine` functionality.
            :param safe_square: The square that should remain free from mines as an (x, y) tuple.
        """
        self._mines = [[False for _ in range(self.width)] for _ in range(self.height)]
        # Select `self.num_mines` random coordinates to place mines at.
        possible_squares = self.squares()
        # Make the safe square impossible if set.
        if safe_square is not None:
            possible_squares.remove(safe_square)
        for x, y in sample(possible_squares, self.num_mines):
            self._mines[y][x] = True

    def select(self, x, y):
        """ Select a square at the given position. If the square hasn't been selected before, dig. If it's a number and
            the neighboring squares are marked with the same number of flags as that number, the remaining neighboring
            squares are opened.
            :returns done: Whether the game has ended.
            :returns opened: The squares that were opened and what their value is.
        """
        # Mines are only determined once a square is opened, to make to `first_never_mine` option possible.
        if self._mines is None:
            self._setup_mines(safe_square=(x, y) if self.first_never_mine else None)
        # If the start time wasn't set yet, no square was opened yet, so start the timer.
        if self._start_time is None:
            self._start_timer()
        # If the game ended, nothing happens.
        if self.done:
            return Result(True, [])
        # The normal case, selecting a closed square or a question mark.
        elif self.state[y][x] is None or self.state[y][x] == '?':
            # Mine, you're dead.
            if self._mines[y][x]:
                self._stop_timer()
                opened = [OpenedSquare(x, y, 'mine_hit')]
                opened += [OpenedSquare(xi, yi, 'mine') for xi, yi in self.squares()
                           if self._mines[yi][xi] and self.state[yi][xi] in [None, '?'] and (x, y) != (xi, yi)]
                opened += [OpenedSquare(xi, yi, 'flag_wrong') for xi, yi in self.squares()
                           if not self._mines[yi][xi] and self.state[yi][xi] == 'flag']
                # Mark the opened squares on the state.
                for x, y, v in opened:
                    self.state[y][x] = v
                self.done = True
                return Result(True, opened)
            else:
                # A safe square, open it.
                number = self._count_neighboring_mines(x, y)
                self.state[y][x] = number
                opened = [OpenedSquare(x, y, number)]
                # If the number is 0, recursively open its neighbors if they haven't been opened or flagged yet.
                if number == 0:
                    opened = opened + list(chain(*[self.select(x, y)[1] for x, y in self.valid_neighbors(x, y) if self.state[y][x] is None]))
                # Check if the game was won.
                self.done = self.is_won()
                if self.done:
                    flagged = [OpenedSquare(x, y, 'flag') for x, y in self.squares() if self._mines[y][x] and self.state[y][x] != 'flag']
                    for x, y, _ in flagged[:2]:
                        self.flag(x, y)
                    opened += flagged
                    self._stop_timer()
                return Result(self.done, opened)
        # Flag, nothing happens.
        elif self.state[y][x] == 'flag':
            return Result(False, [])
        # If we clicked a number, see if we can auto-open neighbors when the same amount of flags have been placed
        # around this square as the number indicates.
        elif isinstance(self.state[y][x], int):
            # The auto-open case, where the same number of neighboring flags have been placed as the number in the square.
            if self._count_neighboring_flags(x, y) == self.state[y][x]:
                # Combine the results of all unmarked, closed neighbors recursively.
                opened = list(chain(*[self.select(x, y)[1] for x, y in self.valid_neighbors(x, y) if self.state[y][x] is None]))
                # Return all opened cells, and if any was a hit mine, that's what the result is too.
                return Result(self.done, opened)
            else:
                # The number and the neighboring flags don't add up, do nothing.
                return Result(False, [])

    def flag(self, x, y):
        """ Toggle a flag at the given position if possible, simply fail otherwise.
            :returns: True if the flag was placed, False if it can't be placed on this spot.
        """
        # The game ended, no point in placing any flags now.
        if self.done:
            return False
        # There's no flag in an empty ot '?' square, place one.
        if self.state[y][x] is None or self.state[y][x] == '?':
            self.mines_left -= 1
            self.state[y][x] = 'flag'
        # There is no
        elif self.state[y][x] == 'flag':
            self.mines_left += 1
            self.state[y][x] = None
        else:
            # In all other cases, just return False.
            return False
        return True

    def question(self, x, y):
        """ Toggle a question mark at the given position if possible, simply fail otherwise.
            :returns: True if the question mark was placed, False if it can't be placed on this spot.
        """
        # The game ended, no point in placing any flags now.
        if self.done:
            return False
        # Place or remove a flag if possible.
        if self.state[y][x] is None:
            self.state[y][x] = '?'
        if self.state[y][x] == 'flag':
            self.mines_left += 1
            self.state[y][x] = '?'
        elif self.state[y][x] == '?':
            self.state[y][x] = None
        else:
            # In all other cases, just return False.
            return False
        return True

    def valid_neighbors(self, x, y):
        """ Generate all valid coordinates of the square's neighbors. """
        # Generate all valid coordinates of the square *and* its neighbors.
        coordinates = list(product(range(max(x-1, 0), min(x+2, self.width)), range(max(y-1, 0), min(y+2, self.height))))
        # But we don't care about the center, so remove it.
        coordinates.remove((x, y))
        return coordinates

    def _count_neighboring_flags(self, x, y):
        # Now return the number of mines.
        return sum(self.state[y][x] == 'flag' for x, y in self.valid_neighbors(x, y))

    def _count_neighboring_mines(self, x, y):
        # Now return the number of mines.
        return sum(self._mines[y][x] for x, y in self.valid_neighbors(x, y))

    def is_won(self):
        """ Check if the current state is a winning one. """
        # A win is when every square that hasn't been opened is a mine, i.e. th number of unopened == `self.num_mines`.
        return self.num_mines == sum([not isinstance(self.state[y][x], int) for x, y in product(range(self.width), range(self.height))])

    def squares(self):
        """ Create a generator that iterates over all x, y coordinate pairs on the board. Squares are ordered column by
            column, row by row.
        """
        return list(product(range(self.width), range(self.height)))

    #
    # From here on, the code deal with the timer and updates.
    #
    def time(self):
        """ :returns: The time that has expired since the first square was opened. """
        if self._final_time is not None:
            return self._final_time
        if self._start_time is None:
            return 0
        return int(time.time() - self._start_time)

    def add_listener(self, listener):
        """ Add a listener to be called when the timer is updated.
            :param listener: The listener, which is a callable objectg.
        """
        # Only start the thread that deals with the timer if there are listeners.
        self._listeners.append(listener)
        # If the timer has already starter and there is no scheduler yet, start it.
        if self._timer is None and self._start_time is not None:
            self._start_scheduler()
            
    def _start_timer(self):
        """ Start the timer. """
        self._start_time = time.time()
        # Start the scheduler if we have listeners.
        if self._listeners:
            self._start_scheduler()

    def _stop_timer(self):
        """ Stop the timer. """
        self._final_time = self.time()
        self._stop_scheduler()

    def _start_scheduler(self):
        """ Start the scheduler thread that will notify listeners of timer changes. """
        if self._start_time is not None:
            t_diff = time.time() - self._start_time
            t_wait = ceil(t_diff) - t_diff
            if t_wait == 0:
                t_wait = 1
            self._timer = Timer(t_wait, self._notify)
            self._timer.start()

    def _stop_scheduler(self):
        """ Stop the scheduler thread that notified listeners of timer changes. """
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def remove_listener(self, listener):
        """ Remove a previously added timer listener. """ 
        self.listeners.remove(listener)
        if not self._listeners:
            self._stop_scheduler()

    def _notify(self):
        """ Update all observers about the timer change and queue up the next update. """
        # Call all listeners.
        for listener in self._listeners:
            listener()
        # Time next tick, start a new timer.
        self._start_scheduler()

# A tuple to store results of a dig action in.
# :param done: Whether the game has ended.
# :param opened: All the cells that were opened as a list of `OpenedSquare`s.
Result = namedtuple('Result', 'done, opened')
# A tuple to represent an opened square and its value.
OpenedSquare = namedtuple('OpenedSquare', 'x, y, value')

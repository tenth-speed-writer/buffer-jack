from typing import Iterable
from collections import deque
from copy import deepcopy
from src.sigil import Sigil


class FrameAlreadyExpired(Exception):
    """An exception raised when trying to decrement an AnimationFrame's ticks_left past zero."""
    pass


class AnimationNotRunning(Exception):
    """An exception raised when trying to tick an animation that isn't running."""
    pass


class AnimationFrame:
    """A single event in an animation sequence. Has both a sigil and a lifetime (length) in ticks.

    @param sigil The sigil to display while this event is active
    @param length The lifespan of this animation frame, in ticks"""
    def __init__(self, sigil: Sigil, length: int):
        self.sigil = sigil
        self.length = length

        # TODO: Determine if this should be length or length-1
        #  (or length + 1 because it's installed and immediately decremented?)
        self.ticks_left = length

    @property
    def has_finished(self):
        return self.ticks_left == 0

    def decrement(self):
        """Decrement ticks_left by 1, raising an exception if the value is already <= 0."""
        if self.has_finished:
            raise FrameAlreadyExpired("Called decrement on an AnimationFrame whose ticks_left is already <= 0")
        else:
            self.ticks_left -= 1


class Animation:
    """
    @param repeating
    @param frames An iterable of frames, in FIFO order."""
    def __init__(self,
                 frames=Iterable[AnimationFrame],
                 repeating: bool = False,
                 always_on_top: bool = False):
        if not frames:
            raise ValueError("Cannot create an Animation with an empty frames queue!")

        # Store the queue as a deque since we'll be left-popping it
        self._queue: deque = deque([el for el in frames])
        self.repeating = repeating

        # If the animation repeats, it'll need to remember its full frame queue.
        self._full_queue: deque = deque([el for el in frames])

        self.always_on_top = always_on_top

    @property
    def _queue_is_empty(self) -> bool:
        return len(self._queue) == 0

    @property
    def _current_frame(self) -> AnimationFrame:
        return self._queue[0]

    @property
    def running(self) -> bool:
        """An animation is running if its queue is not empty,
        if it is empty and the animation repeats,
        or if the queue is not empty but the last frame has finished."""
        empty_or_finished = self._queue_is_empty or self._current_frame.has_finished
        if empty_or_finished and self.repeating:
            return True
        elif not empty_or_finished:
            return True
        else:
            return False

    def tick(self) -> None:
        """Increments the animation by one tick, popping elements
        and (if repeating) repopulating the queue if necessary."""

        if self.running:
            if self.repeating and self._queue_is_empty:
                # Repopulate a repeating animation's queue
                self._queue = deepcopy(self._full_queue)
                self._current_frame.decrement()

            elif self._current_frame.has_finished:
                # Remove a finished animation from the start of the queue
                self._queue.popleft()

            else:
                # If nothing else to do, just decrement the current frame.
                self._current_frame.decrement()

        else:
            # Raise an exception if the animation isn't running
            raise AnimationNotRunning("Tried to tick an animation that isn't running!")

    def get_sigil(self) -> Sigil:
        return self._current_frame.sigil
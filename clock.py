from typing import Callable

LOW = False 
HIGH = True


class CPUClock:
    def __init__(self, clock_low_funcs: list[Callable[[],None]], clock_high_funcs: list[Callable[[], None]]):
        self._cur_clock_state: bool = LOW
        self._clock_low_funcs: list[Callable[[], None]] = clock_low_funcs
        self._clock_high_funcs: list[Callable[[], None]] = clock_high_funcs


    def update_low(self):
        for func in self._clock_low_funcs:
            func() # update all cpu objects to calculate their internal next state

    def update_high(self):
        for func in self._clock_high_funcs:
            func() # update all cpu objects to change their external output state to the internal calculated state

    def tick(self):
        self._cur_clock_state = not self._cur_clock_state


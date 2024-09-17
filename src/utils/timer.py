import re
import time
from typing import Callable

import glfw

from utils import Colors
from utils.messages import print_time


# class to implement a timer
class Timer:
    # constructor method
    def __init__(self) -> None:
        # intialize the starting time to the current time
        self.start = glfw.get_time()
        self.laps = {}
        self.max_laps = 5

    # method to print and obtain the elapsed time
    def elapsed(self, should_print: bool = False, should_print_fps: bool = False) -> float:
        # calculate the elapsed time since the creation or the last reset in ms
        dt = (glfw.get_time() - self.start) * 1000

        # print the time if it's instructed
        if should_print:
            print(f'Time: {round(dt, 4)}')
        if should_print_fps and dt != 0:
            print(f'FPS: {round(1000 / dt, 4)}')

        # return the elapsed time
        return dt

    # method to reset the timer
    def reset(self, laps: bool = False) -> None:
        # reset the starting time to the current time
        self.start = glfw.get_time()

        if laps:
            self.laps = {}

    def record(self, target: str = 'default') -> None:
        if target not in self.laps:
            self.laps[target] = []

        if len(self.laps[target]) == 5:
            self.laps[target].pop(0)

        self.laps[target].append(self.elapsed())

    def get_last_record(self, target: str = 'default') -> float:
        return self.laps[target][-1]


def timeit(*_wrap_args: list[any], **wrap_kwargs: dict[any]) -> None:
    def timeit_decorator(func: Callable) -> Callable:
        def timeit_wrapper(*args: list[any], **kwargs: dict[any]) -> any:
            ref = args[0] if args else None

            info_to_print = ''

            should_timer = ref is not None and 'timer' in dir(ref)
            should_print = wrap_kwargs.get('print', True)

            if wrap_kwargs.get('info', False):
                if len(info_to_print) == 0:
                    info_to_print += f'{Colors.GREY}Info{Colors.ENDC}: '

                info_to_print += ref.__str__()

            if should_timer:
                ref.timer.reset()
            start_time = time.perf_counter()

            result = func(*args, **kwargs)

            end_time = time.perf_counter()
            if should_timer:
                ref.timer.record()

            if should_print:
                total_time = end_time - start_time

                args = list(args)

                for index, arg in enumerate(args):
                    if isinstance(arg, str) and re.search('\.{0,1}(\/[a-z-_]*)*\.[a-z]{1}[a-z]*', arg):
                        args[index] = arg.split('/')[-1]

                print_time(
                    (
                        f'{Colors.GREY}Class{Colors.ENDC}: {ref.__class__.__name__} '
                        if ref.__class__.__name__ != 'NoneType'
                        else ''
                    )
                    + f'{Colors.GREY}Function{Colors.ENDC}: {func.__name__}({args}, {kwargs}) '
                    + f'{Colors.GREY}Time{Colors.ENDC}: {total_time:.4f}s '
                    # (f'{Colors.GREY}Info{Colors.ENDC}: {ref.__str__()}' if should_print_info else '')
                )

            return result

        return timeit_wrapper

    return timeit_decorator

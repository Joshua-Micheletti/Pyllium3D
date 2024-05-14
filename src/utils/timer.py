import glfw
import time
from icecream import ic
from utils.messages import *
from utils.colors import colors

# class to implement a timer
class Timer():
    # constructor method
    def __init__(self):
        # intialize the starting time to the current time
        self.start = glfw.get_time()
        self.laps = dict()
        self.max_laps = 5

    # method to print and obtain the elapsed time
    def elapsed(self, should_print = False, should_print_fps = False):
        # calculate the elapsed time since the creation or the last reset in ms
        dt = (glfw.get_time() - self.start) * 1000

        # print the time if it's instructed
        if should_print:
            print(f"Time: {round(dt, 2)}")
        if should_print_fps:
            if dt != 0:
                print(f"FPS: {round(1000 / dt, 2)}")

        # return the elapsed time
        return(dt)
    
    # method to reset the timer
    def reset(self, laps = False):
        # reset the starting time to the current time
        self.start = glfw.get_time()

        if laps:
            self.laps = dict()

    def record(self, target = "default"):
        if target not in self.laps:
            self.laps[target] = []

        if len(self.laps[target]) == 5:
            self.laps[target].pop(0)

        self.laps[target].append(self.elapsed())

    def get_last_record(self, target = "default"):
        return(self.laps[target][-1])

def timeit(*wrap_args, **wrap_kwargs):
    def timeit_decorator(func):
        def timeit_wrapper(*args, **kwargs):
            ref = args[0]
            
            should_timer = ref is not None and 'timer' in dir(ref)
            should_print = wrap_kwargs.get('print', True)
            
            if should_timer:
                ref.timer.reset()
            start_time = time.perf_counter()
            
            result = func(*args, **kwargs)
            
            end_time = time.perf_counter()
            if should_timer:
                ref.timer.record()
            
            if should_print:                
                total_time = end_time - start_time
                
                print_time(
                    f'{colors.OKBLUE + "Class" + colors.ENDC + ": " + ref.__class__.__name__ + " " if ref.__class__.__name__ else ""}' +
                    f'{colors.OKGREEN + "Function" + colors.ENDC + ": " + func.__name__} ' + 
                    f'{colors.WARNING}Time{colors.ENDC}: {total_time:.2f}s'
                )
                
            return result
        return timeit_wrapper
    return timeit_decorator



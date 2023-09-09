import glfw

# class to implement a timer
class Timer():
    # constructor method
    def __init__(self):
        # intialize the starting time to the current time
        self.start = glfw.get_time()

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
    def reset(self):
        # reset the starting time to the current time
        self.start = glfw.get_time()

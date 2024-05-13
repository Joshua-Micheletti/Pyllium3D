from utils.colors import colors
import glfw

verbose = True

def print_info(text):
    global verbose
    timestamp = ""
    if verbose:
        timestamp = '[' + str(round(glfw.get_time(), 2)) + '] '
    print(timestamp + colors.OKBLUE + text + colors.ENDC)

def print_error(text):
    global verbose
    timestamp = ""
    if verbose:
        timestamp = '[' + str(round(glfw.get_time(), 2)) + '] '
    print(timestamp + colors.ERROR + text + colors.ENDC)

def print_warning(text):
    global verbose
    timestamp = ""
    if verbose:
        timestamp = '[' + str(round(glfw.get_time(), 2)) + '] '
    print(timestamp + colors.WARNING + text + colors.ENDC)

def print_success(text):
    global verbose
    timestamp = ""
    if verbose:
        timestamp = '[' + str(round(glfw.get_time(), 2)) + '] '
    print(timestamp + colors.OKGREEN + text + colors.ENDC)
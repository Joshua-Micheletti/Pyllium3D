from utils.colors import colors
import glfw
from icecream import ic

verbose = True

def print_time(text):
    global verbose
    timestamp = (get_timestamp() if verbose else "")
    print(timestamp + text)

def print_info(text):
    global verbose
    timestamp = (get_timestamp() if verbose else "")
    print(timestamp + colors.OKBLUE + text + colors.ENDC)

def print_error(text):
    global verbose
    timestamp = (get_timestamp() if verbose else "")
    print(timestamp + colors.ERROR + text + colors.ENDC)

def print_warning(text):
    global verbose
    timestamp = (get_timestamp() if verbose else "")
    print(timestamp + colors.WARNING + text + colors.ENDC)

def print_success(text):
    global verbose
    timestamp = (get_timestamp() if verbose else "")
    print(timestamp + colors.OKGREEN + text + colors.ENDC)
 
   
def get_timestamp() -> str:
    time = str(round(glfw.get_time(), 2))
    if len(time) == 3:
        time += '0'
    timestamp = '[' + time + '] '
    return(timestamp)
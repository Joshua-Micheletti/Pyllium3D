import glfw

from utils import Colors

verbose = True


def print_time(text: str) -> None:
    global verbose
    timestamp = get_timestamp() if verbose else ''
    print(timestamp + text)


def print_info(text: str) -> None:
    global verbose
    timestamp = get_timestamp() if verbose else ''
    print(timestamp + Colors.OKBLUE + text + Colors.ENDC)


def print_error(text: str) -> None:
    global verbose
    timestamp = get_timestamp() if verbose else ''
    print(timestamp + Colors.ERROR + text + Colors.ENDC)


def print_warning(text: str) -> None:
    global verbose
    timestamp = get_timestamp() if verbose else ''
    print(timestamp + Colors.WARNING + text + Colors.ENDC)


def print_success(text: str) -> None:
    global verbose
    timestamp = get_timestamp() if verbose else ''
    print(timestamp + Colors.OKGREEN + text + Colors.ENDC)


def get_timestamp() -> str:
    time = str(round(glfw.get_time(), 2))
    if len(time) == 3:
        time += '0'
    timestamp = '[' + time + '] '
    return timestamp

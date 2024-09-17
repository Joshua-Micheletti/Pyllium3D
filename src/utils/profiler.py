import cProfile
import io
import pstats


def profile(fnc: callable) -> None:
    """A decorator that uses cProfile to profile a function"""

    def inner(*args: any, **kwargs: any) -> any:
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return retval

    return inner

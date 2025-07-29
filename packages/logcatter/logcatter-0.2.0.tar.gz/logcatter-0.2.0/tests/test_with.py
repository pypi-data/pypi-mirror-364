import sys
from time import sleep

from src.logcatter import Log

Log.setLevel(Log.VERBOSE)
with Log.print_log(show_error_stack=True):
    print("This is just print")
    print("Wait for 2 secs")
    sleep(2)
    sys.stderr.write("This is stderr message\n")

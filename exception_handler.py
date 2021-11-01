import contextlib
import logging
import os
import sys
import traceback

from PyQt5.QtWidgets import QMessageBox


def handle_exception(exc_type, exc_value, exc_traceback):
    """ handle all exceptions """

    global app

    ## KeyboardInterrupt is a special case.
    ## We don't raise the error dialog when it occurs.
    if issubclass(exc_type, KeyboardInterrupt):
        if app:
            app.quit()
        return

    filename, line, dummy, dummy = traceback.extract_tb(exc_traceback).pop()
    filename = os.path.basename(filename)
    error = "%s: %s" % (exc_type.__name__, exc_value)

    QMessageBox.critical(None, "Error",
                         "<html>A critical error has occured.<br/> "
                         + "<b>%s</b><br/><br/>" % error
                         + "It occurred at <b>line %d</b> of file <b>%s</b>.<br/>" % (line, filename)
                         + "</html>")

    print("Closed due to an error. This is the full error report:")
    print()
    print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    sys.exit(1)

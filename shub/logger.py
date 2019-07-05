'''

Copyright (C) 2017-2019 Vanessa Sochat.

This Source Code Form is subject to the terms of the
Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

'''

import os
import sys

ABRT = -4
ERROR = -3
WARNING = -2
LOG = -1
INFO = 1
QUIET = 0
VERBOSE = VERBOSE1 = 2
VERBOSE2 = 3
VERBOSE3 = 4
DEBUG = 5


class ShubMessage:

    def __init__(self, MESSAGELEVEL=None):
        self.level = get_logging_level()
        self.history = []
        self.errorStream = sys.stderr
        self.outputStream = sys.stdout
        self.colorize = self.useColor()
        self.colors = {ABRT:"\033[31m",    # dark red
                       ERROR: "\033[91m",  # red
                       WARNING:"\033[93m", # dark yellow
                       LOG:"\033[95m",     # purple
                       DEBUG:"\033[36m",   # cyan
                       'OFF':"\033[0m"}    # end sequence


    # Colors --------------------------------------------

    def useColor(self):
        '''useColor will determine if color should be added
           to a print. Will check if being run in a terminal, and
           if has support for ascii
        '''
        COLORIZE = get_user_color_preference()
        if COLORIZE is not None:
            return COLORIZE
        streams = [self.errorStream, self.outputStream]
        for stream in streams:
            if not hasattr(stream, 'isatty'):
                return False
            if not stream.isatty():
                return False
        return True


    def addColor(self, level, text):
        '''addColor to the prompt (usually prefix) if terminal
           supports, and specified to do so
        '''
        if self.colorize:
            if level in self.colors:
                text = "%s%s%s" %(self.colors[level],
                                  text,
                                  self.colors["OFF"])
        return text


    def emitError(self, level):
        '''determine if a level should print to
        stderr, includes all levels but INFO and QUIET'''
        if level in [ABRT,
                     ERROR,
                     WARNING,
                     VERBOSE,
                     VERBOSE1,
                     VERBOSE2,
                     VERBOSE3,
                     DEBUG]:
            return True
        return False


    def emitOutput(self, level):
        '''determine if a level should print to stdout
        only includes INFO'''
        if level in [LOG, INFO]:
            return True
        return False


    def isEnabledFor(self, messageLevel):
        '''check if a messageLevel is enabled to emit a level
        '''
        if messageLevel <= self.level:
            return True
        return False


    def emit(self, level, message, prefix=None):
        '''emit is the main function to print the message
           optionally with a prefix
       
           Parameters
           ==========
           level: the level of the message
           message: the message to print
           prefix: a prefix for the message
        '''

        if prefix is not None:
            prefix = self.addColor(level, "%s " % prefix)
        else:
            prefix = ""
            message = self.addColor(level, message)

        # Add the prefix 
        message = "%s%s" %(prefix, message)

        if not message.endswith('\n'):
            message = "%s\n" % message

        # If the level is quiet, only print to error
        if self.level == QUIET:
            pass

        # Otherwise if in range print to stdout and stderr
        elif self.isEnabledFor(level):
            if self.emitError(level):
                self.write(self.errorStream, message)
            else:
                self.write(self.outputStream, message)

        # Add all log messages to history
        self.history.append(message)


    def write(self, stream, message):
        '''write will write a message to a stream, 
           first checking the encoding
        '''
        if isinstance(message, bytes):
            message = message.decode('utf-8')
        stream.write(message)


    def get_logs(self, join_newline=True):
        ''''get_logs will return the complete history, joined by newline
            (default) or as is.
        '''
        if join_newline:
            return '\n'.join(self.history)
        return self.history
        


    def show_progress(self, iteration,
                      total,
                      length=40,
                      min_level=0,
                      prefix=None,
                      carriage_return=True,
                      suffix=None,
                      symbol=None):
        '''create a terminal progress bar, default bar shows for verbose+
         
           Parameters
           ==========
           iteration: current iteration (Int)
           total: total iterations (Int)
           length: character length of bar (Int)
        '''
        percent = 100 * (iteration / float(total))
        progress = int(length * iteration // total)

        if suffix is None:
            suffix = ''

        if prefix is None:
            prefix = 'Progress'

        # Download sizes can be imperfect, setting carriage_return to False
        # and writing newline with caller cleans up the UI
        if percent >= 100:
            percent = 100
            progress = length

        if symbol is None:
            symbol = "="

        if progress < length:
            bar = symbol * progress + '|' + '-' * (length - progress - 1)
        else:
            bar = symbol * progress + '-' * (length - progress)

        # Only show progress bar for level > min_level
        if self.level > min_level:
            percent = "%5s" %("{0:.1f}").format(percent)
            output = '\r' + prefix +  " |%s| %s%s %s" % (bar, percent, '%', suffix)            
            sys.stdout.write(output)
            if iteration == total and carriage_return: 
                sys.stdout.write('\n')
            sys.stdout.flush()


    def abort(self, message):
        self.emit(ABRT, message, 'ABRT')

    def error(self, message):
        self.emit(ERROR, message, 'ERROR')        

    def exit(self, message, return_code=1):
        self.emit(ERROR, message, 'ERROR')
        sys.exit(return_code)

    def warning(self, message):
        self.emit(WARNING, message, 'WARNING')

    def log(self, message):
        self.emit(LOG, message, 'LOG')        

    def info(self, message):
        self.emit(INFO, message) 

    def newline(self):
        self.write(self.outputStream, '\n')

    def verbose(self, message):
        self.emit(VERBOSE, message, "VERBOSE")        

    def verbose1(self, message):
        self.emit(VERBOSE, message, "VERBOSE1")        

    def verbose2(self, message):
        self.emit(VERBOSE2, message, 'VERBOSE2')        

    def verbose3(self, message):
        self.emit(VERBOSE3, message, 'VERBOSE3')        

    def debug(self, message):
        self.emit(DEBUG, message, 'DEBUG')

    def is_quiet(self):
        '''is_quiet returns true if the level is under 1
        '''
        if self.level < 1:
            return False
        return True
    

def get_logging_level():
    '''get_logging_level will configure a logging to standard out based on the user's
       selected level, which should be in an environment variable called
       SREGISTRY_MESSAGELEVEL. if SOM_MESSAGELEVEL is not set, the maximum level
       (5) is assumed (all messages).     
    '''
    return int(os.environ.get("SREGISTRY_MESSAGELEVEL", 5))
    

def get_user_color_preference():
    '''see in the environment if the user wants to disable colored logging'''
    COLORIZE = os.environ.get('SREGISTRY_COLORIZE', None)
    if COLORIZE is not None:
        COLORIZE = convert2boolean(COLORIZE)
    return COLORIZE


def convert2boolean(arg):
    '''convert2boolean is used for environmental variables that must be
       returned as boolean
    '''
    if not isinstance(arg, bool):
        return arg.lower() in ("yes", "true", "t", "1", "y")
    return arg

bot = ShubMessage()

#!/usr/bin/env python3

import sys
import shub.settings as cfg

if __name__ == "__main__":
    # Either dump all settings, or just the ones specified on the command line
    if len(sys.argv) == 1:
        for key, val in cfg.__dict__.items():
            if key.isupper():
                print(key,'=',val)
    else:
        for i in sys.argv[1:]:
            if i in dir(cfg):
                print(i,'=',cfg.__dict__[i])

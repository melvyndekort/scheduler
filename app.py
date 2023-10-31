#!/usr/bin/env python3
"""
Script that calls / starts the underlying modules
"""

import logging

from scheduler import scheduler


def main(target):
    '''Main method which calls the modules'''
    logging.basicConfig(level=logging.INFO)

    scheduler.main(target)


if __name__ == '__main__':
    main()

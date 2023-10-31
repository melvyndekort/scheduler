#!/usr/bin/env python3
"""
Script that calls / starts the underlying modules
"""

import logging

import trigger_web


def main(target):
    '''Main method which calls the modules'''
    logging.basicConfig(level=logging.INFO)

    trigger_web.main()


if __name__ == '__main__':
    main()

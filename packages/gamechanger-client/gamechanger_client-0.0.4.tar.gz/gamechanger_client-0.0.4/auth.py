#!/bin/python/env
# -*- coding: utf-8 -*-

from gamechanger_client import GameChangerClient


def main():
    gamechanger = GameChangerClient()
    gamechanger.auth()

if __name__ == '__main__':
    main()

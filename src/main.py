#!/usr/env/bin python3

# TODO:
# - Snake tail
# - Map type select

import sys

sys.path.append("/src")

import gamemanager_object as gmanager

def main():
    gamemanager = gmanager.GameManager()
    gamemanager.start()

if __name__ == "__main__":
    main()
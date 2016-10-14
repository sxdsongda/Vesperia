#!/usr/bin/env python
# coding:utf-8

import os
import sys
from core import main


base_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(base_dir)


if __name__ == '__main__':
    client = main.AssetClient()
    client.start()



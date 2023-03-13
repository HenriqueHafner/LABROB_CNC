"""
Created by AndyEveritt at https://github.com/AndyEveritt/GcodeParser
@author: AndyEveritt
"""

from enum import Enum
class Commands(Enum):
    COMMENT = 0
    MOVE = 1
    OTHER = 2
    TOOLCHANGE = 3

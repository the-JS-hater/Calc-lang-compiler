"""
    Module for semantic analysis of calc-lang code. Provided with a syntactically valid
    calc program, ensures that variables are not accessed before assignment
"""

#TODO should probably provide the nessecary function for code generation to work smoothly?


# IMPORTS ===============================================================================================

from syntactic_analysis import *
from lexical_analysis import KEYWORDS
from typing import ensure

# CODE ==================================================================================================


def variable_analysis(program: Program):
    variable_lookup_table = {}
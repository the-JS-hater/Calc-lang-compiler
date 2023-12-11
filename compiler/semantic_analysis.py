"""
    Module for semantic analysis of calc-lang code. Provided with a syntactically valid
    calc program, ensures that variables are not accessed before assignment
"""

#TODO should probably provide the nessecary helper functions for code generation to work smoothly?


# IMPORTS ===============================================================================================

from syntactic_analysis import *
from lexical_analysis import KEYWORDS
from typing import ensure

# CODE ==================================================================================================


def variable_analysis(program: Program):

    try:
        verify_program(program)
    except SyntaxError as e:
        raise e

    variable_lookup_table = {}
    statements = program.statements
    
    analyze_statements(statements)


def analyze_statements(statements: Statements, variable_lookup_table: dict, scope: int) -> dict:
    
    if is_empty_statements(rest_statements(statements)):
        analyze_statement(first_statement(statements))
    
    analyze_statement(first_statement(statements))
    analyze_statements(rest_statements(statements))
    


def analyze_statement(statement: Statement, variable_lookup_table: dict, scope: int) -> dict:
    keyword = get_statement_keyword(statement)

    if not keyword in KEYWORDS:
        raise SyntaxError("Non valid keyword {} at line {}".format(keyword, statement.first_token.row))
    
    if keyword == "if":
        return analyze_selection(statement)

    if keyword == "read":
        return analyze_input(statement)
    
    if keyword == "print":
        return analyze_output(statement)
    
    if keyword == "while":
        return analyze_repetition(statement)
    
    if keyword == "set":
        return analyze_assignment(statement)

    raise SyntaxError("{} is not a valid keyword, at line {}".format(keyword, statement.first_token.row))


def analyze_selection(statement: Statement, variable_lookup_table: dict, scope: int) -> dict:
    analyze_condition(statement_condition(statement, variable_lookup_table, scope))


def analyze_input(statement: Statement, variable_lookup_table: dict, scope: int) -> dict:
    pass


def analyze_output(statement: Statement, variable_lookup_table: dict, scope: int) -> dict:
    pass


def analyze_repetition(statement: Statement, variable_lookup_table: dict,  scope: int) -> dict:
    pass


def analyze_assignment(statement: Statement, variable_lookup_table: dict, scope: int) -> dict:
    pass


def analyze_expression(expression: Expression, variable_lookup_table: dict, scope: int) -> dict:
    pass


def analyze_binary_expression(binary_expression: Binary_expression, variable_lookup_table: dict, scope: int):
    pass


def analyze_condition(condiotion: Condition, variable_lookup_table: dict, scope: int) -> None:
    pass
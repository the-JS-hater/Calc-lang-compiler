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
    """Recursivley look through the calc program structure to find illegal variable access"""

    try:
        verify_program(program)
    except SyntaxError as e:
        raise e

    variable_lookup_table = {}
    statements = program.statements
    
    analyze_statements(statements)


def analyze_statements(statements: Statements, variable_lookup_table: dict, scope: int) -> dict:
    """Recursivley go through the statements structure"""
    
    if is_empty_statements(rest_statements(statements)):
        analyze_statement(first_statement(statements))
    
    analyze_statement(first_statement(statements))
    analyze_statements(rest_statements(statements))
    


def analyze_statement(statement: Statement, variable_lookup_table: dict, scope: int) -> dict:
    """Validate a Statement's variable safety"""

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
    """Pick apart a selection statement and validate variable safety"""

    analyze_condition(statement_condition(statement, variable_lookup_table, scope))
    variable_lookup_table = analyze_statement(selection_true_branch(statement, variable_lookup_table, scope + 1))

    if selection_has_false_branch(statement):
        variable_lookup_table = analyze_statement(selection_false_branch(statement), variable_lookup_table, scope + 1)

    return variable_lookup_table


def analyze_input(statement: Statement, variable_lookup_table: dict, scope: int) -> dict:
    """Add the input variable to the variable lookup table"""

    variable_lookup_table[input_variable(statement)] = scope
    return variable_lookup_table


def analyze_output(statement: Statement, variable_lookup_table: dict, scope: int) -> None:
    """Validate the variable safety of the output espression"""

    if is_constant(output_expression(statement)):
        return

    if is_variable(output_expression(statement)):
        variable = output_expression(statement)
        if not variable in variable_lookup_table:
            raise SyntaxError("Undefined variable {} at line {}".format(variable, statement.first_token.row))
        
        if variable_lookup_table[variable] > scope:
            raise SyntaxError("Variable {} refrenced before assignment at line {}".format(variable, statement.first_token.row))
        
    if is_binary_expression(output_expression(statement)):
        analyze_binary_expression(output_expression(statement))

    raise SyntaxError("Invalid expression {} at line {}".format(output_expression(statement), statement.first_token.row))
    

def analyze_repetition(statement: Statement, variable_lookup_table: dict,  scope: int) -> dict:
    """Validate the variable statements of a repetition statement """
    return analyze_statements(repetition_statements(statement), variable_lookup_table, scope + 1)


def analyze_assignment(statement: Statement, variable_lookup_table: dict, scope: int) -> dict:
    """Add the assignment variable to the variable lookup table"""

    variable_lookup_table[assignment_variable(statement)] = scope
    return variable_lookup_table


def analyze_expression(expression: Expression, variable_lookup_table: dict, scope: int) -> dict:
    
    if is_constant(expression):
        return
    
    if is_variable(expression):
        variable = expression_variable(expression)
        
        if not variable in variable_lookup_table:
            raise SyntaxError() # TODO format this
        
        if variable_lookup_table[variable] > scope:
            raise SyntaxError()
        
        return

    if is_binary_expression(expression):
        analyze_binary_expression(expression, variable_lookup_table, scope + 1)

    raise SyntaxError() #TODO format error message


def analyze_binary_expression(binary_expression: Binary_expression, variable_lookup_table: dict, scope: int):
    analyze_expression(left_expression(binary_expression), variable_lookup_table, scope + 1)
    is_binary_operator(get_binary_operator(binary_expression))
    analyze_expression(right_expression(binary_expression), variable_lookup_table, scope + 1)

    return

def analyze_condition(condiotion: Condition, variable_lookup_table: dict, scope: int) -> None:
    pass
"""
    A module for handling parsing a list of Token's into an abstract syntax tree
"""

# IMPORTS ===============================================================================================

from lexical_analysis import Token
from typing import NamedTuple, Union, Optional
import sys

sys.tracebacklimit = 0  # Only wanna get my compilers error message

#TODO remove later, for testing
from lexical_analysis import perform_lexical_analysis

# STRUCTS ================================================================================================

Program = NamedTuple("Program", [
    ("keyword", str),
    ("statements", NamedTuple),
    ("first_token", Token)
])

Statements = NamedTuple("Statements", [
    ("first_statement", NamedTuple),
    ("rest_statement", list[NamedTuple]),
    ("first_token", Token)
])

Statement = NamedTuple("Statement", [
    ("statement_type", str),
    ("statement", NamedTuple),
    ("first_token", Token)
])

Assignment = NamedTuple("Assignment", [
    ("keyword", str),
    ("variable", str),
    ("expression", NamedTuple),
    ("first_token", Token)
])

Repetition = NamedTuple("Repetition", [
    ("keyword", str),
    ("condition", NamedTuple),
    ("repetition_statements", NamedTuple),
    ("first_token", Token)
])

Selection = NamedTuple("Selection", [
    ("keyword", str),
    ("condition", NamedTuple),
    ("true_branch_statement", NamedTuple),
    ("false_branch_statement", Optional[NamedTuple]),
    ("first_token", Token)
])

Input = NamedTuple("Input", [
    ("keyword", str),
    ("variable", str),
    ("first_token", Token)
])

Output = NamedTuple("Output", [
    ("keyword", str),
    ("output_expression", NamedTuple),
    ("first_token", Token)
])

Expression = NamedTuple("Expression", [
    ("expression_type", str),
    ("constant", Optional[Union[int, float]]),
    ("variable", Optional[str]),
    ("binary_expression", Optional[NamedTuple]),
    ("first_token", Token)
])

Binary_expression = NamedTuple("Binary_expression", [
    ("left_expression", NamedTuple),
    ("binary_oper", str),
    ("roght_expression", NamedTuple),
    ("first_token", Token)
])

Condition = NamedTuple("Condition", [
    ("left_expression", NamedTuple),
    ("condoper", str),
    ("right_expression", NamedTuple),
    ("first_token", Token)
])


# PARSE ==================================================================================================


def parse_program(token_vec: list[Token]) -> Program:
    """Returns if possible a Program struct ['calc', Statements], if possible else raises an error"""

    if not token_vec:
        raise ValueError("No source code found")

    if not token_vec[0].token_type == "open_bracket":
        raise SyntaxError("Expected [ before 'calc'")
    
    calc_token = token_vec[1]
    keyword = calc_token.lexeme
    if not keyword == 'calc':
        raise SyntaxError("Missing keyword {}".format(keyword))
    
    open_bracket = token_vec[2].token_type
    if not open_bracket == "open_bracket":
        line = calc_token.row
        raise SyntaxError("Missing [ after {} line {}".format(keyword, line))
    
    try:
        statements, token_vec = parse_statements(token_vec[2:], [])
    except SyntaxError as e:
        raise e
    
    return Program('program', statements, calc_token)
    

def parse_statements(token_vec: list[Token], statements) -> tuple[Statements, list[Token]]:
    """parses the list of tokens into a Statements struct, which means building a list of Statement structs"""

    if not token_vec:
        raise SyntaxError("Program contains no statements")
    
    current_token = token_vec[0]
    try: 
        if current_token.token_type == "closed_bracket":
            if not statements:
                raise SyntaxError("Exprected statement at line {}".format(current_token.row))
            
            check_bracket_closure(token_vec)
            return Statements(statements[0], statements[1:], current_token), token_vec

        if current_token.token_type == "open_bracket":
            statement, token_vec = parse_statement(token_vec[1:])
            statements.append(statement)
            statements, token_vec = parse_statements(token_vec, statements)
            return statements, token_vec[1:]
    except SyntaxError as e:
        raise e

    raise SyntaxError("Exprected ] after {} at line {}".format(current_token.lexeme, current_token.row))


def parse_statement(token_vec: list[Token]) -> tuple[Statement, list[Token]]:
    """Used to parse an induvidual statement, based on it's keyword"""

    first_token = token_vec[0]
    if not first_token.token_type == "keyword":
        return SyntaxError("Expected a keyword at line {}".format(first_token.row))
    
    keyword = first_token.lexeme

    try:
        if keyword == "set":
            statement, token_vec = parse_assignment(token_vec)
            return Statement("assignment", statement, first_token), token_vec
        
        if keyword == "while":
            statement, token_vec = parse_repetition(token_vec)
            return Statement("repetition", statement, first_token), token_vec

        if keyword == "if":
            statement, token_vec = parse_selection(token_vec)
            return Statement("selection", statement, first_token), token_vec

        if keyword == "read":
            statement, token_vec = parse_input(token_vec)
            return Statement("input", statement, first_token), token_vec

        if keyword == "print":
            statement, token_vec = parse_output(token_vec)
            return Statement("output", statement, first_token), token_vec
    
    except SyntaxError as e:
        raise e
    
    raise SyntaxError("Expected statement keyword, found {} at line {}".format(keyword, first_token.row))


def parse_assignment(token_vec: list[Token]) -> tuple[Assignment, list[Token]]:
    """Parse an assignment statement with form [set, var, epxression]"""

    first_token, variable = token_vec[:2]
    
    if not variable.token_type == "variable":
        raise SyntaxError("Expected variable name, found {} : {}, at line {}".format(variable.token_type, variable.lexeme, variable.row))
    
    try:
        expression, token_vec = parse_expression(token_vec[2:])
        check_bracket_closure(token_vec)

    except SyntaxError as e:
        raise e

    return Assignment(first_token.lexeme, variable, expression, first_token), token_vec[1:]  


def parse_repetition(token_vec: list[Token]) -> tuple[Repetition, list[Token]]:
    """Parse a repetition statement with form [while, condition, statements]"""

    first_token = token_vec[0]

    try:

        condition, token_vec = parse_condition(token_vec[1:])
        statements, token_vec = parse_statements(token_vec[1:])

        check_bracket_closure(token_vec)

    except SyntaxError as e:
        raise e
    
    return Repetition(first_token.lexeme, condition, statements, first_token), token_vec[1:]


def parse_selection(token_vec: list[Token]) -> tuple[Selection, list[Token]]:
    """Parse a selection statement with form [if, condition, statement, optional[statement]]"""

    first_token = token_vec[0]
    try:
        condition, token_vec = parse_condition(token_vec[1:])
        true_branch, token_vec = parse_statement(token_vec[1:])
    

        next_token_type = token_vec[0].token_type
        
        if next_token_type == "closed_bracket":
            check_bracket_closure(token_vec)
            
            return Selection(first_token.lexeme, condition, true_branch, first_token=first_token), token_vec[1:]
    
        false_branch, token_vec = parse_statement(token_vec[1:])
        check_bracket_closure(token_vec)
    
    except SyntaxError as e:
        raise e
    
    return Selection(first_token.lexeme, condition, true_branch, false_branch, first_token), token_vec[1:]


def parse_input(token_vec: list[Token]) -> tuple[Input, list[Token]]:
    """Parse an input statement with form [read, var]"""

    first_token, variable = token_vec[:2]

    try:
        check_bracket_closure(token_vec[2:])

    except SyntaxError as e:
        raise e

    return Input(first_token.lexeme, variable, first_token), token_vec[3:]


def parse_output(token_vec: list[Token]) -> tuple[Output, list[Token]]:
    """Parse an output statement with form [print, expression]"""

    first_token = token_vec[0]

    try:
        expression, token_vec = parse_expression(token_vec[1:])
        check_bracket_closure(token_vec)

    except SyntaxError as e:
        raise e
    
    return Output(first_token.lexeme, expression, first_token), token_vec[1:]


def parse_expression(token_vec: list[Token]) -> tuple[Expression, list[Token]]:
    """Parse an expression, which can be either a variable, constant or a binary expression"""

    first_token = token_vec[0]

    if first_token.token_type == "constant":
        return Expression(expression_type = first_token.token_type, variable = None, constant = first_token.lexeme, binary_expression = None, first_token = first_token), token_vec[1:]

    if first_token.token_type == "variable":
        return Expression(expression_type = first_token.token_type, variable = first_token.lexeme, constant = None, binary_expression = None, first_token = first_token), token_vec[1:]
    
    if first_token.token_type == "open_bracket":
        try:
            binary_expression, token_vec = parse_binary_expression(token_vec[1:])

        except SyntaxError as e:
            raise e
        
        return Expression(expression_type= first_token.token_type, binary_expression= binary_expression, constant = None, variable = None, first_token= first_token), token_vec

    raise SyntaxError("Invalid expression {}, at line {}".format(first_token.lexeme, first_token.row))
    

def parse_binary_expression(token_vec: list[Token]) -> tuple[Binary_expression, list[Token]]:
    """Parse a binary expression with form [expression, operator, expression]"""

    try:
        left_expression, token_vec = parse_expression(token_vec)

        operator = token_vec[0]

        if not operator.token_type == "binaryoper":
            raise SyntaxError("Exprected binary operator, found {} at line {}".format(operator.lexeme, operator.row))
    
        right_expression, token_vec = parse_expression(token_vec[1:])
        check_bracket_closure(token_vec)

    except SyntaxError as e:
        raise e
    
    return Binary_expression(left_expression, operator.lexeme, right_expression, left_expression), token_vec[1:]


def parse_condition(token_vec: list[Token]) -> tuple[Condition, list[Token]]:
    """Parse a condition with form [expression, operator, expression]"""

    try:
        left_expression, token_vec = parse_expression(token_vec)

        operator = token_vec[0]

        if not operator.token_type == "condoper":
            raise SyntaxError("Exprected conditional operator, found {} at line {}".format(operator.lexeme, operator.row))
    
        right_expression, token_vec = parse_expression(token_vec[1:])
        check_bracket_closure(token_vec)

    except SyntaxError as e:
        raise e
     
    return Condition(left_expression, operator.lexeme, right_expression, left_expression), token_vec[1:] 


def check_bracket_closure(token_vec: list[Token]) -> None:
    """Called to ensure open brackets are properly closed"""

    if not token_vec[0].token_type == "closed_bracket":
            raise SyntaxError("Expected ] found {} at line {}".format(token_vec[0].lexeme, token_vec[0].row))


# TREE= =================================================================================================


def build_AST_tree(token_vec: list[Token]): # Return root-node pointer
    pass


# MAIN ==================================================================================================

#TODO test this shit

if __name__ == "__main__":
    pass
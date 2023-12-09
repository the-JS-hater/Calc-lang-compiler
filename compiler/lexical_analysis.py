"""
    A module for handling the first step of compilation: lexical analysis
"""

# IMPORTS ===============================================================================================

from typing import NamedTuple, Union

# STRUCTS ================================================================================================

Token = NamedTuple("Token", [
    ("token_type", str),
    ("lexeme", Union[int, float, str]),
    ("row", int),
    ("column", int)
])

# CONST VARIABLES ========================================================================================

KEYWORDS = (
    "calc",
    "set",
    "print",
    "read",
    "while",
    "if",
)

BINNARYOPER = (
    "+",
    "-",
    "*",
    "/"
)

CONDOPER = (
    "<",
    ">",
    "="
)

ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

# CODE ===================================================================================================

def perform_lexical_analysis(filepath: str) -> list[Token]:
    """Is called with a relative path to a .txt with calc code, in order to tokenize it's content"""   

    input = read_input(filepath)
    print(" vvv INPUT vvv")
    print(input)
    print(" ")
    token_vector = tokenize(input, '', False, 1, 1)

    return token_vector


def tokenize(stream: str, lexeme: str, reading_num: bool, current_row: int, current_column: int) -> list[Token]:
    """
        Recursivley performs lexical analysis, reading one char at a time and creating tokens when
        appropriate.

        At the end it returns a list of tokens, in the order they appeared in the original input
    """

    if not stream:
        return []
    
    c = stream[0]

    if c == '\n':
        if not lexeme:
            return tokenize(stream[1:], '', False, current_row + 1, 1)
        
        token = handle_previous_token(reading_num, lexeme, current_row, current_column)
        return [token] + tokenize(stream[1:], '', False, current_row + 1, 1)

    if c == '[':
        token = Token("open_bracket", c, current_row, current_column)
        return [token] + tokenize(stream[1:], '', False, current_row, current_column + 1)
    
    if c == ']':
        current_token = Token("closed_bracket", c, current_row, current_column + 1)
        if not lexeme:
            return [current_token] + tokenize(stream[1:], '', False, current_row, current_column + 2)

        prev_token = handle_previous_token(reading_num, lexeme, current_row, current_column)
        return [prev_token, current_token] + tokenize(stream[1:], '', False, current_row, current_column + 2)
    
    if c == '\'':
        if not lexeme:
            return tokenize(stream[1:], '', False, current_row, current_column)
        
        token = handle_previous_token(reading_num, lexeme, current_row, current_column)
        return [token] + tokenize(stream[1:], '', False, current_row, current_column + 1)

    if c == ' ' or  c == '\t' or c == ',':
        if not lexeme:
            return tokenize(stream[1:], '', False, current_row, current_column)
        
        token = handle_previous_token(reading_num, lexeme, current_row, current_column)
        return [token] + tokenize(stream[1:], '', False, current_row, current_column + 1)

    if c == '.':
        lexeme += c
        return tokenize(stream[1:], lexeme, True, current_row, current_column)
    
    if c in ALPHABET:
        lexeme += c
        return tokenize(stream[1:], lexeme, False, current_row, current_column)
    
    if c in CONDOPER or c in BINNARYOPER:
        token_type = eval_token_type(c)
        token = Token(token_type, c, current_row, current_column)
        return [token] + tokenize(stream[1:], '', False, current_row, current_column + 1)
    
    if is_num(c):
        lexeme += str(c)
        return tokenize(stream[1:], lexeme, True, current_row, current_column)
    
    else:
        #TODO work on error messaging
        raise SyntaxError("Unrecognized symbol {} line {}".format(c, current_row))


def handle_previous_token(num: bool, lexeme: str, row: int, column) -> list[Token]:
    if num:
        token_type = "constant"
        lexeme = eval_constant_type(lexeme)
    else:
        token_type = eval_token_type(lexeme)
        
    return Token(token_type, lexeme, row, column)


def eval_constant_type(lexeme: str) -> Union[int, float]:
    """evaluates if lexeme is an int or float and returns it's typecasted value"""

    if '.' in lexeme:
        return float(lexeme)
    
    return int(lexeme)


def eval_token_type(lexeme: str) -> str:
    """evaluates if a given lexeme is an operator, keyword or variable"""

    if lexeme in CONDOPER:
        return "condoper"
    
    if lexeme in BINNARYOPER:
        return "binaryoper"
    
    if lexeme in KEYWORDS:
        return "keyword"
    
    return "variable"


def read_input(filepath: str) -> str:
    with open(filepath, "r") as file:
        stream = file.read()
    
    return stream


def is_num(num: str) -> bool:
    """tells you if string isnumeric or can be cast to a float"""

    try:
        float(num)
        return True
    except ValueError:
        True


def print_token(token: Token) -> None:
    """Prints a formated string of a Token's data"""
    print("Type: {}, Lexeme: {}, Row: {}, Column: {} \n".\
          format(
              token.token_type,
              token.lexeme,
              token.row,
              token.column
          ))

# TESTS =================================================================================================


if __name__ == "__main__":
    pass
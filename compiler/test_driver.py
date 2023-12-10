"""
    A module for running various tests on the compiler, and features alot of debug print functions
"""

# IMPORTS ===============================================================================================

from lexical_analysis import perform_lexical_analysis, Token
from syntactic_analysis import parse_program, Program, Statements, Statement

# PRINTS ================================================================================================

def print_AST(program: Program):

    print("============ vvv AST nodes vvv =============")
    print("Root node: " + program.keyword)

    statements = program.statements
    
    print("Program Staments: ")
    print(statements.first_statement.statement_type)
    for statement in statements.rest_statement:
        print(statement.statement_type)

    print("============================================")


def print_token_list(token_vec: list[Token]):

    print("============== vvv Tokens vvv ===============")
    for token in token_vec:
        print("{} {} line {} index {}".format(token.token_type, token.lexeme, token.row, token.column))

    print("============================================")

# MAIN ==================================================================================================

if __name__ == "__main__":
        
        
        token_vec = perform_lexical_analysis("programs\\easy_prog.txt")
            
        program = parse_program(token_vec)
        print_token_list(token_vec)
        print_AST(program)
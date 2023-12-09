"""
    A psuedo-compilator for the imaginary programming language calc
    from lab6 in TDDE24.

    It parses a .txt containing calc programs and creates a .py file 
    with a python function for each proram. 

    FEATURES:
        - Variable safety (maybe)
        - Syntax safety (maybe)
        - Alot of bugs (Probably) 
"""


from calc import *
import os

def compile_calc(filename: str) -> None:
    """Compiles a constCalc .txt into python file"""
    if not os.path.exists(filename):
        return ValueError("Couldn't locate file: " + filename)
    source_file = open(filename)
    source_program = source_file.readlines()
    compiled_program = create_new_file(filename)
    try:
        for func in source_program:
            func_str = parse_function(func)
            compiled_program.write(func_str)
        compiled_program.close()
    except SyntaxError as exc:
        delete_file(compiled_program)
        raise exc
   
    
def create_new_file(filename: str):
    """Creates a new .py file and returns it"""
    program_name = filename.split('.')[0] + ".py"
      
    if os.path.exists(program_name):
        return FileExistsError("Filename is taken")
    
    program_file = open(program_name, "x")
    program_file = open(program_name, "a")
    return program_file


def delete_file(file) -> None:
    """removes the file, called if a compilation error occurs"""
    file.close()
    os.remove(file.name)

    
    
def parse_function(function: str) -> str:
    "converts a calc function into a string of python code"
    split_func_str = function.split(" = ")
    function_name = split_func_str[0].strip()  #.split() can probably be removed
    function_statements = program_statements(eval(split_func_str[1]))
    return "def " + function_name + "():" + "\n" + parse_statements(function_statements, 1, []) + "\n\n\n"
    
    
def parse_statements(statements: list, indentation = 1, variables_in_scope = []) -> str:
    "recursivley parses statements into a string of python code"
    if not is_statements(statements):
        raise SyntaxError("Statements are incorrectly formatted: " + str(statements))
    
    output = ""
    first = first_statement(statements)
    rest = rest_statements(statements)
    try:
        output += parse_statement(first, indentation, variables_in_scope)
    except SyntaxError as exc:
        raise exc
    
    if empty_statements(rest):
        return output
    else:
        return output + "\n" + parse_statements(rest, indentation, variables_in_scope)
        
    
def parse_statement(statement: list, indentation = 1, variables_in_scope = []) -> str:
    """parse a single statement into a string of python code"""
    
    if not is_statement(statement):
        return SyntaxError("Statement {statement} is incorrectly formatted".format(statement))
    try:
        if is_output(statement):
            return parse_output(statement, indentation, variables_in_scope)
        
        elif is_assignment(statement):
            return parse_assignment(statement, indentation, variables_in_scope)
        
        elif is_input(statement):
            return parse_input(statement, indentation, variables_in_scope)
        
        elif is_selection(statement):
            return parse_selection(statement, indentation, variables_in_scope)
        
        elif is_repetition(statement):
            return parse_repetition(statement, indentation, variables_in_scope)
    except SyntaxError as exc:
        raise exc


def parse_selection(statement: list, indentation = 1, variables_in_scope = []) -> str:
    """Converts a selection statement into a string of python code"""
    try:
        condition = parse_condition(selection_condition(statement), indentation, variables_in_scope)
        output = indentation * "\t" + "if " + condition + ":\n"
        output += parse_statement(selection_true_branch(statement), indentation + 1, variables_in_scope)
        
        if selection_has_false_branch(statement):
            output += "\n" + indentation * "\t" + "else:\n" + parse_statement(selection_false_branch(statement), indentation + 1, variables_in_scope)
            
        return output
    except SyntaxError as exc:
        raise exc


def parse_repetition(statement: list, indentation = 1, variables_in_scope = []) -> str:
    """Converts a repetition statement into a string of python code"""
    try:
        condition = parse_condition(repetition_condition(statement), indentation, variables_in_scope)
        output = indentation * "\t" + "while " + condition + ":\n"
        return output + parse_statements(repetition_statements(statement), indentation + 1, variables_in_scope)
    except SyntaxError as exc:
        raise exc
    

def parse_output(statement: list, indentation = 1, variables_in_scope = []) -> str:
    """Convert an output statement into a string of python code"""
    try:
        return indentation * "\t" + "print(" + parse_expression(output_expression(statement), indentation, variables_in_scope) + ")"
    except SyntaxError as exc:
        raise exc

def parse_assignment(statement: list, indentation = 1, variables_in_scope = []) -> str:
    """Converts an assignment statement into a string of python code"""

    var_flag = True

    for ind, var  in variables_in_scope:
        if assignment_variable(statement) == var and ind <= indentation:
            var_flag = False

    if var_flag:
        variables_in_scope.append((indentation, assignment_variable(statement)))

    return indentation * "\t" + assignment_variable(statement) + " = " + parse_expression(assignment_expression(statement), indentation, variables_in_scope)


def parse_input(statement: list, indentation = 1, variables_in_scope = []) -> str:
    """Converts an input statement into a string of python code"""
    variables_in_scope.append((indentation, input_variable(statement)))
    return indentation * "\t" + input_variable(statement) + " = " + "int(input())"


def parse_expression(expression, indentation = 1, variables_in_scope = []) -> str:
    """parse an expression into a string"""
    if is_variable(expression):
        for ind, var in variables_in_scope:
            if expression == var and indentation >= ind:
                return expression
            
        raise SyntaxError("Variable {0} refrenced before assignment".format(expression))
    
    if is_constant(expression):
        return str(expression)
    
    if is_binaryexpr(expression):
        try:
            return parse_binary_expression(expression, indentation, variables_in_scope)
        except SyntaxError as exc:
            raise exc


def parse_binary_expression(binaryexpr: list, indentation = 1, variables_in_scope = []) -> str:
    """parse a binary expression into a string"""
    try:
        left_str = parse_expression(binaryexpr_left(binaryexpr), indentation, variables_in_scope)
        operator = binaryexpr_operator(binaryexpr)
        right_str = parse_expression(binaryexpr_right(binaryexpr), indentation, variables_in_scope)
        return left_str + " " + operator + " " + right_str
    except SyntaxError as exc:
        raise exc


def parse_condition(condition: list, indentation = 1, variables_in_scope = []) -> str:
    """parses a condition expression into a string"""
    try:
        left_expr = parse_expression(condition_left(condition), indentation, variables_in_scope)
        right_expr = parse_expression(condition_right(condition), indentation, variables_in_scope)
        if condition_operator(condition) == "=":
            condoper = "=="
        else:
            condoper = condition_operator(condition)
        
        return left_expr + " " + condoper + " " + right_expr
    except SyntaxError as exc:
        raise exc    


def parse_variable(variable: str) -> str:
    """Simply return the variable name"""
    return variable
    
    
if __name__ == "__main__":
    compile_calc("funcs.txt")
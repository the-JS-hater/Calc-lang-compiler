# ----------------------------------------------------------------------------
#  Primitive functions for the ConstCalc and Calc language constructs
# ----------------------------------------------------------------------------


# ----- PROGRAM -----


def is_program(p):
    return isinstance(p, list) and len(p) > 1 and p[0] == 'calc'


def program_statements(p):
    # The first item is 'calc', the rest are the statements
    return p[1:]


# ----- STATEMENTS -----


def is_statements(p):
    # A non-empty list of statements
    return isinstance(p, list) and p and all(is_statement(s) for s in p)


def first_statement(p):
    return p[0]


def rest_statements(p):
    return p[1:]


def empty_statements(p):
    return not p


# ----- STATEMENT -----


def is_statement(s):
    return (
        is_assignment(s)
        or is_repetition(s)
        or is_selection(s)
        or is_output(s)
        or is_input(s)
    )


# ----- ASSIGNMENT -----


def is_assignment(p):
    return isinstance(p, list) and len(p) == 3 and p[0] == 'set'


def assignment_variable(p):
    return p[1]


def assignment_expression(p):
    return p[2]


# ----- REPETITION -----


def is_repetition(p):
    return isinstance(p, list) and len(p) > 2 and p[0] == 'while'


def repetition_condition(p):
    return p[1]


def repetition_statements(p):
    return p[2:]


# ----- SELECTION -----


def is_selection(p):
    return isinstance(p, list) and (3 <= len(p) <= 4) and p[0] == 'if'


def selection_condition(p):
    return p[1]


def selection_true_branch(p):
    return p[2]


def selection_has_false_branch(p):
    return len(p) == 4


def selection_false_branch(p):
    return p[3]


# ----- INPUT -----


def is_input(p):
    return isinstance(p, list) and len(p) == 2 and p[0] == 'read'


def input_variable(p):
    return p[1]


# ----- OUTPUT -----


def is_output(p):
    return isinstance(p, list) and len(p) == 2 and p[0] == 'print'


def output_expression(p):
    return p[1]


# ----- EXPRESSION -----

# No functions for expressions in general. Instead, see the differenct
# types of expressions: constants, variables and binary expressions.


# ----- BINARYEXPR -----


def is_binaryexpr(p):
    return isinstance(p, list) and len(p) == 3 and is_binaryoper(p[1])


def binaryexpr_operator(p):
    return p[1]


def binaryexpr_left(p):
    return p[0]


def binaryexpr_right(p):
    return p[2]


# ----- CONDITION -----


def is_condition(p):
    return isinstance(p, list) and len(p) == 3 and is_condoper(p[1])


def condition_operator(p):
    return p[1]


def condition_left(p):
    return p[0]


def condition_right(p):
    return p[2]


# ----- BINARYOPER -----


def is_binaryoper(p):
    return p in ['+', '-', '*', '/']


# ----- CONDOPER -----


def is_condoper(p):
    return p in ['<', '>', '=']


# ----- VARIABLE -----


def is_variable(p):
    return isinstance(p, str) and p != ""

# ----- CONSTANT -----


def is_constant(p):
    return isinstance(p, int) or isinstance(p, float)


# ----------------------------------------------------------------------------
#  Grammar for the *complete* Calc language
# ----------------------------------------------------------------------------

"""

    (* FÃ¶r att vi inte sjÃ¤lva ska rÃ¥ka lÃ¤sa fel och blanda ihop EBNF-komma
    och det ',' som ingÃ¥r i vÃ¥rt sprÃ¥k skapar vi en icke-terminal fÃ¶r detta... *)
    COMMA = ',' ;

    (* Ett program bestÃ¥r av en fÃ¶ljd av satser.  Eftersom ordet calc ska stÃ¥ inom 
    apostrofer behÃ¶ver vi lÃ¤gga detta inom citattecken i grammatiken. JÃ¤mfÃ¶r med att 
    hakparenteserna ska vara utan apostrofer i vÃ¥rt sprÃ¥k, men *har* en nivÃ¥ av 
    apostrofer i grammatiken. *)
    PROGRAM = '[', "'calc'", COMMA, STATEMENTS, ']' ;

    (* STATEMENTS Ã¤r ett ensamt STATEMENT, eller ett STATEMENT fÃ¶ljt av komma 
           och STATEMENTS (som i sin tur Ã¤r 1 STATEMENT som mÃ¶jligen fÃ¶ljs av flera,
        och sÃ¥ vidare).  *)
    STATEMENTS = 
        STATEMENT
      | STATEMENT, COMMA, STATEMENTS ;
    
    (* En sats kan vara en tilldelning, en upprepning, ett val,
       en inmatning eller en utmatning. *)
    STATEMENT =
        ASSIGNMENT
      | REPETITION
      | SELECTION
      | INPUT
      | OUTPUT ;

    (* En tilldelning bestÃ¥r av en variabel och ett uttryck vars vÃ¤rde ska berÃ¤knas
       fÃ¶r att sedan kopplas till det givna variabelnamnet. *)
    ASSIGNMENT = '[', "'set'", COMMA, VARIABLE, COMMA, EXPRESSION, ']' ;

    (* En upprepning bestÃ¥r av ett villkorsuttryck och en fÃ¶ljd av satser,
       vilka upprepas sÃ¥ lÃ¤nge villkorsuttrycket Ã¤r sant.  *)
    REPETITION = '[', "'while'", COMMA, CONDITION, COMMA, STATEMENTS, ']' ;

    (* Ett val bestÃ¥r av ett villkorsuttryck fÃ¶ljt av en eller tvÃ¥ satser.
       Den fÃ¶rsta satsen utfÃ¶rs om villkorsuttrycket Ã¤r sant,
       den andra (om den finns) om villkorsuttrycket Ã¤r falskt.
       Notera att [ ... ] betyder att det som stÃ¥r inom hakparenteserna
       fÃ¥r utelÃ¤mnas ("optional").  *)
    SELECTION = '[', "'if'", COMMA, CONDITION, COMMA, STATEMENT, [COMMA, STATEMENT], ']'

    (* En inmatningssats anger namnet pÃ¥ en variabel som ska fÃ¥ ett
       numeriskt vÃ¤rde av anvÃ¤ndaren. *)
    INPUT = '[', "'read'", COMMA, VARIABLE, ']' ;

    (* En utmatningssats anger ett uttryck vars vÃ¤rde ska skrivas ut. *)
    OUTPUT = '[', "'print'", COMMA, EXPRESSION, ']' ;

    (* Ett matematiskt uttryck kan vara en konstant, en variabel eller
       ett binÃ¤rt uttryck. *)
    EXPRESSION =
        CONSTANT
      | VARIABLE
      | BINARYEXPR ;

    (* Ett binÃ¤rt uttryck bestÃ¥r av tvÃ¥ uttryck med en matematisk operator i mitten. *)
    BINARYEXPR = '[', EXPRESSION, COMMA, BINARYOPER, COMMA, EXPRESSION, ']' ;

    (* Ett villkor bestÃ¥r av tvÃ¥ uttryck med en villkorsoperator i mitten. *)
    CONDITION = '[', EXPRESSION, COMMA, CONDOPER, COMMA, EXPRESSION, ']' ;

    (* En binÃ¤roperator symboliserar ett av de fyra grundlÃ¤ggande rÃ¤knesÃ¤tten.
       Eftersom man i sprÃ¥ket mÃ¥ste skriva detta med citattecken som i
           [10, "+", 20]
       mÃ¥ste vi hÃ¤r ha med *dubbla* citattecken.  Om vi bara skrev '+'
       skulle uttrycket vara
           [10, +, 20]
       vilket inte kan tolkas i Python.
    *)
    BINARYOPER = "'+'" | "'-'" | "'*'" | "'/'" ;

    (* En villkorsoperator Ã¤r stÃ¶rre Ã¤n, mindre Ã¤n eller lika med. *)
    CONDOPER = "'<'" | "'>'" | "'='" ;

    (* En variabel Ã¤r en strÃ¤ng definierad som i Python -- strÃ¤ngen anger
       namnet pÃ¥ variabeln.  Text mellan tvÃ¥ frÃ¥getecken anger att nÃ¥got
       Ã¤r definierat utanfÃ¶r EBNF -- vi gÃ¥r alltsÃ¥ inte sÃ¥ lÃ¥ngt som att
       vi definierar exakt hur en strÃ¤ng ser ut. *)
    VARIABLE = ? a Python string ? ;

    (* En konstant Ã¤r ett tal i Python. *)
    CONSTANT = ? a Python number ? ;
"""
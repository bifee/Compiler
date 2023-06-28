import lexica as lex
from lexica import TK
tokens = lex.tokens
current_token = None
next_token = None
index = 0

class Node:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children if children else []

    def __str__(self):
        return str(self.label)

def parse_S():
    node = Node('<S>')
    if current_token['lexeme'] == 'def':
        node.children.append(parse_func())
        if current_token['lexeme'] == 'def':
            node.children.append(parse_S())
    elif current_token['lexeme'] in ['int', 'float', 'char', 'bool', 'string']:
        node.children.append(parse_define_var())
        node.children.append(parse_S())
    else:
        raise SyntaxError(f"Expected '<S>', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_expressao():
    node = Node('<expressao>')
    if current_token['type'] == TK.ID:
        node.children.append(parse_operacao())
        if current_token['lexeme'] not in ['}', 'return']:
            node.children.append(parse_expressao())
    elif current_token['lexeme'] in ['int', 'float', 'char', 'bool', 'string']:
        node.children.append(parse_define_var())
        if current_token['lexeme'] not in ['}']:
            node.children.append(parse_expressao())
    elif current_token['lexeme'] in ['senhor, caso', 'senao, receio que', 'senhor, voce tem das', 'durante tal ordem,']:
        node.children.append(parse_estrut_control())
        if current_token['lexeme'] not in ['}']:
            node.children.append(parse_expressao())
    elif current_token['lexeme'] == 'return':
        node.children.append(parse_return_struct())
    else:
        raise SyntaxError(f"Expected 'expressao', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_estrut_control():
    node = Node('<estrut_control>')
    if current_token['lexeme'] == 'senhor, caso':
        node.children.append(parse_if_struct())
    elif current_token['lexeme'] == 'senao, receio que':
        node.children.append(parse_else_struct())
    elif current_token['lexeme'] == 'senhor, voce tem das':
        node.children.append(parse_for_struct())
    elif current_token['lexeme'] == 'durante tal ordem,':
        node.children.append(parse_while_struct())
    else:
        raise SyntaxError(f"Expected 'estrutura de controle', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_operacao():
    node = Node('<operacao>')
    if next_token['type'] == TK.OPERADOR:
        node.children.append(parse_operacao_atr())
    elif next_token['type'] == TK.COMPARADOR:
        node.children.append(parse_operacao_comp())
    else:
        raise SyntaxError(f"Expected 'operacao', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_operacao_atr():
    node = Node('<operacao_atr>')
    node.children.append(parse_var_name())
    node.children.append(match('='))
    if current_token['type'] == TK.ID:
        node.children.append(parse_var_name())
        if current_token['type'] != TK.OPERADOR:
            return node
        else:
            node.children.append(parse_operador())
            if current_token['type'] == TK.ID:
                node.children.append(parse_var_name())
            elif current_token['type'] == TK.INT:
                node.children.append(parse_int())
            else:
                raise SyntaxError(f"Expected 'numero ou variavel', but found {current_token['lexeme']}, line {current_token['line_number']}")
    elif current_token['type'] in [TK.CHAR, TK.INT, TK.STRING, TK.BOOL, TK.FLOAT] and next_token['type'] != TK.OPERADOR:
        print(current_token)
        node.children.append(parse_atr())
    elif current_token['type'] == TK.INT:
        node.children.append(parse_int())
        node.children.append(parse_operador())
        if current_token['type'] == TK.ID:
            node.children.append(parse_var_name())
        elif current_token['type'] == TK.INT:
            node.children.append(parse_int())
        else:
            raise SyntaxError(f"Expected 'numero ou variavel', but found {current_token['lexeme']}, line {current_token['line_number']}")
    else:
        raise SyntaxError(f"Expected 'atribuiçao', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_operacao_comp():
    node = Node('<operacao_comp>')
    node.children.append(parse_var_name())
    node.children.append(parse_comparacao())
    if current_token['type'] == TK.ID:
        node.children.append(parse_var_name())
    elif current_token['type'] in [TK.CHAR, TK.INT, TK.STRING, TK.BOOL, TK.FLOAT]:
        node.children.append(parse_atr())
    else:
        raise SyntaxError(f"Expected 'comparacao', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_define_var():
    node = Node('<define_var>')
    node.children.append(parse_type())
    node.children.append(parse_var_name())
    node.children.append(match('='))
    if current_token['type'] == TK.ID:
        node.children.append(parse_var_name())
    elif current_token['type'] in [TK.CHAR, TK.INT, TK.STRING, TK.BOOL, TK.FLOAT]:
        node.children.append(parse_atr())
    else:
        raise SyntaxError(f"Expected 'numero ou variavel', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_escopo():
    node = Node('<escopo>')
    if current_token['type'] == TK.PARENTESES_cls:
        vazio = Node('')
        node.children.append(vazio)
        return node
    elif current_token['lexeme'] in ['int', 'float', 'char', 'bool', 'string']:
        while current_token['type'] != TK.PARENTESES_cls:
            node.children.append(parse_type())
            node.children.append(parse_var_name())
            if current_token['type'] != TK.PARENTESES_cls:
                node.children.append(match(','))
    else:
        raise SyntaxError(f"Expected 'type', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_return_struct():
    node = Node('<return_struct>')
    node.children.append(parse_return())
    if current_token['type'] == TK.ID:
        node.children.append(parse_var_name())
    elif current_token['type'] in [TK.CHAR, TK.INT, TK.STRING, TK.BOOL, TK.FLOAT]:
        node.children.append(parse_atr())
    else:
        raise SyntaxError(f"Expected 'numero ou variavel', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_if_struct():
    node = Node('<if_struct>')
    node.children.append(parse_IF())
    node.children.append(parse_operacao_comp())
    node.children.append(match('{'))
    node.children.append(parse_expressao())
    node.children.append(match('}'))
    return node

def parse_else_struct():
    node = Node('<else_struct>')
    node.children.append(parse_ELSE())
    node.children.append(match('{'))
    node.children.append(parse_expressao())
    node.children.append(match('}'))
    return node

def parse_for_struct():
    node = Node('<for_struct>')
    node.children.append(parse_FOR())
    node.children.append(parse_var_name())
    node.children.append(parse_ate())
    if current_token['type'] == TK.ID:
        node.children.append(parse_var_name())
    elif current_token['type'] == TK.INT:
        node.children.append(parse_int())
    else:
        raise SyntaxError(f"Expected 'numero ou variavel', but found {current_token['lexeme']}, line {current_token['line_number']}")
    node.children.append(match('{'))
    node.children.append(parse_expressao())
    node.children.append(match('}'))
    return node

def parse_while_struct():
    node = Node('<while_struct>')
    node.children.append(parse_WHILE())
    node.children.append(parse_operacao_comp())
    node.children.append(match('{'))
    node.children.append(parse_expressao())
    node.children.append(match('}'))
    return node

def parse_func():
    node = Node('<func>')
    node.children.append(parse_def())
    node.children.append(parse_var_name())
    node.children.append(match('('))
    node.children.append(parse_escopo())
    node.children.append(match(')'))
    node.children.append(match('{'))
    node.children.append(parse_expressao())
    node.children.append(match('}'))
    return node

def parse_var_name():
    node = Node('<var_name>')
    if current_token['type'] == TK.ID:
        node.children.append(match(current_token['type']))
    else:
        raise SyntaxError(f"Expected 'variavel', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_def():
    if current_token['lexeme'] == 'def':
        node = match(current_token['lexeme'])
    else:
        raise SyntaxError(f"Expected 'def', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_type():
    node = Node('<type>')
    if current_token['lexeme'] in ['int', 'float', 'char', 'bool', 'string']:
        node.children.append(match(current_token['lexeme']))
    else:
        raise SyntaxError(f"Expected 'type', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_IF():
    if current_token['lexeme'] == 'senhor, caso':
        node = match(current_token['lexeme'])
    else:
        raise SyntaxError(f"Expected 'IF', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_ELSE():
    if current_token['lexeme'] == 'senao, receio que':
        node = match(current_token['lexeme'])
    else:
        raise SyntaxError(f"Expected 'ELSE', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_FOR():
    if current_token['lexeme'] == 'senhor, voce tem das':
        node = match(current_token['lexeme'])
    else:
        raise SyntaxError(f"Expected 'FOR', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_WHILE():
    if current_token['lexeme'] == 'durante tal ordem,':
        node = match(current_token['lexeme'])
    else:
        raise SyntaxError(f"Expected 'WHILE', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_return():
    if current_token['lexeme'] == 'return':
        node = match(current_token['lexeme'])
    else:
        raise SyntaxError(f"Expected 'return', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_ate():
    if current_token['lexeme'] == 'ate':
        node = match(current_token['lexeme'])
    else:
        raise SyntaxError(f"Expected 'ate', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_char():
    node = Node('<letra>')
    if current_token['type'] == TK.CHAR:
        node.children.append(match(current_token['type']))
    else:
        raise SyntaxError(f"Expected 'char', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_int():
    node = Node('<digito>')
    if current_token['type'] == TK.INT:
        node.children.append(match(current_token['type']))
    else:
        raise SyntaxError(f"Expected 'int', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_float():
    node = Node('<float>')
    if current_token['type'] == TK.FLOAT:
        node.children.append(match(current_token['type']))
    else:
        raise SyntaxError(f"Expected 'float', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_string():
    node = Node('<string>')
    if current_token['type'] == TK.STRING:
        node.children.append(match(current_token['type']))
    else:
        raise SyntaxError(f"Expected 'string', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_bool():
    node = Node('<bool>')
    if current_token['type'] == TK.KEYWORD:
        node.children.append(match(current_token['type']))
    else:
        raise SyntaxError(f"Expected 'bool', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_atr():
    node = Node('<atr>')
    if current_token['type'] in [TK.CHAR, TK.INT, TK.STRING, TK.BOOL, TK.FLOAT]:
        node.children.append(match(current_token['type']))
    else:
        raise SyntaxError(f"Expected 'atr_var', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_comparacao():
    node = Node('<comparador>')
    if current_token['type'] == TK.COMPARADOR:
        node.children.append(match(current_token['type']))
    else:
        raise SyntaxError(f"Expected 'comparador', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

def parse_operador():
    node = Node('<operador>')
    if current_token['type'] == TK.OPERADOR:
        node.children.append(match(current_token['type']))
    else:
        raise SyntaxError(f"Expected 'operador', but found {current_token['lexeme']}, line {current_token['line_number']}")
    return node

# funcoes auxiliares
def match(expected_type):
    global current_token
    global next_token
    global index
    if current_token['type'] == expected_type:
        node = Node(current_token['lexeme'])
        index += 1
        if index < len(tokens):
            current_token = tokens[index]
            if index + 1 != len(tokens):
                next_token = tokens[index + 1]
    elif current_token['lexeme'] == expected_type:
        node = Node(current_token['lexeme'])
        index += 1
        if index < len(tokens):
            current_token = tokens[index]
            if index +1 != len(tokens):
                next_token = tokens[index + 1]
    else:
        raise SyntaxError(f"line {current_token['line_number']}, Expected '{expected_type}', but found '{current_token['lexeme']}'")
    return node

current_token = tokens[index]
next_token = tokens[index+1]
parse_tree = parse_S()


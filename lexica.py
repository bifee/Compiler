import re
from enum import Enum
tokens = []
symbol_table =[]

class TK(Enum):
    KEYWORD = 1
    ID = 2
    INT = 3
    FLOAT = 4
    CHAR = 5
    STRING = 6
    CHAVES_op = 7
    CHAVES_cls = 8
    PARENTESES_op = 9
    PARENTESES_cls = 10
    OPERADOR = 11
    COMPARADOR = 12
    COMMENT = 13
    VIRGULA = 14
    BOOL = 15

token_patterns = {
    TK.KEYWORD: r'(int|float|string|char|bool|senhor, caso|senao, receio que|durante tal ordem,|senhor, voce tem das|ate|return|def)\n?',
    TK.BOOL: r'(True|False)\n?',
    TK.ID: r'[a-zA-Z][a-zA-Z0-9]*\n?',
    TK.FLOAT: r'[+-]?[0-9]+\.[0-9]+',
    TK.INT: r'\b\d+\b\n?',
    TK.CHAR: r'\'(.*?)\'\n?',
    TK.STRING: r'\"(.*?)\"\n?',
    TK.CHAVES_op: r'\{\n?',
    TK.CHAVES_cls: r'\}\n?',
    TK.PARENTESES_op: r'\(\n?',
    TK.PARENTESES_cls: r'\)\n?',
    TK.OPERADOR: r'[-+*/%=]\n?',
    TK.COMPARADOR: r'==|!=|<=|>=|<|>\n?',
    TK.COMMENT: r'#.*\n?',
    TK.VIRGULA: r'\,'
}
def search(symbol_table, token, scope_stack, token_ant):
    for symbol in symbol_table:
        if token['lexeme'] == symbol['name'] and symbol['type'] == TK.ID:
            if token_ant['lexeme'] in ['int', 'char', 'float', 'string', 'bool']:
                if symbol['scope'] != scope_stack[-1]:
                    return False
                return False
            return True
    return False

def create_symbol(symbol_table, entrada, name, type, data_type, value, scope, line_number):
        symbol = {
            'entrada': entrada,
            'name': name,
            'type': type,
            'data_type': data_type,
            'value': value,
            'scope': scope,
            'line': line_number
        }
        symbol_table.append(symbol)

def build_symbol_table(tokens):
    symbol_table = []
    current_scope = "global"
    scope_stack = ["global"]
    aux = 0
    contador = 0
    func_name = ''
    for token in tokens:
        if token['lexeme'] == 'def':
            func_name = tokens[aux+1]['lexeme']
        elif token['type'] == TK.KEYWORD:
            if token['lexeme'] in ["int"]:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], 'int', None, current_scope, token['line_number'])
            elif token['lexeme'] in ["char"]:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], 'char', None, current_scope, token['line_number'])
            elif token['lexeme'] in ["float"]:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], 'float', None, current_scope, token['line_number'])
            elif token['lexeme'] in ["string"]:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], 'string', None, current_scope, token['line_number'])
            elif token['lexeme'] in ["bool"]:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], 'bool', None, current_scope, token['line_number'])
            else:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], None, None, current_scope, token['line_number'])

        elif search(symbol_table, token, scope_stack, tokens[aux-1]) == False:
            if token['type'] == TK.ID:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], None, None, current_scope, token['line_number'])
            elif token['type'] == TK.CHAR:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], 'char', token['lexeme'], current_scope, token['line_number'])
            elif token['type'] == TK.BOOL:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], 'bool', token['lexeme'], current_scope, token['line_number'])
            elif token['type'] == TK.INT:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], 'int', token['lexeme'], current_scope, token['line_number'])
            elif token['type'] == TK.FLOAT:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], 'float', token['lexeme'], current_scope, token['line_number'])
            elif token['type'] == TK.STRING:
                contador += 1
                create_symbol(symbol_table, contador, token['lexeme'], token['type'], 'string', token['lexeme'], current_scope, token['line_number'])
            elif token['type'] == TK.CHAVES_op:
                current_scope = func_name
                scope_stack.append(current_scope)
            elif token['type'] == TK.CHAVES_cls:
                contador += 1
                scope_stack.pop()
                current_scope = scope_stack[-1]
            elif token['type'] == TK.PARENTESES_op:
                current_scope = func_name
                scope_stack.append(current_scope)
            elif token['type'] == TK.PARENTESES_cls:
                scope_stack.pop()
                current_scope = scope_stack[-1]
        aux += 1
    return symbol_table

def tokenize(source_code):
    tokens = []
    line_number = 1
    while source_code:
        match = None

        for token_type, pattern in token_patterns.items():
            regex = re.compile(pattern)
            match = regex.match(source_code)

            if match:
                lexeme = match.group(0)
                if token_type == TK.COMMENT:
                    source_code = source_code[len(lexeme):].lstrip()
                    break
                if "\n" in lexeme:
                    lexeme = lexeme.translate(str.maketrans('', '', "\n"))
                    line_number += 1
                token = {
                    'type': token_type,
                    'lexeme': lexeme,
                    'line_number': line_number
                }
                tokens.append(token)
                source_code = source_code[len(lexeme):].lstrip()
                break

        if not match:
            wr_token = source_code[:1]
            raise ValueError(f"Invalid token '{wr_token}' at line {line_number}")

    return tokens

def tokenize_file(file):
    global tokens
    global symbol_table
    with open(file, 'r') as file:
        source_code = file.read()
        tokens = tokenize(source_code)
        symbol_table = build_symbol_table(tokens)

file = 'source_code.txt'
tokenize_file(file)

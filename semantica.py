from sintatica import *
from lexica import *

scope_track = ['global']
root = parse_tree
symbol_table1 = symbol_table
father = Node('')

class SemanticError(Exception):
    pass

def update_table_atr(value, data_type):
    global symbol_table1

    for symbol1 in symbol_table1:
        if symbol1['name'] == data_type.label:
            aux = symbol1['data_type']

    for symbol in symbol_table1:
        if symbol['name'] == value.label and symbol['scope'] == scope_track[-1]:
            symbol['data_type'] = aux
            symbol['value'] = data_type.label

def update_table(node):
    global symbol_table1
    global father
    for symbol in symbol_table1:
        if symbol['name'] == node.label:
            symbol['data_type'] = father.label
            symbol['value'] = '0'

def verify_type(type, atr):
    aux1 = None
    aux2 = None
    for symbol in symbol_table1:
        if symbol['name'] == type.children[0].label and symbol['scope'] in [scope_track[-1], 'global']:
            aux1 = symbol
    for symbol in symbol_table:
        if symbol['name'] == atr.children[0].label and symbol['scope'] in [scope_track[-1], 'global']:
            aux2 = symbol
    if aux1['data_type'] == aux2['data_type']:
        return
    raise SemanticError(f"Tipos de dado incompativeis: {aux1['data_type']}, {aux2['data_type']}, line: {aux1['line']}")


def verify_duplicity(node):
    global symbol_table1
    for symbol in symbol_table1:
        if symbol['name'] == node.children[0].label and symbol['value'] != None:
            if symbol['scope'] != scope_track[-1]:
                return
            raise SemanticError(f"Semantic Error: variavel {node.children[0].label} ja declarada, line: {symbol['line']}")
    return

def verify_var_existence(node):
    global father
    global symbol_table1
    for symbol in symbol_table1:
        if symbol['name'] == node.children[0].label and symbol['value'] != None and (symbol['scope'] == scope_track[-1] or symbol['scope'] == 'global'):
            return
        elif symbol['name'] == node.children[0].label and father.label in ['def', 'int', 'string', 'char', 'bool', 'float'] and (symbol['scope'] == scope_track[-1] or symbol['scope'] == 'global'):
            if father.label == 'def':
                if scope_track[-1] != 'global':
                    scope_track.pop()
                scope_track.append(node.children[0].label)
            update_table(node.children[0])
            return
    raise SemanticError(f"Semantic Error: variavel {node.children[0].label} nao declarada, line: {symbol['line']}")

def verify_define_var(node):
    global symbol_table1
    verify_duplicity(node.children[1])
    var = node.children[1]
    atr = node.children[3]
    verify_type(node.children[0], node.children[3])
    update_table_atr(var.children[0], atr.children[0])

def verify_comp_op(node):
    verify_var_existence(node.children[0])
    verify_var_existence(node.children[2])
    verify_type(node.children[0], node.children[2])

def verify_atr_op(node):
    verify_var_existence(node.children[0])
    verify_var_existence(node.children[2])
    if node.children[-2].label != '<operador>':
        if verify_type(node.children[0], node.children[2]):
            return
    else:
        if verify_type(node.children[2], node.children[-1]):
            if verify_type(node.children[0], node.children[2]):
                return

def pre_order_traversal(node):
    global scope_track
    global father
    if node is None:
        return
    if node.label == '<define_var>':
        verify_define_var(node)
    elif node.label == '<var_name>':
        verify_var_existence(node)
    elif node.label == '<operacao_comp>':
        verify_comp_op(node)
    elif node.label == '<operacao_atr>':
        verify_atr_op(node)
    father = node
    for child in node.children:
        pre_order_traversal(child)

pre_order_traversal(root)
scope_track.pop()







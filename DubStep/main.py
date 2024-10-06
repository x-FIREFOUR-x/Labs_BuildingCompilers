    
    # Таблиця лексем мови
tokenTable = {
    'true': 'boolval',
    'false': 'boolval',
    'int': 'keyword',
    'real': 'keyword',
    'bool': 'keyword',
    'program': 'keyword',
    'var': 'keyword',
    'begin': 'keyword',
    'end': 'keyword',
    'end.': 'keyword',
    'read': 'keyword',
    'write':'keyword',       
    'for': 'keyword',
    'to': 'keyword',
    'do': 'keyword',
    'if': 'keyword',
    'then': 'keyword',
    'else': 'keyword',  
    ':=': 'assign_op',
    '+': 'add_op',
    '-': 'add_op',       
    '*': 'mult_op',
    '/': 'mult_op',
    '^': 'step_op',
    '<': 'rel_op',
    '>': 'rel_op',
    '<=': 'rel_op',
    '>=': 'rel_op',
    '=': 'rel_op',      
    '<>': 'rel_op',
    'and': 'log_op',
    'or': 'log_op',
    'not': 'log_op',
    '(': 'brackets_op ',
    ')': 'brackets_op ',
    '.': 'punct',
    ',': 'punct',
    ';': 'punct',
    ':': 'punct',
    ' ': 'ws',
    '\t': 'ws',
    '\n': 'eol',
    '\r\n': 'eol',
}

    # Решту токенів визначаємо не за лексемою, а за заключним станом
tokStateTable = {
    3: 'id',
    5: 'intnum',
    7: 'realnum',
}

# Діаграма станів
#               Q                                                            q0          F
# M = ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17}, Σ,  δ, 0, {2, 3, 5, 7, 9, 11, 12, 15, 16, 17})

# δ - state-transition_function
stateTransitionFunction = {
    (0, 'ws'): 0, (0, 'eol'): 0,

    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, '.'): 2, (1, 'Other'): 3,

    (0, 'Digit'): 4, (4, 'Digit'): 4, (4, 'Other'): 5, (4, '.'): 6, (6, 'Digit'): 6, (6, 'Other'): 7, 
    (0, '.'): 8, (8, 'Digit'): 6, (8, 'Other'): 9,

    (0, ':'): 10, (10, '='): 11, (10, 'Other'): 17,

    (0, '+'): 12, (0, '-'): 12, (0, '*'): 12, (0, '/'): 12, (0, '^'): 12, 
    (0, '('): 12, (0, ')'): 12, 
    (0, ','): 12, (0, ';'): 12, 
    (0, '='): 12,

    (0, '>'): 13, (13, '='): 12, (13, 'Other'): 15,
    (0, '<'): 14, (14, '='): 12, (14, '>'): 12, (14, 'Other'): 15,
    
    (0, 'Other'): 16,
}

initState = 0  # q0 - стартовий стан
F = {2, 3, 5, 7, 9, 11, 12, 15, 16, 17}
Fstar = {2, 3, 5, 7, 15}  # зірочка
Ferror = {9, 16, 17}  # обробка помилок

tableOfId = {}  # Таблиця ідентифікаторів
tableOfConst = {}  # Таблиць констант
tableOfSymb = {}  # Таблиця символів програми (таблиця розбору)

state = initState  # поточний стан

f = open('test.ds', 'r')
sourceCode = f.read()
f.close()

# FSuccess - ознака успішності розбору
FSuccess = (True, 'Lexer')

lenCode = len(sourceCode) - 1  # номер останнього символа у файлі з кодом програми
numLine = 1  # лексичний аналіз починаємо з першого рядка
numChar = -1  # з першого символа (в Python'і нумерація - з 0)
char = ''  # ще не брали жодного символа
lexeme = ''  # ще не починали розпізнавати лексеми


def is_final(state):
    if (state in F):
        return True
    else:
        return False

def nextChar():
    global numChar
    numChar += 1
    return sourceCode[numChar]

def nextState(state, classChar):
    try:
        return stateTransitionFunction[(state, classChar)]
    except KeyError:
        return stateTransitionFunction[(state, 'Other')]
    
def classOfChar(char):
    if char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
        res = "Letter"
    elif char in "0123456789":
        res = "Digit"
    elif char in " \t":
        res = "ws"
    elif char in "\r\n":
        res = "nl"
    elif char in "+-*/^=()<>,;.":
        res = char
    else:
        res = 'символ не належить алфавіту'
    return res

def getToken(state, lexeme):
    try:
        return tokenTable[lexeme]
    except KeyError:
        return tokStateTable[state]
    
def indexIdConst(state, lexeme):
    indx = 0
    if state == 3:
        indx = tableOfId.get(lexeme)
        if indx is None:
            indx = len(tableOfId) + 1
            tableOfId[lexeme] = indx
    if state in (5, 7):
        indx = tableOfConst.get(lexeme)
        if indx is None:
            indx = len(tableOfConst) + 1
            tableOfConst[lexeme] = (tokStateTable[state], indx)
        else:
            indx = indx[1]
    return indx
    
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
    '(': 'brackets_op',
    ')': 'brackets_op',
    '.': 'punct',
    ',': 'punct',
    ';': 'punct',
    ':': 'punct',
    ' ': 'ws',
    '': 'eol',
    '\t': 'ws',
    '\n': 'eol',
    '\r\n': 'eol',
}

    # Решту токенів визначаємо не за лексемою, а за заключним станом
tokStateTable = {
    3: 'id',
    5: 'int',
    7: 'real',
}

# Діаграма станів
#               Q                                                            q0          F
# M = ({0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17}, Σ,  δ, 0, {2, 3, 5, 7, 9, 11, 12, 15, 16, 17})

# δ - state-transition_function
stateTransitionFunction = {
    (0, 'ws'): 0, (0, 'eol'): 18,

    (0, 'Letter'): 1, (1, 'Letter'): 1, (1, 'Digit'): 1, (1, '.'): 2, (1, 'Other'): 3,

    (0, 'Digit'): 4, (4, 'Digit'): 4, (4, 'Other'): 5, (4, '.'): 6, (6, 'Digit'): 6, (6, 'Other'): 7, 
    (0, '.'): 8, (8, 'Digit'): 6, (8, 'Other'): 9,

    (0, ':'): 10, (10, '='): 11, (10, 'Other'): 15,

    (0, '+'): 12, (0, '-'): 12, (0, '*'): 12, (0, '/'): 12, (0, '^'): 12, 
    (0, '('): 12, (0, ')'): 12, 
    (0, ','): 12, (0, ';'): 12, 
    (0, '='): 12,

    (0, '>'): 13, (13, '='): 12, (13, 'Other'): 15,
    (0, '<'): 14, (14, '='): 12, (14, '>'): 12, (14, 'Other'): 15,
    
    (0, 'Other'): 16,
}

initState = 0  # q0 - стартовий стан
F = {2, 3, 5, 7, 9, 11, 12, 15, 16, 18}
Fstar = {3, 5, 7, 15}  # зірочка
Ferror = {9, 16}  # обробка помилок

tableOfId = {}  # Таблиця ідентифікаторів
tableOfConst = {}  # Таблиць констант
tableOfSymb = {}  # Таблиця символів програми (таблиця розбору)

state = initState  # поточний стан

f = open('test.ds', 'r')
sourceCode = f.read()
f.close()

# FSuccess - ознака успішності розбору
FSuccess = ('Lexer', False)

lenCode = len(sourceCode) - 1  # номер останнього символа у файлі з кодом програми
numLine = 1  # лексичний аналіз починаємо з першого рядка
numChar = -1  # з першого символа (в Python'і нумерація - з 0)
char = ''  # ще не брали жодного символа
lexeme = ''  # ще не починали розпізнавати лексеми



def lex():
    global state, numLine, char, lexeme, numChar, FSuccess
    try:
        while numChar < lenCode:
            char = nextChar()  # прочитати наступний символ
            classCh = classOfChar(char)  # до якого класу належить
            state = nextState(state, classCh)  # обчислити наступний стан
            if (is_final(state)):  # якщо стан заключний
                processing()  # виконати семантичні процедури
            elif state == initState:
                lexeme = ''  # якщо стан НЕ заключний, а стартовий - нова лексема
            else:
                lexeme += char  # якщо стан НЕ закл. і не стартовий - додати символ до лексеми
        FSuccess = ('Lexer', True)
        print('Lexer: Лексичний аналіз завершено успішно')
        return FSuccess
    except SystemExit as e:
        # Встановити ознаку неуспішності
        FSuccess = ('Lexer', False)
        # Повідомити про факт виявлення помилки
        print('Lexer: Аварійне завершення програми з кодом {0}'.format(e))
        return FSuccess

def processing():
    global state, lexeme, char, numLine, numChar, tableOfSymb
    if state == 18:  # eol 
        numLine += 1
        lexeme = ''
        state = initState
    if state in (3, 5, 7):  # id, keyword; int; float
        token = getToken(state, lexeme)
        if token != 'keyword':
            index = indexIdConst(state, lexeme)
            print('{0:<3d} {1:<10s} {2:<10s} {3:<2d} '.format(numLine, lexeme, token, index))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, index)
        else:
            print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        numChar = putCharBack(numChar)  # зірочка
        state = initState
    if state in (11, 12): # 11: asign_op (':=') ; 12: add_op ('+', '-'), rel_op ('=', '>=', '<=', '<>'), mult_op('*', '/'), step_op ('^'), brackets_op ('(', ')'), punct (',', ';')
        lexeme += char
        token = getToken(state, lexeme)
        print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
    if state == 15:     # rel_op ('>', '<'), punct (':')
        if len(lexeme) > 1:
            lexeme = lexeme[:-1]
        numChar = putCharBack(numChar)  # зірочка
        token = getToken(state, lexeme)
        print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
        tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
        lexeme = ''
        state = initState
    if state == 2:  # keyword ('.end')
        try:
            lexeme = lexeme + char
            token = getToken(state, lexeme)
            print('{0:<3d} {1:<10s} {2:<10s} '.format(numLine, lexeme, token))
            tableOfSymb[len(tableOfSymb) + 1] = (numLine, lexeme, token, '')
            lexeme = ''
            state = initState
        except KeyError:
            state = 9
    if state in Ferror:  # (9, 16):  # ERROR
        fail()


def fail():
    global state, numLine, char, lexeme
    print(numLine)
    if state == 9:
        print('Lexer: у рядку ', numLine, ' зайвий символ "." в "' + lexeme+char + '"')
        exit(9)
    if state == 16:
        print('Lexer: у рядку ', numLine, ' неочікуваний символ ' + char)
        exit(16)


def is_final(state):
    if (state in F):
        return True
    else:
        return False

def nextChar():
    global numChar
    numChar += 1
    return sourceCode[numChar]

def putCharBack(numChar):
    return numChar - 1

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
        res = "eol"
    elif char in "+-*/^=()<>,;.:":
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



# запуск лексичного аналізатора	
#lex()

# Таблиці: розбору, ідентифікаторів та констант
#print('-'*265)
#print('tableOfSymb:{0}'.format(tableOfSymb))
#print('tableOfId:{0}'.format(tableOfId))
#print('tableOfConst:{0}'.format(tableOfConst))
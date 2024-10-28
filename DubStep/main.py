from lexer import lex
from lexer import tableOfSymb, tableOfConst

path_file = 'test.ds'
FSucces = lex(path_file)

print('-'*265)
print('tableOfSymb:{0}'.format(tableOfSymb))
print('-'*265)


# номер рядка таблиці розбору/лексем/символів ПРОГРАМИ tableOfSymb
numSymb = 1
curNumLine = 1
identId = 1
# довжина таблиці символів програми
# він же - номер останнього запису
len_tableOfSymb = len(tableOfSymb)
print(('len_tableOfSymb', len_tableOfSymb))

tableOfVar={}



# Функція для розбору за правилом
# Program = program Id var DeclarList begin StatementList end.
# читає таблицю розбору tableOfSymb
def parseProgram():
    try:
        # перевірити наявність ключового слова 'program' та прочитати ім'я програми
        parseToken('program', 'keyword', '')
        parseIdDeclarationsList()

        # перевірити наявність ключового слова 'var'
        parseToken('var', 'keyword', '')
        # перевірити визначення змінних
        parseIdDeclarationsList()

        # перевірити наявність ключового слова 'begin'
        parseToken('begin', 'keyword', '')
        # перевірити синтаксичну коректність списку інструкцій StatementList
        parseStatementList()
        # перевірити наявність ключового слова 'end.'
        parseToken('end.', 'keyword', '')

        # повідомити про синтаксичну коректність програми
        print('Parser: Синтаксичний та семантичний аналіз завершився успішно')
        return True
    except SystemExit as e:
        # Повідомити про факт виявлення помилки
        print('Parser: Аварійне завершення програми з кодом {0}'.format(e))



# Функція перевіряє, чи у поточному рядку таблиці розбору
# зустрілась вказана лексема lexeme з токеном token
def parseToken(lexeme, token, indent):
    # доступ до поточного рядка таблиці розбору
    global numSymb

    # якщо всі записи таблиці розбору прочитані,
    # а парсер ще не знайшов якусь лексему
    if numSymb > len_tableOfSymb:
        failParse('неочікуваний кінець програми', (lexeme, token, numSymb))

    # прочитати з таблиці розбору
    # номер рядка програми, лексему та її токен
    numLine, lex, tok = getSymb()

    # тепер поточним буде наступний рядок таблиці розбору
    numSymb += 1

    # чи збігаються лексема та токен таблиці розбору з заданими
    if (lex, tok) == (lexeme, token):
        # вивести у консоль номер рядка програми та лексему і токен
        print(indent + 'parseToken(): В рядку {0} токен {1}'.format(numLine, (lexeme, token)))
        return True
    else:
        # згенерувати помилку та інформацію про те, що
        # лексема та токен таблиці розбору (lex,tok) відрізняються від
        # очікуваних (lexeme,token)
        failParse('невідповідність токенів', (numLine, lex, tok, lexeme, token))
        return False
    
# Прочитати з таблиці розбору поточний запис
# Повертає номер рядка програми, лексему та її токен
def getSymb():
    if numSymb > len_tableOfSymb:
        failParse('getSymb(): неочікуваний кінець програми', numSymb)
    # таблиця розбору реалізована у формі словника (dictionary)
    # tableOfSymb[numSymb]={numSymb: (numLine, lexeme, token, indexOfVarOrConst)
    numLine, lexeme, token, _ = tableOfSymb[numSymb]
    return numLine, lexeme, token



# Функція для розбору за правилом для StatementList
# DeclarList = Declaration {';' Declaration }
def parseIdDeclarationsList():
    global numSymb
    print('\t' * 4 + 'parseIdDeclarationsList():')

    # взяти поточну лексему
    numLine, lexeme, token = getSymb()

    # взяти поопередню лексему
    numSymb -= 1
    _, prev_lexeme, prev_token = getSymb()

    # встановити номер нової поточної лексеми
    numSymb += 2

    # ім'я програми
    print('\t' * 5 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
    if (prev_lexeme, prev_token) == ("program", "keyword") and token == "id":
        return True

    if token in ("id"):
        addIdVar(numLine, lexeme, "undefined", None)
    else:
        failParse('parseIdDeclarationsList(): не очікуванний символ', (numLine, lexeme))

    next_numLine, next_lexeme, next_token = getSymb()
    numSymb += 1
    print('\t' * 5 + 'в рядку {0} - {1}'.format(next_numLine, (next_lexeme, next_token)))

        #перевірити перерахунок змінних
    if (next_lexeme, next_token) == (",","punct"):
        parseIdDeclarationsList()
        return True
    
        #перевірити визначення типу
    elif (next_lexeme, next_token) == (":", "punct"):
        next_numLine, next_lexeme, next_token = getSymb()
        numSymb += 1
        print('\t' * 5 + 'в рядку {0} - {1}'.format(next_numLine, (next_lexeme, next_token)))
            #перевірити тип змінної
        if next_token == "keyword" and next_lexeme in ("int", "real", "bool"):
            addTypeForIdVar(next_lexeme)

                #перевірити кінець визначення змінної
            parseToken(";","punct","\t"*6)

                #перевірити кінець визначення змінних
            next_numLine, next_lexeme, next_token = getSymb()
            if (next_lexeme, next_token) == ("begin","keyword"):
                return True
                #перевірити ініціалізацію наступної змінної
            else:
                parseIdDeclarationsList()
            return True
        else:
            failParse('parseIdDeclarationsList(): невідомий тип', (numLine, next_lexeme, next_token))
    else:
        return False

# Додати в таблицю змінних нову змінну
def addIdVar(numLine, lexeme, lexeme_type, val):
    index = tableOfVar.get(lexeme)
    if index is None:
        index = len(tableOfVar) + 1
        tableOfVar[lexeme] = (index, lexeme_type, val)
    else: failParse("повторне оголошення змінної", (numLine, lexeme, lexeme_type, val))

# Додати дані про тип для змінної в таблицю змінних
def addTypeForIdVar(type_name):
    flag = True
    for id in tableOfVar:
        if tableOfVar[id][1] == "undefined":
            tableOfVar[id] = (tableOfVar[id][0],type_name,tableOfVar[id][2])



# Функція для розбору за правилом для StatementList
# StatementList = (Statement ';') { Statement ';'}
# викликає функцію parseStatement() доти,
# доки parseStatement() повертає True
def parseStatementList():
    print('\t parseStatementList():')
    while parseStatement():
        pass
    return True

# Функція для розбору за правилом для Statement
def parseStatement():
    print('\t\t parseStatement():')
    global numSymb

    # прочитаємо поточну лексему в таблиці розбору
    numLine, lexeme, token = getSymb()

    if token == 'id':
        parseAssign()
        return True

    elif (lexeme, token) == ('if', 'keyword'):
        parseIf()
        return True

    elif (lexeme, token) == ('for', 'keyword'):
        parseFor()
        return True

    elif (lexeme, token) == ('write', 'keyword'):
        parseWrite()
        return True

    elif (lexeme, token) == ('read', 'keyword'):
        parseRead()
        return True

    elif (lexeme, token) == ('end', 'keyword'):
        return False

    elif (lexeme, token) == ('end.', 'keyword'):
        return False

    else:
        # жодна з інструкцій не відповідає
        # поточній лексемі у таблиці розбору,
        failParse('невідповідність інструкцій', (numLine, lexeme, token, 'id або if або for або write або read або значення для присвоєння'))
        return False


def getTypeVar(id):
    try:
        return tableOfVar[id][1]
    except KeyError:
        return "error"
    
def initVar(id, val):
    tableOfVar[id] = (tableOfVar[id][0],tableOfVar[id][1], val)

def getTypeOp(left_type, op, right_type):
    t_res = "error"
    t_arith = left_type in ('real', 'int') and right_type in ('real', 'int')
    if t_arith and op in ("+","-","*","/","^"):
        t_res = left_type
    elif t_arith and op in ("<", ">","<=",">=","<>","="):
        t_res = "bool"
    return t_res

def getTypeConst(id):
    try:
        return tableOfConst[id][0]
    except KeyError:
        return 'error'
    
def getTypeVar(id):
    try:
        return tableOfVar[id][1]
    except KeyError:
        return 'error'

def isInitVar(id):
    if tableOfVar[id][2] is not None:
        return True
    else:
        return False

def parseExpression(isRes=True):
    global numSymb
    print('\t' * 5 + 'parseExpression():')
    res_pars = parseTerm(isRes=isRes)
    if not isRes and res_pars == "error":
        return "error"
    F = True
    # продовжувати розбирати Доданки (Term)
    # розділені лексемами '+' або '-'
    while F:
        numLine, lexeme, token = getSymb()
        if token in ('add_op'):
            numSymb += 1
            print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
            r_res_pars = parseTerm(isRes=isRes)
            if not isRes and r_res_pars == "error":
                return "error"
            res_type = getTypeOp(res_pars, lexeme, r_res_pars)
            if res_type != "error":
                res_pars = res_type
            else:
                if not isRes:
                    return "error"
                else:
                    failParse("присвоєння хибного типу", (numLine, lexeme, r_res_pars, res_pars))
        else:
            F = False
    return res_pars

def parseTerm(isRes=True):
    global numSymb
    print('\t' * 6 + 'parseTerm():')
    res_pars = parseFactor(isRes=isRes)
    if not isRes and res_pars == "error":
        return "error"
    F = True
    # продовжувати розбирати Множники (Factor)
    # розділені лексемами '*' або '/'
    while F:
        numLine, lexeme, token = getSymb()
        if token in ('mult_op, step_op'):
            numSymb += 1
            print('\t' * 6 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
            r_pars_res = parseFactor(isRes=isRes)
            if r_pars_res == "error" and not isRes:
                return "error"
            res_type = getTypeOp(res_pars, lexeme, r_pars_res)
            if res_type != "error":
                res_pars = res_type
            else:
                if not isRes:
                    return "error"
                else:
                    failParse("присвоєння хибного типу", (numLine, lexeme, r_pars_res, res_pars))
        else:
            F = False
    return res_pars

def parseFactor(isRes=True):
    global numSymb
    print('\t' * 7 + 'parseFactor():')
    numLine, lexeme, token = getSymb()
    print('\t' * 7 + 'parseFactor():=============рядок: {0}\t (lexeme, token):{1}'.format(numLine, (lexeme, token)))

    # перша і друга альтернативи для Factor
    # якщо лексема - це константа або ідентифікатор
    if token in ('int', 'real'):
        numSymb += 1
        print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
        return getTypeConst(lexeme)

    elif token == "id":
        if getTypeVar(lexeme) != "error":
            if isInitVar(lexeme):
                numSymb += 1
                print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
                return getTypeVar(lexeme)
            else:
                failParse('використання не ініціалізованної зінної', (numLine, lexeme, token))
        else:
            failParse('використання неоголошенної зінної', (numLine, lexeme, token))

    # третя альтернатива для Factor
    # якщо лексема - це відкриваюча дужка
    elif lexeme == '(':
        numSymb += 1
        res_pars = parseExpression(isRes=isRes)
        if not isRes and res_pars == "error":
            return "error"
        parseToken(')', 'brackets_op', '\t' * 7)
        print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
        return res_pars
    else:
        if isRes:
            failParse('невідповідність у Expression.Factor',
                  (numLine, lexeme, token, 'rel_op, int, real, id або \'(\' Expression \')\''))
        else:
            return "error"

def parseBoolExpression(isRes=True):
    global numSymb
    print('\t' * 4 + 'parseBoolExpression():')
    res_par = parseExpression(isRes=isRes)
    if res_par == "error" and not isRes:
        return "error"
    numLine, lexeme, token = getSymb()
    if token in ('rel_op'):
        numSymb += 1
        print('\t' * 5 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
    else:
        if isRes:
            failParse('невідповідність у BoolExpression', (numLine, lexeme, token, 'relop'))
        else:
            return "error"
    r_res_par = parseExpression(isRes=isRes)
    if r_res_par == "error" and not isRes:
        return "error"
    res_val = getTypeOp(res_par, lexeme, r_res_par)
    if res_val == "error":
        if isRes:
            failParse("присвоєння хибного типу", (numSymb, lexeme, getTypeVar(lexeme), "bool"))
    return res_val

def parseExpressionList():
    global numSymb
    print('\t' * 4 + 'parseExpressionList():')
    parseToken("(","brackets_op","\t"*7)
    flag = True
    numSymb_last = 0
    numLine, lexeme, token = getSymb()
    expr_flag = False
    while flag:
        numSymb_loc = numSymb

        isBoolExp = parseBoolExpression(isRes=False)
        numSymb_last = numSymb if numSymb_last < numSymb else numSymb_last
        numSymb = numSymb_loc

        isMathExpr = parseExpression(isRes=False)
        numSymb_last = numSymb if numSymb_last < numSymb else numSymb_last
        numSymb = numSymb_loc

        isTerm = parseTerm(isRes=False)
        numSymb_last = numSymb if numSymb_last < numSymb else numSymb_last
        numSymb = numSymb_last

        if isBoolExp != "error" or  isMathExpr != "error":
            numLine, lexeme, token = getSymb()
            if lexeme == ",":
                numSymb +=1
            else:
                flag = False
        else:
            if isTerm != "error":
                numLine, lexeme, token = getSymb()
                if lexeme == ",":
                    numSymb += 1
                else:
                    flag = False
            else:
                failParse('невідповідність у ExpressionList',
                      (numLine, lexeme, token, "Expression, BoolExpr, Id"))
    parseToken(")", "brackets_op", "\t" * 7)


# Функція для розбору Statement за правилом для Assign
def parseAssign():
    global numSymb
    print('\t' * 4 + 'parseAssign():')
    sign = 1

    # взяти поточну лексему
    numLine, lexeme, token = getSymb()
    num_line_id, id_lexeme, id_token = getSymb()
    id_type = getTypeVar(lexeme)
    if id_type == "error":
        failParse('використання неоголошенної зінної', (numLine, lexeme, token))
        return False

    # встановити номер нової поточної лексеми
    numSymb += 1

    print('\t' * 5 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
    numLine, lexeme, token = getSymb()
    numSymb += 1

    start_n = numSymb
    end_n = 0
    if (lexeme, token) == (":=","assign_op"):
        numLine, lexeme, token = getSymb()
        if token in ('add_op'):
            if lexeme == "-":
                sign = -1
            numSymb += 1

        is_math = parseExpression(isRes=False)
        end_n = numSymb if numSymb > end_n and is_math != "error" else end_n

        numSymb = start_n
        is_bool = parseBoolExpression(isRes=False)
        end_n = numSymb if numSymb > end_n and is_bool != "error" else end_n

        numSymb = start_n
        n_numLine, n_lexeme, n_token = getSymb()
        numSymb += 1
        is_boolean = "bool" if n_token=="keyword" and n_lexeme in ["true", "false"] else "error"
        end_n = numSymb if numSymb > end_n and is_boolean else end_n
        numSymb = end_n
        if is_math != "error" or is_bool != "error" or is_boolean != "error":
            #TODO: change to real val
            if is_boolean != "error":
                if id_type != is_boolean:
                    failParse("присвоєння хибного типу",(num_line_id, id_lexeme, id_type, "bool"))
                initVar(id_lexeme, 1 * sign)
                parseToken(";", "punct", "\t" * 7)
                return True
            elif is_bool != "error":
                if id_type != is_bool:
                    failParse("присвоєння хибного типу",(num_line_id, id_lexeme, id_type, "bool"))
                initVar(id_lexeme, 1 * sign)
                parseToken(";", "punct", "\t" * 7)
                return True
            elif is_math != "error":
                if id_type != is_math:
                    failParse("присвоєння хибного типу",(num_line_id, id_lexeme, id_type, is_math))
                initVar(id_lexeme, 1 * sign)
                parseToken(";", "punct", "\t" * 7)
                return
        return False
    else:
        return False

# Функція для розбору Statement за правилом для IfStatement
def parseIf():
    global numSymb
    print('\t' * 4 + 'parseIf():')
    numLine, lexem, token = getSymb()
    if lexem == 'if' and token == 'keyword':
        numSymb += 1
        parseToken('(', 'brackets_op', '\t' * 5)
        start_numSymb = numSymb
        end_numSymb = 0
        is_bool = parseBoolExpression(isRes=False)
        end_numSymb = numSymb
        numSymb = start_numSymb
        is_term = parseExpression(isRes=False)
        end_numSymb = numSymb if numSymb > end_numSymb else end_numSymb
        numSymb = end_numSymb
        flag = True
        numLine, lexem, token = getSymb()
        if is_bool=="error" and is_term in ("error", "int", "real"):
            failParse("невідповідність інструкцій", (numLine, lexem, token, "bool expression or bool id"))
        parseToken(')', 'brackets_op', '\t' * 5)
        parseToken('do', 'keyword', '\t' * 5)
        if (lexem, token)==("begin","keyword"):
            numSymb += 1
            parseStatementList()
            parseToken('end', 'keyword', '\t' * 5)
        else:
            parseStatement()
        numLine, lexem, token = getSymb()
        if (lexem, token)==("else","keyword"):
            parseToken('else', 'keyword', '\t' * 5)
            flag = True
            numLine, lexem, token = getSymb()
            if (lexem, token) == ("begin", "keyword"):
                numSymb += 1
                parseStatementList()
                parseToken('end', 'keyword', '\t' * 5)
            else:
                parseStatement()
        return True
    else:
        return False

# Функція для розбору Statement за правилом для ForStatement
def parseFor():
    global numSymb
    print('\t' * 4 + 'parseFor():')
    numLine, lexeme, token = getSymb()
    if lexeme == 'for' and token == 'keyword':
        numSymb += 1
        numLine, lexeme, token = getSymb()
        numLine_id, lexeme_id, token_id = getSymb()
        if token == "id":
            if getTypeVar(lexeme) != "error":
                numSymb += 1
                parseToken(':=', 'assign_op', '\t' * 5)
                type = parseExpression()
                if type != "int":
                    failParse('присвоєння хибного типу', (numLine, lexeme, type, 'int'))
                #TODO: change to real val
                initVar(lexeme_id, 1)
            else:
                failParse('використання неоголошенної зінної', (numLine, lexeme, token))
                return False
        else:
            return False

        _, lexeme, token = getSymb()
        if (lexeme, token) == ("down","keyword"):
            numSymb += 1
        parseToken('to', 'keyword', '\t' * 5)
        numLine, lexeme, token = getSymb()
        type = parseExpression()
        if type != "int":
            failParse('присвоєння хибного типу', (numLine, lexeme, type, 'int'))
        parseToken('do', 'keyword', '\t' * 5)
        flag = True
        numLine, lexeme, token = getSymb()
        if (lexeme, token) == ("begin", "keyword"):
            numSymb += 1
            parseStatementList()
            parseToken('end', 'keyword', '\t' * 5)
        else:
            parseStatement()
        numLine, lexeme, token = getSymb()
        if (lexeme, token) == ("else", "keyword"):
            parseToken('else', 'keyword', '\t' * 5)
            flag = True
            numLine, lexeme, token = getSymb()
            if (lexeme, token) == ("begin", "keyword"):
                numSymb += 1
                parseStatementList()
                parseToken('end', 'keyword', '\t' * 5)
            else:
                parseStatement()
        return True
    else:
        return False

# Функція для розбору Statement за правилом для Outp
def parseWrite():
    global numSymb
    print('\t' * 4 + 'parseWrite():')
    numLine, lexeme, token = getSymb()
    if (lexeme, token) == ("write", "keyword"):
        numSymb += 1
        parseExpressionList()
        parseToken(";", "punct", "\t" * 5)
        return True
    else:
        return False

# Функція для розбору Statement за правилом для Inp
def parseRead():
    global numSymb
    print('\t' * 4 + 'parseRead():')
    numLine, lexeme, token = getSymb()
    if (lexeme, token) == ("read", "keyword"):
        numSymb += 1
        parseToken("(", "brackets_op", "\t" * 5)
        flag = True
        while flag:
            numLine, lexeme, token = getSymb()
            if token == "id":
                if getTypeVar(lexeme) != "error":
                    #TODO: switch to real val (for now it will be 1)
                    initVar(lexeme, 1)
                    numSymb += 1
                else:
                    failParse('використання неоголошенної зінної', (numLine, lexeme, token))
                    return False
            else:
                failParse('невідповідність у Read.ExpressionList', (numLine, lexeme, token, "Id"))
                return False
            numLine, lexeme, token = getSymb()
            if (lexeme, token) == (",","punct"):
                numSymb += 1
            else:
                flag = False
        parseToken(")", "brackets_op", "\t" * 5)
        parseToken(";", "punct", "\t" * 5)
        return True
    else:
        return False



# Обробити помилки
# вивести поточну інформацію та діагностичне повідомлення
def failParse(str, tuple):
    if str == 'неочікуваний кінець програми':
        (lexeme, token, numRow) = tuple
        print('Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {1}. \n\t Очікувалось - {0}'.format(
                (lexeme, token), numRow))
        exit(401)

    elif str == 'getSymb(): неочікуваний кінець програми':
        numRow = tuple
        print('Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {0}. \n\t Останній запис - {1}'.format(
                numRow, tableOfSymb[numRow - 1]))
        exit(402)

    elif str == 'невідповідність токенів':
        (numLine, lex, tok, lexeme, token) = tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - ({3},{4}).'.format(
            numLine, lex, tok, lexeme, token))
        exit(403)

    elif str == 'невідповідність інструкцій':
        (numLine, lexeme, token, additional_msg) = tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(
                numLine, lexeme, token, additional_msg))
        exit(404)

    elif str == 'невідповідність у Expression.Factor':
        (numLine, lexeme, token, additional_msg) = tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(
                numLine, lexeme, token, additional_msg))
        exit(405)

    elif str == 'невідповідність у ExpressionList':
        (numLine, lexeme, token, additional_msg) = tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(
                numLine, lexeme, token, additional_msg))
        exit(406)

    elif str == 'невідповідність у Read.ExpressionList':
        (numLine, lexeme, token, additional_msg) = tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(
                numLine, lexeme, token, additional_msg))
        exit(407)

    elif str == 'невідповідність у BoolExpression':
        (numLine, lexeme, token, additional_msg) = tuple
        print('Parser ERROR: \n\t В рядку {0} неочікуваний елемент ({1},{2}). \n\t Очікувався - {3}.'.format(
                numLine, lexeme, token, additional_msg))
        exit(408)

    elif str == 'використання неоголошенної зінної':
        (numLine, lexeme, _) = tuple
        print('Parser ERROR: \n\t В рядку {0} використання неоголошенної змінної {1}. \n\t'.format(
                numLine, lex))
        exit(409)

    elif str == 'використання не ініціалізованної зінної':
        (numLine, lexeme, _) = tuple
        print('Parser ERROR: \n\t В рядку {0} використання не ініціалізованної змінної {1}. \n\t'.format(
                numLine, lex))
        exit(410)

    elif str == 'присвоєння хибного типу':
        (numLine, lexeme, type, additional_msg) = tuple
        print(
            'Parser ERROR: \n\t В рядку {0} присвоєння хибного типу для змінної {1}. Очікувався тип {2}, а отримано {3} \n\t'.format(numLine, lexeme, type, additional_msg))
        exit(411)

    elif str == 'повторне оголошення змінної':
        (numLine, lexeme, type, additional_msg) = tuple
        print(
            'Parser ERROR: \n\t В рядку {0} повторне оголошення змінної {1}. \n\t'.format(numLine, lexeme))
        exit(412)

    else:
        (numLine, lexeme, token, additional_msg) = tuple
        print('Parser ERROR: \n\t Щось пішло не так!')
        exit(400)


parseProgram()
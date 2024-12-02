#from DubStep_lexer import lex
from DubStep_lexer import tableOfSymb, tableOfConst


# номер рядка таблиці розбору/лексем/символів ПРОГРАМИ tableOfSymb
numSymb = 1
curNumLine = 1
identId = 1
# довжина таблиці символів програми
# він же - номер останнього запису
len_tableOfSymb = 0

tableOfVar={}
tableOfLbl={}
postfCode = []
codeIl = []

# Функція для розбору за правилом
# Program = program Id var DeclarList begin StatementList end.
# читає таблицю розбору tableOfSymb
def parseProgram():
    global numSymb, curNumLine, identId, len_tableOfSymb, tableOfVar

    len_tableOfSymb = len(tableOfSymb)
    print(('len_tableOfSymb', len_tableOfSymb))


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
        codeIl.append("ret")
        FSuccess = True
        return FSuccess
    
    except SystemExit as e:
        # Повідомити про факт виявлення помилки
        print('Parser: Аварійне завершення програми з кодом {0}'.format(e))

        FSuccess = False
        return FSuccess



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
    global numSymb, postfCode
    print('\t' * 5 + 'parseExpression():')
    res_pars = parseTerm(isRes=isRes)
    if not isRes and res_pars == "error":
        return "error"
    F = True
    # продовжувати розбирати Доданки (Term)
    # розділені лексемами '+' або '-'
    while F:
        numLine, lexeme, token = getSymb()
        sign_lex = lexeme
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
            if isRes:
                postfCode.append((sign_lex, "add_op"))
                postfixCLR_codeGen(sign_lex, 0)
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
        sign_tok = token
        sign_lex = lexeme
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
            if isRes:
                postfCode.append((sign_lex, sign_tok))
                postfixCLR_codeGen(sign_lex, 0)
        else:
            F = False
    return res_pars

def parseFactor(isRes=True, isFirstMinus=True):
    global numSymb
    print('\t' * 7 + 'parseFactor():')
    numLine, lexeme, token = getSymb()
    print('\t' * 7 + 'parseFactor():=============рядок: {0}\t (lexeme, token):{1}'.format(numLine, (lexeme, token)))

    # перша і друга альтернативи для Factor
    # якщо лексема - це константа або ідентифікатор
    if token in ('int', 'real'):
        numSymb += 1
        print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
        if isRes:
            postfCode.append((lexeme, token))
            postfixCLR_codeGen(token, lexeme)
        return getTypeConst(lexeme)
    
    elif token in ('add_op'):
        if not isFirstMinus:
            failParse("присвоєння хибного типу", (numLine, lexeme, "подвійний мінус", "мінус лише один"))
        numSymb += 1
        print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
        res_pars = parseFactor(isRes=isRes, isFirstMinus=False)
        if isRes:
            lex_t = -1.0
            lex_t = -1 if res_pars=="int" else lex_t
            postfCode.append((lex_t, res_pars))
            postfixCLR_codeGen(res_pars, lex_t)
            postfCode.append(("*", "mult_op"))
            postfixCLR_codeGen("*", 0)
        return res_pars


    elif token == "id":
        if getTypeVar(lexeme) != "error":
            if isInitVar(lexeme):
                numSymb += 1
                print('\t' * 7 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
                if isRes:
                    postfCode.append((lexeme, "r-val"))
                    postfixCLR_codeGen("r-val", lexeme)
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
    global numSymb, postfCode
    rel_tok = ""
    rel_lex = ""
    print('\t' * 4 + 'parseBoolExpression():')
    res_par = parseExpression(isRes=isRes)
    if res_par == "error" and not isRes:
        return "error"
    numLine, lexeme, token = getSymb()
    if token in ('rel_op'):
        numSymb += 1
        print('\t' * 5 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
        rel_tok = token
        rel_lex = lexeme
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
    if isRes:
        postfCode.append((rel_lex, rel_tok))
        postfixCLR_codeGen(rel_lex, 0)
    return res_val

def parseExpressionList():
    global numSymb
    print('\t' * 4 + 'parseExpressionList():')
    parseToken("(","brackets_op","\t"*7)
    flag = True
    numSymb_last = 0
    numLine, lexeme, token = getSymb()
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
        numSymb = numSymb_loc

        ind_type = ""

        if isBoolExp != "error" or  isMathExpr != "error":
            if isBoolExp != "error":
                parseBoolExpression()
                ind_type = "bool"
            elif isMathExpr != "error":
                parseExpression()
                ind_type = isMathExpr
            numLine, lexeme, token = getSymb()
            if lexeme == ",":
                postfCode.append(("OUT", "out_op"))
                codeIl.append(f"call    void[mscorlib] System.Console::WriteLine({getTypeNameIl(ind_type)})")
                numSymb +=1
            else:
                flag = False
        else:
            if isTerm != "error":
                numLine, lexeme, token = getSymb()

                postfCode.append((lex, "r-val"))
                postfixCLR_codeGen("r-val", lex)
                lex_n = lex
                numSymb += 1
                numLine, lex, tok = getSymb()
                ind_type = tableOfVar[lex_n][1]

                if lexeme == ",":
                    numSymb += 1
                    postfCode.append(("OUT", "out_op"))
                    codeIl.append(f"call    void[mscorlib] System.Console::WriteLine({getTypeNameIl(ind_type)})")
                else:
                    flag = False
            else:
                failParse('невідповідність у ExpressionList',
                      (numLine, lexeme, token, "Expression, BoolExpr, Id"))
    postfCode.append(("OUT", "out_op"))
    codeIl.append(f"call    void[mscorlib] System.Console::WriteLine({getTypeNameIl(ind_type)})")
    parseToken(")", "brackets_op", "\t" * 7)



# Функція для розбору Statement за правилом для Assign
def parseAssign():
    global numSymb, postfCode
    print('\t' * 4 + 'parseAssign():')
    sign = 1

    # взяти поточну лексему
    numLine, lexeme, token = getSymb()
    num_line_id, id_lexeme, id_token = getSymb()
    id_type = getTypeVar(lexeme)
    if id_type == "error":
        failParse('використання неоголошенної зінної', (numLine, lexeme, token))
        return False
    postfCode.append((lexeme, "l-val"))
    postfixCLR_codeGen("l-val", lexeme)
    # встановити номер нової поточної лексеми
    numSymb += 1

    print('\t' * 5 + 'в рядку {0} - {1}'.format(numLine, (lexeme, token)))
    numLine, lexeme, token = getSymb()
    numSymb += 1

    start_n = numSymb
    end_n = 0
    is_min = False
    if (lexeme, token) == (":=","assign_op"):
        numLine, lexeme, token = getSymb()
        if token in ('add_op'):
            postfCode.append((0.0, id_type))
            postfixCLR_codeGen(id_type, 0.0)
            if lexeme == "-":
                is_min = True
                sign = -1
            numSymb += 1
            start_n = numSymb

        is_math = parseExpression(isRes=False)
        #end_n = numSymb if numSymb > end_n and is_math != "error" else end_n

        numSymb = start_n
        is_bool = parseBoolExpression(isRes=False)
        #end_n = numSymb if numSymb > end_n and is_bool != "error" else end_n

        numSymb = start_n
        n_numLine, n_lexeme, n_token = getSymb()
        #numSymb += 1
        is_boolean = "bool" if n_token=="keyword" and n_lexeme in ["true", "false"] else "error"
        #end_n = numSymb if numSymb > end_n and is_boolean else end_n
        #numSymb = end_n
        if is_math != "error" or is_bool != "error" or is_boolean != "error":
            if is_bool != "error":
                if id_type != is_boolean:
                    failParse("присвоєння хибного типу",(num_line_id, id_lexeme, id_type, "bool"))
                parseBoolExpression()
                initVar(id_lexeme, 1 * sign)
                parseToken(";", "punct", "\t" * 7)
                postfCode.append((":=", "assign_op"))
                postfixCLR_codeGen(":=", id_type)
                return True
            
            elif is_math != "error":
                if is_math not in ("int", "real"):
                    failParse("присвоєння хибного типу",(num_line_id, id_lexeme, id_type, is_math))
                parseExpression()
                initVar(id_lexeme, 1 * sign)
                parseToken(";", "punct", "\t" * 7)
                if is_min:
                    postfCode.append(("-", "add_op"))
                    postfixCLR_codeGen("-", 0)
                postfCode.append((":=", "assign_op"))
                postfixCLR_codeGen(":=", id_type)
                return True
            
            elif is_boolean != "error":
                if id_type != is_boolean:
                    failParse("присвоєння хибного типу",(num_line_id, id_lexeme, id_type, "bool"))
                n_numLine, n_lex, n_tok = getSymb()
                postfCode.append((n_lex, "bool"))
                postfixCLR_codeGen("bool", n_lex)
                numSymb += 1
                initVar(id_lexeme, 1 * sign)
                postfCode.append((":=", "assign_op"))
                postfixCLR_codeGen(":=", id_type)
                parseToken(";", "punct", "\t" * 7)
                return True
                
        return False
    else:
        return False

# Функція для розбору Statement за правилом для IfStatement
def parseIf():
    global numSymb, tableOfLbl, postfCode
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
        numSymb = start_numSymb
        flag = True
        numLine, lexem, token = getSymb()
        if is_bool=="error" and is_term in ("error", "int", "real"):
            failParse("невідповідність інструкцій", (numLine, lexem, token, "bool expression or bool id"))
        else:
            if is_bool!="error":
                parseBoolExpression()
            else:
                parseExpression()
        parseToken(')', 'brackets_op', '\t' * 5)
        parseToken('do', 'keyword', '\t' * 5)

        name_mf = "m" + str(len(tableOfLbl) + 1)
        tableOfLbl[name_mf] = 0
        name_ms = "m" + str(len(tableOfLbl) + 1)
        tableOfLbl[name_ms] = 0

        postfCode.append((name_mf, "label"))
        postfCode.append(("JF", "jf"))
        codeIl.append("brfalse    " + name_mf)
        if (lexem, token)==("begin","keyword"):
            numSymb += 1
            parseStatementList()
            parseToken('end', 'keyword', '\t' * 5)
        else:
            parseStatement()
        numLine, lexem, token = getSymb()

        if (lexem, token)==("else","keyword"):
            postfCode.append((name_ms, "label"))
            postfCode.append(("JMP", "jmp"))
            codeIl.append("br     "+name_ms)
            postfCode.append((name_mf, "label"))
            codeIl.append(f"{name_mf}:")
            tableOfLbl[name_mf] = len(postfCode) + 1
            postfCode.append((":", "colon"))

            parseToken('else', 'keyword', '\t' * 5)
            flag = True
            numLine, lexem, token = getSymb()
            if (lexem, token) == ("begin", "keyword"):
                numSymb += 1
                parseStatementList()
                parseToken('end', 'keyword', '\t' * 5)
            else:
                parseStatement()
            postfCode.append((name_ms, "label"))
            codeIl.append(f"{name_ms}:")
            tableOfLbl[name_ms] = len(postfCode) + 1
            postfCode.append((":", "colon"))

        return True
    else:
        return False

# Функція для розбору Statement за правилом для ForStatement
def parseFor():
    global numSymb, tableOfLbl, postfCode
    print('\t' * 4 + 'parseFor():')
    numLine, lexeme, token = getSymb()
    if lexeme == 'for' and token == 'keyword':
        numSymb += 1
        numLine, lexeme, token = getSymb()
        numLine_id, lexeme_id, token_id = getSymb()
        prm = lexeme
        if token == "id":
            if getTypeVar(lexeme) != "error":
                postfCode.append((prm, "l-val"))
                postfixCLR_codeGen("l-val", prm)
                numSymb += 1
                parseToken(':=', 'assign_op', '\t' * 5)
                type = parseExpression()
                if type != "int":
                    failParse('присвоєння хибного типу', (numLine, lexeme, type, 'int'))
                initVar(lexeme_id, 1)
                postfCode.append((":=", "assign_op"))
                postfixCLR_codeGen(":=", type)
            else:
                failParse('використання неоголошенної зінної', (numLine, lexeme, token))
                return False
        else:
            return False

        _, lexeme, token = getSymb()

        _r1 = f"_r{len(tableOfVar)}"
        _r2 = f"_r{len(tableOfVar) + 1}"
        tableOfVar[_r1]=(len(tableOfVar)+1,'int',1)
        tableOfVar[_r2] = (len(tableOfVar)+1, 'int', 1)

        name_mf = "m" + str(len(tableOfLbl) + 1)
        name_ms = "m" + str(len(tableOfLbl) + 2)
        name_mt = "m" + str(len(tableOfLbl) + 3)
        tableOfLbl[name_mt] = 0
        tableOfLbl[name_mt] = 0
        tableOfLbl[name_mt] = 0
        postfCode.append((_r1, "l-val"))
        postfixCLR_codeGen("l-val", _r1)
        postfCode.append((1, "int"))
        postfixCLR_codeGen("int", 1)
        postfCode.append((":=", "assign_op"))
        postfixCLR_codeGen(":=", "int")

        postfCode.append((name_mf, "label"))
        tableOfLbl[name_mf] = len(postfCode)+1
        postfCode.append((":", "colon"))
        codeIl.append(f"{name_mf}:")
        postfCode.append((_r2, "l-val"))
        postfixCLR_codeGen("l-val", _r2)

        postfCode.append((0, "int"))
        postfixCLR_codeGen("int", 0)
        postfCode.append((1, "int"))
        postfixCLR_codeGen("int", 1)

        is_down = False
        if (lexeme, token) == ("down","keyword"):
            numSymb += 1
            is_down = True
            postfCode.append(("-", "add_op"))
            postfixCLR_codeGen("-", 0)
        else:
            postfCode.append(("+", "add_op"))
            postfixCLR_codeGen("+", 0)

        parseToken('to', 'keyword', '\t' * 5)

        postfCode.append((":=", "assign_op"))
        postfixCLR_codeGen(":=", "int")
        postfCode.append((_r1, "r-val"))
        postfixCLR_codeGen("r-val", _r1)
        postfCode.append((0, "int"))
        postfixCLR_codeGen("int", 0)
        postfCode.append(("=", "rel_op"))
        postfixCLR_codeGen("=", 0)
        postfCode.append((name_ms, "label"))
        postfCode.append(("JF", "jf"))
        codeIl.append("brfalse    "+name_ms)
        postfCode.append((prm, "l-val"))
        postfixCLR_codeGen("l-val", prm)
        postfCode.append((prm, "r-val"))
        postfixCLR_codeGen("r-val", prm)
        postfCode.append((_r2, "r-val"))
        postfixCLR_codeGen("r-val", _r2)
        postfCode.append(("+", "add_op"))
        postfixCLR_codeGen("+", 0)
        postfCode.append((":=", "assign_op"))
        postfixCLR_codeGen(":=", tableOfVar[prm][1])
        postfCode.append((name_ms, "label"))
        tableOfLbl[name_ms] = len(postfCode)+1
        postfCode.append((":", "colon"))
        codeIl.append(f"{name_ms}:")
        postfCode.append((_r1, "l-val"))
        postfixCLR_codeGen("l-val", _r1)
        postfCode.append((0, "int"))
        postfixCLR_codeGen("int", 0)
        postfCode.append((":=", "assign_op"))
        postfixCLR_codeGen(":=", "int")
        postfCode.append((prm, "r-val"))
        postfixCLR_codeGen("r-val", prm)

        numLine, lexeme, token = getSymb()
        type = parseExpression()
        if type != "int":
            failParse('присвоєння хибного типу', (numLine, lexeme, type, 'int'))
        parseToken('do', 'keyword', '\t' * 5)
        postfCode.append(("-", "add_op"))
        postfixCLR_codeGen("-", 0)
        postfCode.append((_r2, "r-val"))
        postfixCLR_codeGen("r-val", _r2)
        postfCode.append(("*", "mult_op"))
        postfixCLR_codeGen("*", 0)
        postfCode.append((0, "int"))
        postfixCLR_codeGen("int", 0)
        postfCode.append(("<=", "rel_op"))
        postfixCLR_codeGen("<=", 0)
        postfCode.append((name_mt, "label"))
        postfCode.append(("JF", "jf"))
        codeIl.append("brfalse    "+name_mt)

        flag = True
        numLine, lexeme, token = getSymb()
        if (lexeme, token) == ("begin", "keyword"):
            numSymb += 1
            parseStatementList()
            parseToken('end', 'keyword', '\t' * 5)
        else:
            parseStatement()

        postfCode.append((name_mf, "label"))
        postfCode.append(("JMP", "jmp"))
        codeIl.append("br    "+name_mf)
        postfCode.append((name_mt, "label"))
        tableOfLbl[name_mt] = len(postfCode)+1
        postfCode.append((":", "colon"))
        codeIl.append(f"{name_mt}:")

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
    global numSymb, postfCode
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
                    initVar(lexeme, 1)
                    postfCode.append((lexeme, "r-val"))
                    postfixCLR_codeGen("r-val", lexeme)
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

            postfCode.append(("IN", "in_op"))
        parseToken(")", "brackets_op", "\t" * 5)
        parseToken(";", "punct", "\t" * 5)
        return True
    else:
        return False



# Обробити помилки
# вивести поточну інформацію та діагностичне повідомлення
def failParse(str, tuple):
    if str == 'неочікуваний кінець програми':
        (lexeme, token, numSymb) = tuple
        print('Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {1}. \n\t Очікувалось - {0}'.format(
                (lexeme, token), numSymb))
        exit(401)

    elif str == 'getSymb(): неочікуваний кінець програми':
        numSymb = tuple
        print('Parser ERROR: \n\t Неочікуваний кінець програми - в таблиці символів (розбору) немає запису з номером {0}. \n\t Останній запис - {1}'.format(
                numSymb, tableOfSymb[numSymb - 1]))
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
                numLine, lexeme))
        exit(409)

    elif str == 'використання не ініціалізованної зінної':
        (numLine, lexeme, _) = tuple
        print('Parser ERROR: \n\t В рядку {0} використання не ініціалізованної змінної {1}. \n\t'.format(
                numLine, lexeme))
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



def sufTypes(type_v):
    if type_v == "int":
        return 'i4'
    else:
        return 'r4'

def getTypeNameIl(type_v):
    if type_v == "bool": return "bool"
    elif type_v == "int": return "int32"
    elif type_v == "real": return "float32"
    else: return "error"

def relopCRL(rel_op):
    if rel_op == "<": return 'clt'
    elif rel_op == ">": return 'cgt'
    elif rel_op == "<=": return 'cle'
    elif rel_op == ">=": return 'cqe'
    elif rel_op == "=": return 'ceq'
    elif rel_op == "<>": return 'beg'
    else: return ""

def postfixCLR_codeGen(casse, toTran):
    global codeIl
    if casse == 'l-val':
        codeIl.append('ldloca   '+toTran)
    elif casse == ":=":
        sufficsType = sufTypes(toTran)
        codeIl.append('stind.'+sufficsType)
    elif casse == "+":
        codeIl.append('add')
    elif casse == "-":
        codeIl.append('sub')
    elif casse == "*":
        codeIl.append('mul')
    elif casse == "/":
        codeIl.append('div')
    elif casse == "r-val":
        codeIl.append('ldloc    '+toTran)
    elif casse in ("int", "real"):
        sufficsType = sufTypes(casse)
        codeIl.append('ldc.'+sufficsType+f"   {toTran}")
    elif casse == "boolconst":
        if toTran=="true":
            val = "1"
        elif toTran=="false":
            val = "0"
        codeIl.append('ldc.i4   ' + val)
    elif relopCRL(casse) != "":
        relop = relopCRL(casse)
        codeIl.append(relop)

def saveIlCode(filename):
    str = '''

//  Microsoft (R) .NET Framework IL Disassembler.  Version 4.8.3928.0
//  Copyright (c) Microsoft Corporation.  All rights reserved.



// Metadata version: v4.0.30319
.assembly extern mscorlib
{
  .publickeytoken = (B7 7A 5C 56 19 34 E0 89 )                         // .z\V.4..
  .ver 4:0:0:0
}
.assembly file1
{
  .custom instance void [mscorlib]System.Runtime.CompilerServices.CompilationRelaxationsAttribute::.ctor(int32) = ( 01 00 08 00 00 00 00 00 ) 
  .custom instance void [mscorlib]System.Runtime.CompilerServices.RuntimeCompatibilityAttribute::.ctor() = ( 01 00 01 00 54 02 16 57 72 61 70 4E 6F 6E 45 78   // ....T..WrapNonEx
                                                                                                             63 65 70 74 69 6F 6E 54 68 72 6F 77 73 01 )       // ceptionThrows.

  // --- The following custom attribute is added automatically, do not uncomment -------
  //  .custom instance void [mscorlib]System.Diagnostics.DebuggableAttribute::.ctor(valuetype [mscorlib]System.Diagnostics.DebuggableAttribute/DebuggingModes) = ( 01 00 07 01 00 00 00 00 ) 

  .hash algorithm 0x00008004
  .ver 0:0:0:0
}
.module file1.exe
// MVID: {19EA7ACA-85EF-4B03-BE73-5F9ED591B011}
.imagebase 0x00400000
.file alignment 0x00000200
.stackreserve 0x00100000
.subsystem 0x0003       // WINDOWS_CUI
.corflags 0x00000001    //  ILONLY
// Image base: 0x06620000


// =============== CLASS MEMBERS DECLARATION ===================

.class public auto ansi beforefieldinit Program1
       extends [mscorlib]System.Object
{
  .method public hidebysig static void  Main() cil managed
  {
    .entrypoint
    // Code size       16 (0x10)
    .maxstack  2
    .locals init '''

    loc = "("+", ".join([f"{getTypeNameIl(val[1])} {key}" for key,val in tableOfVar.items()])+")"
    code_t = "\n".join([f"IL_{i:04x}:  "+codeIl[i] for i in range(len(codeIl))])

    str2 = '''
  } // end of method Program1::Main

  .method public hidebysig specialname rtspecialname 
          instance void  .ctor() cil managed
  {
    // Code size       8 (0x8)
    .maxstack  8
    IL_0000:  ldarg.0
    IL_0001:  call       instance void [mscorlib]System.Object::.ctor()
    IL_0006:  nop
    IL_0007:  ret
  } // end of method Program1::.ctor

} // end of class Program1


// =============================================================

// *********** DISASSEMBLY COMPLETE ***********************
// WARNING: Created Win32 resource file file1.res
    '''
    final = str+loc+code_t+str2
    f = open(filename+".il", "w")
    f.write(final)
    f.close()
    print("Il код збережено до "+filename+".il")
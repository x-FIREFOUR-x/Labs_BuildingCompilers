from lexer import lex
from lexer import tableOfSymb


FSucces = lex()

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
        parseId()

        # перевірити наявність ключового слова 'var'
        parseToken('var', 'keyword', '')
        # перевірити визначення змінних
        parseId()

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
def parseId():
    global numSymb
    print('\t' * 4 + 'parseIdentByItself():')

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
        failParse('parseId(): не очікуванний символ', (numLine, lexeme))

    next_numLine, next_lexeme, next_token = getSymb()
    numSymb += 1
    print('\t' * 5 + 'в рядку {0} - {1}'.format(next_numLine, (next_lexeme, next_token)))

        #перевірити перерахунок змінних
    if (next_lexeme, next_token) == (",","punct"):
        parseId()
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
                parseId()
            return True
        else:
            failParse('parseId(): невідомий тип', (numLine, next_lexeme, next_token))
    else:
        return False

# Додати в таблицю змінних нову змінну
def addIdVar(numLine, lex, lex_type, val):
    index = tableOfVar.get(lex)
    if index is None:
        index = len(tableOfVar) + 1
        tableOfVar[lex] = (index, lex_type, val)
    else: failParse("повторне оголошення змінної", (numLine, lex, lex_type, val))

# Додати дані про тип для змінної в таблицю змінних
def addTypeForIdVar(type_name):
    flag = True
    for id in tableOfVar:
        if tableOfVar[id][1] == "undefined":
            tableOfVar[id] = (tableOfVar[id][0],type_name,tableOfVar[id][2])





parseProgram()
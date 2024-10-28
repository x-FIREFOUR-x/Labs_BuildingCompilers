from lexer import lex
from lexer import tableOfSymb


FSucces = lex()

print('-'*265)
print('tableOfSymb:{0}'.format(tableOfSymb))
print('-'*265)


# номер рядка таблиці розбору/лексем/символів ПРОГРАМИ tableOfSymb
numRow = 1
curNumLine = 1
identId = 1
# довжина таблиці символів програми
# він же - номер останнього запису
len_tableOfSymb = len(tableOfSymb)
print(('len_tableOfSymb', len_tableOfSymb))

tableOfVar={}


# Функція для розбору за правилом
# Program = program var begin StatementList end.
# читає таблицю розбору tableOfSymb
def parseProgram():
    try:
        # перевірити наявність ключового слова 'program' та прочитати ім'я програми
        parseToken('program', 'keyword', '')
        parseIdentByItself()

        # перевірити наявність ключового слова 'var' та прочитати ім'я зміниих
        parseToken('var', 'keyword', '')
        parseIdentByItself()

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


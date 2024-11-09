from DubStep_lexer import *
from DubStep_parser import *
from postfixMachine import *

len_tableOfSymb = 0


def compileToPOstfix(fileName):
    global len_tableOfSymb
    print("Start Lexer")
    FSuccess = lex(fileName)
    if not FSuccess:
        exit(1)
    print("Lexer - Success")
    len_tableOfSymb = len(tableOfSymb)
    print("-"*55)
    print("Start parser")
    FSuccess = parseProgram()
    if not FSuccess:
        exit(1)
    print("Parser - Success")
    print("-" * 55)
    print('-' * 30)
    print('tableOfSymb:{0}'.format(tableOfSymb))
    print('tableOfId:{0}'.format(tableOfId))
    print('tableOfConst:{0}'.format(tableOfConst))
    print('tableOfVar:{0}'.format(tableOfVar))
    print('postCode:{0}'.format(postfCode))
    print('CIL Code:{0}'.format(codeIl))
    print('-' * 30)


    pm1 = PSM()
    pm1.tableOfId = tableOfVar
    pm1.tableOfLabel = tableOfLbl
    pm1.tableOfConst = tableOfConst
    pm1.postfixCode = postfCode
    pm1.serv()
    pm1.savePostfixCode(fileName)
    pm1.loadPostfixFile(fileName)  # завантаження .postfix - файла

    pm1.postfixExec()


compileToPOstfix("test2.ds")
#compileToPOstfix("testError16.ds")
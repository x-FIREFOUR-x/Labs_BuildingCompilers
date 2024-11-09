from DubStep_lexer import *
from DubStep_parser import *


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
    print('-' * 30)



compileToPOstfix("test.ds")
#compileToPOstfix("testError16.ds")
from DubStep_lexer import *
from DubStep_parser import *
from postfixMachine import *
from CLRMachine import *

len_tableOfSymb = 0

DIR_WITH_TESTS = "tests/"
DIR_WITH_POSTFIX = "postfix/"
DIR_WITH_IL = "il/"

def compileToPOstfix(fileName):
    global len_tableOfSymb
    print("Start Lexer")
    FSuccess = lex(DIR_WITH_TESTS + fileName)
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

    clr = CLRM()
    clr.tableOfId = tableOfVar
    clr.codeIl = codeIl
    clr.saveCLICode(DIR_WITH_IL, fileName[: fileName.find(".")])

    pm1 = PSM()
    pm1.tableOfId = tableOfVar
    pm1.tableOfLabel = tableOfLbl
    pm1.tableOfConst = tableOfConst
    pm1.postfixCode = postfCode
    pm1.serv()
    pm1.savePostfixCode(DIR_WITH_POSTFIX + fileName)
    pm1.loadPostfixFile(DIR_WITH_POSTFIX + fileName)  # завантаження .postfix - файла

    pm1.postfixExec()




compileToPOstfix("test.ds")
#compileToPOstfix("tests/testError16.ds")2
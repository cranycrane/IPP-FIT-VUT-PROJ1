from scanner import Scanner, TokenType, KeywordType, Token, LexerContext
from xmlgenerator import XmlGenerator
import sys
from exceptions import *

class Parse:
    def __init__(self, file):
        self.file = file
        self.scanner = Scanner(self.file)
        self.scannerIter = iter(self.scanner)
        self.counter = 1
        self.xmlgenerator = XmlGenerator()
    
    def execute(self):
        try:
            self.parse()
        except WrongHeaderException as err:
            print(err, file=sys.stderr)
            sys.exit(21)
        except SyntaxErrorException as err:
            print(err, file=sys.stderr)
            sys.exit(22)
        except OtherErrorException as err:
            print(err, file=sys.stderr)
            sys.exit(23)
        except ScannerException as err:
            print(err, file=sys.stderr)
            sys.exit(23)

    def parse(self):
        try:
            self.scanner.setContext(LexerContext.HEADER)
            header = self.getToken()
            #print("\nVRACIm\n")
            if header.tokenType == TokenType.NEWLINE:
                header = self.getToken()
        except ScannerException:
            raise WrongHeaderException("Chybna hlavicka IPPCode")

        if header is None or header.tokenType != TokenType.HEADER:
            raise WrongHeaderException('Chybejici hlavicka')

        token = self.checkOpcode()
        while token.tokenType != TokenType.EOF:
            tokenType = token.tokenType
            #print(token.tokenType)
            if tokenType == TokenType.NEWLINE:
                token = self.checkOpcode()
                continue
            elif tokenType != TokenType.KEYWORD:
                raise OtherErrorException(f"Syntakticka chyba, ocekavan OPCode, dostal {tokenType}")

            self.processKeyword(token.value)
            token = self.checkOpcode()

        self.xmlgenerator.generateXML()

    def processKeyword(self, keywordType):
        if keywordType in [KeywordType.MOVE, KeywordType.INT2CHAR, KeywordType.STRLEN, KeywordType.TYPE, KeywordType.NOT]:
            varToken = self.checkVar()
            symbToken = self.checkSymb()
            self.xmlgenerator.addTreeElement(keywordType, varToken, symbToken)
        elif keywordType in [KeywordType.CREATEFRAME, KeywordType.PUSHFRAME, KeywordType.POPFRAME, KeywordType.RETURN, KeywordType.BREAK]:
            self.xmlgenerator.addTreeElement(keywordType)
        elif keywordType in [KeywordType.DEFVAR, KeywordType.POPS]:
            varToken = self.checkVar()
            self.xmlgenerator.addTreeElement(keywordType, varToken)
        elif keywordType in [KeywordType.CALL, KeywordType.LABEL, KeywordType.JUMP]:
            labelToken = self.checkLabel()
            self.xmlgenerator.addTreeElement(keywordType, labelToken)
        elif keywordType in [KeywordType.JUMPIFEQ, KeywordType.JUMPIFNEQ]:
            labelToken = self.checkLabel()
            symbToken1 = self.checkSymb()
            symbToken2 = self.checkSymb()
            self.xmlgenerator.addTreeElement(keywordType, labelToken, symbToken1, symbToken2)
        elif keywordType in [KeywordType.PUSHS, KeywordType.WRITE, KeywordType.EXIT, KeywordType.DPRINT]:
            symbToken = self.checkSymb()
            self.xmlgenerator.addTreeElement(keywordType, symbToken)
        elif keywordType in [KeywordType.ADD, KeywordType.SUB, KeywordType.MUL, KeywordType.IDIV, 
                            KeywordType.LT, KeywordType.GT, KeywordType.EQ, KeywordType.AND, 
                            KeywordType.OR, KeywordType.STRI2INT, KeywordType.CONCAT,
                            KeywordType.GETCHAR, KeywordType.SETCHAR]:
            varToken = self.checkVar()
            symbToken = self.checkSymb()
            symbToken2 = self.checkSymb()
            self.xmlgenerator.addTreeElement(keywordType, varToken, symbToken, symbToken2)
        elif keywordType == KeywordType.READ:
            varToken = self.checkVar()
            typeToken = self.checkType()
            self.xmlgenerator.addTreeElement(keywordType, varToken, typeToken)
        else:
            raise SyntaxErrorException(f"Chybny nebo chybejici OPCode {keywordType}")

    def checkOpcode(self):
        self.scanner.setContext(LexerContext.OPCODE)
        try:
            self.checkNewLine()
            token = self.getToken()
        except ScannerException as e:
            raise SyntaxErrorException(f"Chyba: OPCode chyba, got: {e}")
        return token

    def checkNewLine(self):
        try:
            token = self.getToken()
            if token.tokenType != TokenType.NEWLINE and token.tokenType != TokenType.EOF:
                raise OtherErrorException(f"Chyba: Syntakticka chyba, ocekavan novy radek, ziskal {token.tokenType}, {token.value}")
        except ScannerException as e:
            raise OtherErrorException(f"Chyba: Syntakticka chyba VAR, got: {e}")
        return token

    def checkToken(self, lexContext):
        self.scanner.setContext(lexContext)
        try:
            token = self.getToken()
        except ScannerException as e:
            raise OtherErrorException(f"Chyba: Syntakticka chyba VAR, got: {e}")
        return token

    def checkVar(self):
        self.scanner.setContext(LexerContext.VAR)
        try:
            token = self.getToken()
        except ScannerException as e:
            raise OtherErrorException(f"Chyba: Syntakticka chyba VAR, got: {e}")
        return token

    def checkSymb(self):
        self.scanner.setContext(LexerContext.CONST)
        try:
            token = self.getToken()
        except ScannerException as e:
            raise OtherErrorException(f"Chyba: Syntakticka chyba VAR, got: {e}")
        return token


    def checkLabel(self):
        self.scanner.setContext(LexerContext.LABEL)
        try:
            token = self.getToken()
        except ScannerException as e:
            raise OtherErrorException(f"Chyba: Syntakticka chyba VAR, got: {e}")
        return token


    def checkType(self):
        self.scanner.setContext(LexerContext.TYPE)
        try:
            token = self.getToken()
        except ScannerException as e:
            raise OtherErrorException(f"Chyba: Syntakticka chyba VAR, got: {e}")
        return token


    def getToken(self):
        return next(self.scannerIter, Token(TokenType.EOF))
 

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print("Chyba: Bylo zadano prilis mnoho argumentu!")
        sys.exit(10)

    if "--help" in sys.argv:
        print("""IPPCode24 Parser, Version 1.0, FIT VUT Brno, Autor: Jakub Jerabek (xjerab28)
- Prijima na standardni vstup zdrojovy kod v jazyku IPPCode24
- V pripade chyby ve zdrojovem kodu, ukoncuje program s odpovidajici hlaskou
a navratovym kodem, dle specifikace""")
        sys.exit()


parser = Parse(sys.stdin)
parser.execute()

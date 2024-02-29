from scanner import Scanner, TokenType, KeywordType, Token, LexerContext
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
import argparse
from exceptions import *

class Parse:
    def __init__(self, file):
        self.file = file
        self.scanner = Scanner(self.file)
        self.scannerIter = iter(self.scanner)
        self.counter = 1

    def initXML(self):
        self.root = ET.Element("program")
        self.root.set("language", "IPPcode24")
    
    def addTreeElement(self, opcode, *argv):
        instruction = ET.SubElement(self.root, "instruction", order=str(self.counter), opcode=f"{opcode.name}")
        self.counter +=1
        for i, arg in enumerate(argv):
            child = ET.SubElement(instruction, f"arg{i+1}", type=self.getArgType(arg))
            child.text = arg.value

    def getArgType(self, token):
        tokenTypeStr = token.tokenType.name
        return tokenTypeStr.lower()
    def parse(self):
        self.initXML()

        try:
            self.scanner.setContext(LexerContext.HEADER)
            header = self.getToken()
            while header.tokenType == TokenType.NEWLINE:
                header = self.getToken()
        except ScannerException:
            raise WrongHeaderException("Chybna hlavicka IPPCode")

        if header is None or header.tokenType != TokenType.HEADER:
            raise WrongHeaderException('Chybejici hlavicka')

        self.scanner.setContext(LexerContext.OPCODE)
        for token in self.scannerIter:
            tokenType = token.tokenType
            #print(token.tokenType)
            if tokenType == TokenType.NEWLINE:
                continue
            elif tokenType != TokenType.KEYWORD:
                raise OtherErrorException(f"Syntakticka chyba, ocekavan OPCode, dostal {tokenType}")

            self.processKeyword(token.value)

        self.generateXML()
    
    def generateXML(self):
        prettyTree = self.prettify(self.root)
        print(prettyTree)
        with open("output.xml", "w") as f:
            f.write(prettyTree)

    def prettify(self, element):
        """Vrátí formátovaný řetězec XML pro daný element ET."""
        rough_string = ET.tostring(element, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def processKeyword(self, keywordType):
        if keywordType in [KeywordType.MOVE, KeywordType.INT2CHAR, KeywordType.STRLEN, KeywordType.TYPE, KeywordType.NOT]:
            varToken = self.checkVar()
            symbToken = self.checkSymb()
            self.addTreeElement(keywordType, varToken, symbToken)
        elif keywordType in [KeywordType.CREATEFRAME, KeywordType.PUSHFRAME, KeywordType.POPFRAME, KeywordType.RETURN, KeywordType.BREAK]:
            self.checkNewLine()
            self.addTreeElement(keywordType)
        elif keywordType in [KeywordType.DEFVAR, KeywordType.POPS]:
            varToken = self.checkVar()
            self.addTreeElement(keywordType, varToken)
        elif keywordType in [KeywordType.CALL, KeywordType.LABEL, KeywordType.JUMP]:
            labelToken = self.checkLabel()
            self.addTreeElement(keywordType, labelToken)
        elif keywordType in [KeywordType.JUMPIFEQ, KeywordType.JUMPIFNEQ]:
            labelToken = self.checkLabel()
            symbToken1 = self.checkSymb()
            symbToken2 = self.checkSymb()
            self.addTreeElement(keywordType, labelToken, symbToken1, symbToken2)
        elif keywordType in [KeywordType.PUSHS, KeywordType.WRITE, KeywordType.EXIT, KeywordType.DPRINT]:
            symbToken = self.checkSymb()
            self.addTreeElement(keywordType, symbToken)
        elif keywordType in [KeywordType.ADD, KeywordType.SUB, KeywordType.MUL, KeywordType.IDIV, 
                            KeywordType.LT, KeywordType.GT, KeywordType.EQ, KeywordType.AND, 
                            KeywordType.OR, KeywordType.STRI2INT, KeywordType.CONCAT,
                            KeywordType.GETCHAR, KeywordType.SETCHAR]:
            varToken = self.checkVar()
            symbToken = self.checkSymb()
            symbToken2 = self.checkSymb()
            self.addTreeElement(keywordType, varToken, symbToken, symbToken2)
        elif keywordType == KeywordType.READ:
            varToken = self.checkVar()
            typeToken = self.checkType()
            self.addTreeElement(keywordType, varToken, typeToken)
        else:
            raise SyntaxErrorException(f"Chybny nebo chybejici OPCode {keywordType}")

        self.scanner.setContext(LexerContext.OPCODE)

    def checkNewLine(self):
        #self.scanner.setContext(LexerContext.NEWLINE)
        token = self.getToken()
        if token.tokenType != TokenType.NEWLINE and token.tokenType != TokenType.EOF:
            raise OtherErrorException(f"Chyba: Syntakticka chyba, ocekavan novy radek, ziskal {token.tokenType}")
        return token

    def checkVar(self):
        self.scanner.setContext(LexerContext.VAR)
        token = self.getToken()
        if token.tokenType != TokenType.VAR:
            raise OtherErrorException(f"Chyba: Syntakticka chyba VAR, got {token.tokenType}, {token.value}")
        return token

    def checkSymb(self):
        self.scanner.setContext(LexerContext.CONST)
        token = self.getToken()
        if token.tokenType not in [TokenType.VAR, TokenType.INT, TokenType.BOOL, TokenType.STRING, TokenType.NIL]:
            raise OtherErrorException(f"Chyba: Syntakticka chyba SYMB, got {token.tokenType}, {token.value}")
        return token

    def checkLabel(self):
        self.scanner.setContext(LexerContext.LABEL)
        token = self.getToken()
        if token.tokenType == TokenType.TYPE:
            token.tokenType = TokenType.LABEL

        if token.tokenType == TokenType.KEYWORD:
            pass

        if token.tokenType != TokenType.LABEL:
            raise OtherErrorException(f"Chyba: Syntakticka chyba LABEL, {token.tokenType}")
        return token

    def checkType(self):
        self.scanner.setContext(LexerContext.TYPE)
        token = self.getToken()
        if token.tokenType != TokenType.TYPE:
            raise OtherErrorException('Chyba: Syntakticka chyba TYPE')
        return token

    def getToken(self):
        return next(self.scannerIter, Token(TokenType.EOF))


parser = Parse(sys.stdin)
try:
    parser.parse()
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
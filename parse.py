from scanner import Scanner, TokenType, KeywordType, Token
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys
import argparse
from exceptions import *

class Parse:
    def __init__(self, file):
        self.file = file
        self.scanner = iter(Scanner(self.file))
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
            header = self.getToken()
            while header.tokenType == TokenType.NEWLINE:
                header = self.getToken()
        except ScannerException:
            raise WrongHeaderException("Chybna hlavicka IPPCode")

        if header is None or header.tokenType != TokenType.HEADER:
            raise WrongHeaderException('Chybejici hlavicka')

        for token in self.scanner:
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
            varToken = self.getToken()
            self.checkVar(varToken)
            symbToken = self.getToken()
            self.checkSymb(symbToken)
            self.addTreeElement(keywordType, varToken, symbToken)
        elif keywordType in [KeywordType.CREATEFRAME, KeywordType.PUSHFRAME, KeywordType.POPFRAME, KeywordType.RETURN, KeywordType.BREAK]:
            self.checkNewLine()
            self.addTreeElement(keywordType)
        elif keywordType in [KeywordType.DEFVAR, KeywordType.POPS]:
            varToken = self.getToken()
            self.checkVar(varToken)
            self.addTreeElement(keywordType, varToken)
        elif keywordType in [KeywordType.CALL, KeywordType.LABEL, KeywordType.JUMP]:
            labelToken = self.getToken()
            self.checkLabel(labelToken)
            self.addTreeElement(keywordType, labelToken)
        elif keywordType in [KeywordType.JUMPIFEQ, KeywordType.JUMPIFNEQ]:
            labelToken = self.getToken()
            self.checkLabel(labelToken)
            symbToken1 = self.getToken()
            self.checkSymb(symbToken1)
            symbToken2 = self.getToken()
            self.checkSymb(symbToken2)
            self.addTreeElement(keywordType, labelToken, symbToken1, symbToken2)
        elif keywordType in [KeywordType.PUSHS, KeywordType.WRITE, KeywordType.EXIT, KeywordType.DPRINT]:
            symbToken = self.getToken()
            self.checkSymb(symbToken)
            self.addTreeElement(keywordType, symbToken)
        elif keywordType in [KeywordType.ADD, KeywordType.SUB, KeywordType.MUL, KeywordType.IDIV, 
                            KeywordType.LT, KeywordType.GT, KeywordType.EQ, KeywordType.AND, 
                            KeywordType.OR, KeywordType.STRI2INT, KeywordType.CONCAT,
                            KeywordType.GETCHAR, KeywordType.SETCHAR]:
            varToken = self.getToken()
            self.checkVar(varToken)
            symbToken = self.getToken()
            self.checkSymb(symbToken)
            symbToken2 = self.getToken()
            self.checkSymb(symbToken2)
            self.addTreeElement(keywordType, varToken, symbToken, symbToken2)
        elif keywordType == KeywordType.READ:
            varToken = self.getToken()
            self.checkVar(varToken)
            typeToken = self.getToken()
            self.checkType(typeToken)
            self.addTreeElement(keywordType, varToken, typeToken)
            pass
        else:
            raise SyntaxErrorException(f"Chybny nebo chybejici OPCode {keywordType}")
    
    def checkNewLine(self):
        token = self.getToken()
        if token.tokenType != TokenType.NEWLINE and token.tokenType != TokenType.EOF:
            raise OtherErrorException(f"Chyba: Syntakticka chyba, ocekavan novy radek, ziskal {token.tokenType}")
    
    def checkVar(self, token):
        if token.tokenType != TokenType.VAR:
            raise OtherErrorException(f"Chyba: Syntakticka chyba VAR, got {token.tokenType}, {token.value}")

    def checkSymb(self, token):
        if token.tokenType not in [TokenType.VAR, TokenType.INT, TokenType.BOOL, TokenType.STRING, TokenType.NIL]:
            raise OtherErrorException(f"Chyba: Syntakticka chyba SYMB, got {token.tokenType}, {token.value}")

    def checkLabel(self, token):
        if token.tokenType == TokenType.TYPE:
            token.tokenType = TokenType.LABEL

        if token.tokenType == TokenType.KEYWORD:
            pass

        if token.tokenType != TokenType.LABEL:
            raise OtherErrorException(f"Chyba: Syntakticka chyba LABEL, {token.tokenType}")

    def checkType(self, token):
        if token.tokenType != TokenType.TYPE:
            raise OtherErrorException('Chyba: Syntakticka chyba TYPE')

    def getToken(self):
        return next(self.scanner, Token(TokenType.EOF))


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
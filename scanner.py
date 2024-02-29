import re
from enum import Enum, auto
import sys
from exceptions import ScannerException

class LexerContext(Enum):
    OPCODE = auto()
    CONST = auto()
    VAR = auto()
    TYPE = auto()
    #NEWLINE = auto()
    LABEL = auto()
    HEADER = auto()

class TokenType(Enum):
    VAR = 0
    KEYWORD = 1
    FRAME = 2
    INT = 3
    HEADER = 4
    NIL = 5
    NEWLINE = 6
    LABEL = 7
    BOOL = 8
    STRING = 9
    TYPE = 10
    EOF = 11

class KeywordType(Enum):
    MOVE = auto()
    CREATEFRAME = auto()
    PUSHFRAME = auto()
    POPFRAME = auto()
    DEFVAR = auto()
    CALL = auto()
    RETURN = auto()
    PUSHS = auto()
    POPS = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    IDIV = auto()
    LT = auto()
    GT = auto()
    EQ = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    INT2CHAR = auto()
    STRI2INT = auto()
    READ = auto()
    WRITE = auto()
    STRLEN = auto()
    CONCAT = auto()
    GETCHAR = auto()
    SETCHAR = auto()
    TYPE = auto()
    LABEL = auto()
    JUMP = auto()
    JUMPIFEQ = auto()
    JUMPIFNEQ = auto()
    EXIT = auto()
    DPRINT = auto()
    BREAK = auto()


class Token:
    def __init__(self, type, value = None):
        self.tokenType = type
        self.value = value

    def getType(self):
        return self.tokenType

    def getValue(self):
        return self.value


class Scanner:
    def __init__(self, file):
        self.file = file
        self.context = None
        # Definice regulárních výrazů pro různé typy tokenů
        self.wordRegex = [
            ("COMMENT", r'#.*'),
            ("WHITESPACE",  r'[ \t\v\f\r]+'),
            ("WORD", r'\S+'),
            ("NEWLINE", r'\n')
        ]

        self.headerRegex = r'(?i)\.IPPcode24'
        self.opcodeRegex = r'\b(?i)(MOVE|CREATEFRAME|PUSHFRAME|POPFRAME|DEFVAR|' \
                            r'CALL|RETURN|PUSHS|POPS|ADD|SUB|MUL|IDIV|LT|GT|' \
                            r'EQ|AND|OR|NOT|CONCAT|GETCHAR|SETCHAR|INT2CHAR|' \
                            r'STRI2INT|READ|WRITE|STRLEN|TYPE|LABEL|JUMP|' \
                            r'JUMPIFEQ|JUMPIFNEQ|EXIT|DPRINT|BREAK)\b'
        self.constRegex = [
            ("INT",         r'\b(int)@(-?(?:0x[0-9A-Fa-f]+|0o[0-7]+|0[0-7]*|[1-9][0-9]*|0))\b'),
            ("BOOL",        r'\b(bool)@(true|false)\b'),
            ("STRING",      r'\b(string)@(?:[^\s#\\]|\\[0-9]{3})*'),
            ("NIL",         r'nil@nil')
        ]

        self.varRegex = r'\b(LF|TF|GF)@[A-Za-z_$&%*!?-][A-Za-z0-9_$&%*!?-]*\b'
        self.typeRegex = r'\b(int|string|bool)\b'
        self.labelRegex = r'[A-Za-z_$&%*!?-][A-Za-z0-9_$&%*!?-]*\b'

        keywords = r'\b(?i)(MOVE|CREATEFRAME|PUSHFRAME|POPFRAME|DEFVAR|' \
                            r'CALL|RETURN|PUSHS|POPS|ADD|SUB|MUL|IDIV|LT|GT|' \
                            r'EQ|AND|OR|NOT|CONCAT|GETCHAR|SETCHAR|INT2CHAR|' \
                            r'STRI2INT|READ|WRITE|STRLEN|TYPE|LABEL|JUMP|' \
                            r'JUMPIFEQ|JUMPIFNEQ|EXIT|DPRINT|BREAK)\b'
        self.keywordRegex = re.compile(keywords)

        # Kompilace regulárních výrazů do patternů
        #self.tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specs)
        self.wordsRegex = '|'.join('(?P<%s>%s)' % pair for pair in self.wordRegex)
    # Funkce lexikálního analyzátoru
    def __iter__(self):
        
        for mo in re.finditer(self.wordsRegex, self.file.read()):
            kind = mo.lastgroup
            value = mo.group()
            print(f"{value} a {kind} a {self.context}")
            if kind == "COMMENT" or kind == "WHITESPACE":
                continue
            elif kind == "NEWLINE":
                yield Token(TokenType.NEWLINE)
                continue

            if self.context == LexerContext.HEADER:
                match = re.search(self.headerRegex, value)
                if match:
                    yield Token(TokenType.HEADER)
            elif self.context == LexerContext.CONST:
                match = re.match(self.varRegex, value)
                if match:
                    #print("NASEL")
                    yield Token(TokenType.VAR, value)
                    continue

                for dataType, regex in self.constRegex:
                    match = re.match(regex, value)
                    if match:
                        tokenType = getattr(TokenType, dataType, None)
                        yield Token(tokenType, value.split('@',1)[1])
                        break

            elif self.context == LexerContext.VAR:
                match = re.match(self.varRegex, value)
                if match:
                      yield Token(TokenType.VAR, value)
            elif self.context == LexerContext.LABEL:
                match = re.match(self.labelRegex, value)
                if match:
                    yield Token(TokenType.LABEL, value)
            #elif self.context == LexerContext.NEWLINE:
            #    yield Token(TokenType.NEWLINE)
            elif self.context == LexerContext.OPCODE:
                match = re.search(self.keywordRegex, value)
                if match:
                    keyword_type = getattr(KeywordType, match.group().upper(), None)  # Získání KeywordType hodnoty
                    if keyword_type is not None:
                        yield Token(TokenType.KEYWORD, keyword_type)
                    else:
                        raise ScannerException(f"Unknown keyword {match.group().upper()}")
            elif self.context == LexerContext.TYPE:
                match = re.match(self.typeRegex, value)
                if match:
                    yield Token(TokenType.TYPE, value)

            if match is None:
                raise ScannerException(f"Lexikalniii chyba {value}")

    def setContext(self, lexContext):
        self.context = lexContext

    def openFile(self):
        f = open(self.file, "r")
        return f.read()
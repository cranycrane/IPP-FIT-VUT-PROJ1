import re
from enum import Enum, auto
import sys
from exceptions import ScannerException

class LexerContext(Enum):
    OPCODE = auto()
    CONST = auto()
    VAR = auto()
    TYPE = auto()
    NEWLINE = auto()
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


class Scanner:
    def __init__(self, file):
        self.file = file
        self.context = None
        # Definice reg. vyrazu
        self.wordRegex = [
            ("COMMENT", r'(#.*)'),
            ("WORD", r'([^\s#]+)'),
            ("NEWLINE", r'\n+')
        ]

        self.headerRegex = r'^\.IPPcode24$'
        self.opcodeRegex = r'^(?i)(MOVE|CREATEFRAME|PUSHFRAME|POPFRAME|DEFVAR|' \
                            r'CALL|RETURN|PUSHS|POPS|ADD|SUB|MUL|IDIV|LT|GT|' \
                            r'EQ|AND|OR|NOT|CONCAT|GETCHAR|SETCHAR|INT2CHAR|' \
                            r'STRI2INT|READ|WRITE|STRLEN|TYPE|LABEL|JUMP|' \
                            r'JUMPIFEQ|JUMPIFNEQ|EXIT|DPRINT|BREAK)$'
        self.constRegex = [
            ("INT",         r'^(int)@(-?(?:0x[0-9A-Fa-f]+|0o[0-7]+|0[0-7]*|[1-9][0-9]*|0))$'),
            ("BOOL",        r'^(bool)@(true|false)$'),
            ("STRING",      r'^(string)@(?:[^\s#\\]|\\[0-9]{3})*$'),
            ("NIL",         r'^nil@nil$')
        ]

        self.varRegex = r'^(LF|TF|GF)@[A-Za-z_$&%*!?-][A-Za-z0-9_$&%*!?-]*$'
        self.typeRegex = r'^(int|string|bool)$'
        self.labelRegex = r'^[A-Za-z_$&%*!?-][A-Za-z0-9_$&%*!?-]*$'

        keywords = r'^(?i)(MOVE|CREATEFRAME|PUSHFRAME|POPFRAME|DEFVAR|' \
                            r'CALL|RETURN|PUSHS|POPS|ADD|SUB|MUL|IDIV|LT|GT|' \
                            r'EQ|AND|OR|NOT|CONCAT|GETCHAR|SETCHAR|INT2CHAR|' \
                            r'STRI2INT|READ|WRITE|STRLEN|TYPE|LABEL|JUMP|' \
                            r'JUMPIFEQ|JUMPIFNEQ|EXIT|DPRINT|BREAK)$'
        self.keywordRegex = re.compile(keywords)

        self.wordsRegex = '|'.join('(?P<%s>%s)' % pair for pair in self.wordRegex)

        file_content = self.file.read()

        self.file_content_without_comments = re.sub(r'#.*', '', file_content)

    def __iter__(self):
        
        for mo in re.finditer(self.wordsRegex, self.file_content_without_comments):
            kind = mo.lastgroup
            value = mo.group()

            if kind == "COMMENT" or kind == "WHITESPACE":
                continue
            if kind == "NEWLINE" and (self.context == LexerContext.OPCODE or self.context == LexerContext.HEADER):
                yield Token(TokenType.NEWLINE)
                continue
            
            if self.context == LexerContext.HEADER:
                match = re.match(self.headerRegex, value)
                if match:
                    yield Token(TokenType.HEADER)
            elif self.context == LexerContext.CONST:
                match = re.match(self.varRegex, value)
                if match:
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
        
        if self.context != LexerContext.OPCODE:
            raise ScannerException("Token nenalezen")

    def setContext(self, lexContext):
        self.context = lexContext

    def openFile(self):
        f = open(self.file, "r")
        return f.read()
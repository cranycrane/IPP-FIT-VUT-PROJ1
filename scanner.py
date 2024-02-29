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

    def getType(self):
        return self.tokenType

    def getValue(self):
        return self.value


class Scanner:
    def __init__(self, file):
        self.file = file
        self.context = None
        # Definice regulárních výrazů pro různé typy tokenů
        self.wordRegex = r'\S+';
        
        self.token_specs = [
            ("HEADER",      r'\.IPPcode24'),          # Hlavička kódu
            ("VAR",         r'\b(LF|TF|GF)@([A-Za-z_\-&%*!?][A-Za-z0-9_\-&%*!?]*)\b'),
            ("INT",         r'\b(int)@(-?(?:0x[0-9A-Fa-f]+|0o[0-7]+|0[0-7]*|[1-9][0-9]*|0))\b'),
            ("BOOL",        r'\b(bool)@(true|false)\b'),
            ("STRING",      r'\b(string)@(?:[^\s#\\]|\\[0-9]{3})*'),
            ("NIL",      r'\b(nil)@(nil)*\b'),
            ("TYPE",        r'\b(int|string|bool)\b'),
            ("LABEL",       r'\b([A-Za-z_\-&%*!?][A-Za-z0-9_\-&%*!?]*)\b'),
            #("CONSTANT",    r'\b(int|bool|string|nil)@[A-Za-z0-9_\-]*'),
            ("WHITESPACE",  r'[ \t\v\f\r]+'),  # Bílé znaky, ignorovány, kromě nového řádku
            ("NEWLINE",     r'\n'),            # Nový řádek
            ("COMMENT",     r'#.*'),                  # Komentáře
            ("UNKNOWN",     r'.+'),  # Neznámé tokeny
        ]

        keywords = r'\b(?i)(MOVE|CREATEFRAME|PUSHFRAME|POPFRAME|DEFVAR|' \
                            r'CALL|RETURN|PUSHS|POPS|ADD|SUB|MUL|IDIV|LT|GT|' \
                            r'EQ|AND|OR|NOT|CONCAT|GETCHAR|SETCHAR|INT2CHAR|' \
                            r'STRI2INT|READ|WRITE|STRLEN|TYPE|LABEL|JUMP|' \
                            r'JUMPIFEQ|JUMPIFNEQ|EXIT|DPRINT|BREAK)\b'
        self.keywordRegex = re.compile(keywords)

        # Kompilace regulárních výrazů do patternů
        self.tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specs)

    # Funkce lexikálního analyzátoru
    def __iter__(self):
        for mo in re.finditer(self.tok_regex, self.file.read()):
            kind = mo.lastgroup
            value = mo.group()

            if kind == "WHITESPACE" or kind == "COMMENT":
                continue  # Ignoruj bílé znaky a komentáře

            if self.context == LexerContext.HEADER:
                pass
            elif self.context == LexerContext.CONST:
                pass
            elif self.context == LexerContext.VAR:
                pass
            elif self.context == LexerContext.LABEL:
                pass
            elif self.context == LexerContext.NEWLINE:
                pass
            elif self.context == LexerContext.OPCODE:
                pass
            elif self.context == LexerContext.TYPE:
                pass
            
            elif kind == "NEWLINE":
                yield Token(TokenType.NEWLINE)  # Příklad, jak vytvořit token pro nový řádek
            elif kind == "HEADER":
                yield Token(TokenType.HEADER)
            elif kind == "VAR":
                yield Token(TokenType.VAR, value)
            elif kind == "INT":
                yield Token(TokenType.INT, value.split('@',1)[1])
            elif kind == "BOOL":
                yield Token(TokenType.BOOL, value.split('@',1)[1])
            elif kind == "STRING":
                yield Token(TokenType.STRING, value.split('@',1)[1])
            elif kind == "NIL":
                yield Token(TokenType.NIL, "nil")
            elif kind == "TYPE":
                yield Token(TokenType.TYPE, value)
            elif kind == "LABEL":
                keyword = re.search(self.keywordRegex, value)
                if keyword:
                    keyword_type = getattr(KeywordType, keyword.group().upper(), None)  # Získání KeywordType hodnoty
                    if keyword_type is not None:
                        yield Token(TokenType.KEYWORD, keyword_type)
                    else:
                        raise ScannerException(f"Unknown keyword {keyword.group().upper()}")
                else :
                    yield Token(TokenType.LABEL, value)
            elif kind == "UNKNOWN":
                raise ScannerException(f"Lexikalni chyba {value}")

    def openFile(self):
        f = open(self.file, "r")
        return f.read()

from enum import Enum 

class TokenType(Enum):
    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"

    EQUAL = "="
    NOT_EQUAL = "!="
    GT = ">"
    LT = "<"
    GE = ">="
    LE = "<="

    DESCENDANTS = "<<"
    ASCENDANTS = ">>"

    IDENTIFIER = "identifier"
    STRING = "string"
    NUMBER = "number"
    TERM = "term"

    TIME_EQUALS = "EQUALS"
    TIME_OVERLAPS = "OVERLAPS"
    TIME_WITHIN = "WITHIN"
    TIME_STARTS = "STARTS"
    TIME_FINISHES = "FINISHES"
    TIME_MEETS = "MEETS"
    TIME_BEFORE = "BEFORE"

    AND = "and"
    OR = "or"
    NOT = "not"

    EOF = "end_of_file"

keywords = {
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
    'equals': TokenType.TIME_EQUALS,
    'overlaps': TokenType.TIME_OVERLAPS,
    'within': TokenType.TIME_WITHIN,
    'starts': TokenType.TIME_STARTS,
    'finishes': TokenType.TIME_FINISHES,
    'meets': TokenType.TIME_MEETS,
    'before': TokenType.TIME_BEFORE
}
class OpType(Enum):
    Algebra = "algebra"
    Allen = "allen"

class Token(object):
    def __init__(self, type: TokenType, lexeme: str, literal, pointer: int ):
        self.type = type 
        self.lexeme = lexeme 
        self.literal = literal 
        self.pointer = pointer 

    def __str__(self):
        return f"({self.type} | {self.lexeme} | {self.literal} ({self.pointer}))"
    def __repr__(self):
        return f"({self.type} | {self.lexeme} | {self.literal} ({self.pointer}))"

class Tokenizer(object):
    def __init__(self):
        self.source = ''
        self.start = 0
        self.current = 0
        self.tokens = []

        self.operations = []
        self.parse_start = 0
        self.parse_current = 0

    def tokenize(self, source):
        self.source = source

        while not self.is_at_end():
            self.start = self.current
            self.scan(source)

        self.tokens.append(Token(TokenType.EOF, "", None, self.current))
        return self.tokens
        
    def is_at_end(self):
        return self.current >= len(self.source)
    
    def advance(self):
        l = self.source[self.current]
        self.current += 1
        return l 

    def match(self, c):
        if self.is_at_end():
            return False
        if self.source[self.current] != c :
            return False 
        
        self.current += 1
        return True 
    
    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]
    
    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def is_digit(self, c):
        return c >= '0' and c <= '9'

    def is_alpha(self, c):
        return ((c >= 'a') & (c <='z')) | ((c >='A') & (c <= 'Z')) | (c=='_')

    def is_alpha_numeric(self, c):
        return self.is_alpha(c) | self.is_digit(c)

    def identifier(self):
        while self.is_alpha_numeric(self.peek()) :
            self.advance()
        
        t = self.source[self.start: self.current]
        
        type = keywords.get(t.lower())
        if type == None:
            type = TokenType.IDENTIFIER
        self.add_token(type)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()
        self.add_token(TokenType.NUMBER, float(self.source[self.start: self.current]))


    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            self.advance()
        
        if self.is_at_end():
            return 
        
        self.advance()
        val = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, val.strip())

    def term(self):
        while self.peek() != '}' and not self.is_at_end():
            self.advance()

        if self.is_at_end():
            return 
        
        self.advance()
        val = self.source[self.start + 1 : self.current - 1]
        try:
            if val.split("|")[0].strip():
                self.add_token(TokenType.TERM, val.split("|")[0].strip())
        except:
            pass 

    def add_token(self, type: TokenType, literal = None):
        t = self.source[self.start: self.current]
        self.tokens.append(Token(type, t, literal, self.current))
    
    def scan(self, source):
        l = self.advance()
        match l :
            case TokenType.LEFT_PAREN.value:
                self.add_token(TokenType.LEFT_PAREN)
            case TokenType.RIGHT_PAREN.value:
                self.add_token(TokenType.RIGHT_PAREN)
            case TokenType.LEFT_BRACE.value:
                self.term()  
            case TokenType.LT.value:
                if self.match(TokenType.EQUAL.value):
                    self.add_token(TokenType.LE) 
                elif self.match(TokenType.LT.value):
                    self.add_token(TokenType.DESCENDANTS)
                else:
                    self.add_token(TokenType.LT)
            case TokenType.GT.value:
                if self.match(TokenType.EQUAL.value):
                    self.add_token(TokenType.GE) 
                elif self.match(TokenType.GT.value):
                    self.add_token(TokenType.ASCENDANTS)
                else:
                    self.add_token(TokenType.GT)
            case TokenType.EQUAL.value:
                self.add_token(TokenType.EQUAL if self.match(TokenType.EQUAL.value) else TokenType.EQUAL)
            case "!":
                self.add_token(TokenType.NOT_EQUAL if self.match(TokenType.EQUAL.value) else TokenType.NOT)
            case ' ':
                pass 
            case '\r':
                pass 
            case '\t':
                pass 
            case '\n':
                pass 
            case '"':
                self.string()
            case _ :
                if self.is_digit(l):
                    self.number()
                if self.is_alpha(l):
                    self.identifier()

    def is_parse_end(self):
        return self.parse_current >= len(self.tokens)

    def parse_advance(self):
        l = self.tokens[self.parse_current].type
        self.parse_current += 1
        return l 
    def parse_peek(self):
        if self.is_parse_end():
            return '\0'
        return self.tokens[self.parse_current].type 

    def add_operation(self, operation, term1=None, term2=None):
        self.operations.append((operation, term1, term2))

    def operate_next(self, operator):
        self.operations.append((operator,))

    def operation(self):
        while self.parse_peek() != TokenType.RIGHT_PAREN and not self.is_parse_end():
            self.parse_advance()
    
        if self.is_parse_end():
            return 
        
        self.parse_advance()
        val = self.tokens[self.parse_start + 1 : self.parse_current - 1]
        # print('val', val)
        if len(val) == 1:
            self.add_operation(val[0].type, val[0].literal)
        if len(val) == 2:
            self.add_operation(val[0].type, val[1].literal)
        if len(val) == 3:
            self.add_operation(val[1].type, val[0].literal, val[2].literal)


    def parse_scan(self):
        l = self.parse_advance()
        match l:
            case TokenType.LEFT_PAREN:
                self.operation()
            case TokenType.AND:
                self.operate_next(TokenType.AND) 
            case TokenType.OR:
                self.operate_next(TokenType.OR) 
            case TokenType.NOT:
                self.operate_next(TokenType.NOT) 
            case _:
                pass 

    def parse(self):
        while not self.is_parse_end():
            self.parse_start = self.parse_current
            self.parse_scan()

        self.operations.append((TokenType.EOF,))
        return self.operations





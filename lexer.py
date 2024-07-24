import sys
from enum import Enum, auto


class TokenKind(Enum):
    tok_eof = auto()
    tok_def = auto()
    tok_extern = auto()
    tok_if = auto()
    tok_else = auto()
    tok_then = auto()
    tok_var = auto()
    tok_identifier = auto()
    tok_number = auto()
    tok_op_arithmetric = auto()
    tok_open_paren = auto()
    tok_close_paren = auto()
    tok_open_angle = auto()
    tok_close_angle = auto()
    tok_open_brace = auto()
    tok_close_brace = auto()
    tok_open_array = auto()
    tok_close_array = auto()
    tok_comma = auto()
    tok_endline = auto()
    tok_assign = auto()
    tok_return = auto()

    def __str__(self):
        return self.name


class Token:
    def __init__(self, tokenkind: TokenKind, value = None, linenumber = 0):
        self.type = tokenkind
        self.value = value
        self.linenumber = linenumber

    def __str__(self):
        if self.type == TokenKind.tok_identifier or self.type == TokenKind.tok_number:
            return str(self.type) + ' : ' + str(self.value) + " : " + str(self.linenumber)
        else:
            return str(self.type) +  " : None : " + str(self.linenumber)

def tokenize(text):
    tokens = []
    i = 0
    current_line = 0
    while i < len(text):
        if text[i].isalpha():
            j = i
            while j < len(text) and (text[j].isalnum() or  text[j] == "_") :
                j += 1
            if text[i:j] == 'def':
                tokens.append(Token(TokenKind.tok_def, text[i:j], current_line))
            elif text[i:j] == 'var':
                tokens.append(Token(TokenKind.tok_var, text[i:j], current_line))
            elif text[i:j] == 'extern':
                tokens.append(Token(TokenKind.tok_extern, text[i:j], current_line))
            elif text[i:j] == 'if':
                tokens.append(Token(TokenKind.tok_if, text[i:j], current_line))
            elif text[i:j] == 'else':
                tokens.append(Token(TokenKind.tok_else, text[i:j], current_line))
            elif text[i:j] == 'then':
                tokens.append(Token(TokenKind.tok_then, text[i:j], current_line))
            elif text[i:j] == 'return':
                tokens.append(Token(TokenKind.tok_return, text[i:j], current_line))
            else :
                tokens.append(Token(TokenKind.tok_identifier, text[i:j], current_line))
            i = j
        elif text[i].isdigit():
            j = i
            while j < len(text) and text[j].isdigit():
                j += 1
            tokens.append(Token(TokenKind.tok_number, text[i:j], current_line))
            i = j
        elif text[i] == '(':
            tokens.append(Token(TokenKind.tok_open_paren, None, current_line))
            i += 1
        elif text[i] == ')':
            tokens.append(Token(TokenKind.tok_close_paren, None, current_line))
            i += 1
        elif text[i] == '{':
            tokens.append(Token(TokenKind.tok_open_brace, None, current_line))
            i += 1
        elif text[i] == '}':
            tokens.append(Token(TokenKind.tok_close_brace, None, current_line))
            i += 1
        elif text[i] == '[':
            tokens.append(Token(TokenKind.tok_open_array, None, current_line))
            i += 1
        elif text[i] == ']':
            tokens.append(Token(TokenKind.tok_close_array, None, current_line))
            i += 1
        elif text[i] == '<':
            tokens.append(Token(TokenKind.tok_open_angle, None, current_line))
            i += 1
        elif text[i] == '>':
            tokens.append(Token(TokenKind.tok_close_angle, None, current_line))
            i += 1
        elif text[i] == '=':
            tokens.append(Token(TokenKind.tok_assign, None, current_line))
            i += 1
        elif text[i] == ',':
            tokens.append(Token(TokenKind.tok_comma, None, current_line))
            i += 1
        elif text[i] == ';':
            tokens.append(Token(TokenKind.tok_endline, None, current_line))
            i += 1
        elif text[i] in ['+', '-', '*', '/']:
            tokens.append(Token(TokenKind.tok_op_arithmetric, text[i], current_line))
            i += 1
        elif text[i] in ['<', '>', '=', '!']:
            if i + 1 < len(text) and text[i + 1] == '=':
                tokens.append(Token(TokenKind.tok_op_boolean, text[i:i+2], current_line))
                i += 2
            else:
                tokens.append(Token(TokenKind.tok_op_boolean, text[i], current_line))
                i += 1
        else:
            if text[i] == '#':
                i += 1
                while i < len(text) and not text[i] in ['\n', '\r', '\r\n']:
                    i += 1
            elif text[i] in ['\n', '\r', '\r\n']:
                i += 1
                current_line += 1
            elif text[i].isspace():
                i += 1
            else:
                print(text[i])
                i += 1
    tokens.append(Token(TokenKind.tok_eof, None, current_line))
    return tokens
    

if __name__ == '__main__':
    text = open(sys.argv[1], 'r').read()
    print(text)
    tokens = tokenize(text)
    print(tokens)
    for token in tokens:
        print(token)

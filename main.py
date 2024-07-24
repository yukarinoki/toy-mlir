import sys
from lexer import tokenize
from parser import parse

if __name__ == '__main__':
    text = open(sys.argv[1], 'r').read()
    print(text)
    tokens = tokenize(text)
    print(tokens)
    for token in tokens:
        print(token)

    ast = parse(tokens)
    for stmt in ast:
        print(stmt)
    

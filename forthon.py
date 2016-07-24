#!/usr/bin/env python3
"""."""
from sys import stdin
from re import sub

COMMENT_RE = r'\(.*\)\s'


def tokenize(raw):
    return sub(COMMENT_RE, '', raw).split()


class Reader():
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def peek(self):
        try:
            return self.tokens[self.position]
        except IndexError:
            return None

    def next(self):
        token = self.peek()
        self.position += 1
        return token

    def match(self, token):
        next = self.next()
        assert next == token, "Expected {} to match {}".format(next, token)
        return next

    def read_until(self, until):
        body = []
        while self.peek() != until:
            body.append(self.next())
        body.append(self.match(until))
        return body

    def read_word(self):
        """Read a Forth word."""
        name = self.next()
        body = self.read_until(';')[:-1]
        return name, body


def make_env():
    """."""
    return {'1+': ['1', '+'], 'do': ['0', '?do']}


def interpret(reader, stack, env, returnstack=None):
    """Interpret a Forth token stream."""
    returnstack = returnstack or []

    while True:
        token = reader.peek()
        if token is None:
            break
        elif token == ':':
            reader.match(':')
            name, body = reader.read_word()
            env[name] = body
        elif token.isdigit():
            reader.match(token)
            stack.append(int(token))
        elif token == 'swap':
            reader.match(token)
            stack[-1], stack[-2] = stack[-2], stack[-1]
        elif token == 'dup':
            reader.match(token)
            stack.append(stack[-1])
        elif token == 'rot':
            reader.match(token)
            stack.append(stack.pop(-3))
        elif token == 'over':
            reader.match(token)
            stack.append(stack[-2])
        elif token == 'drop':
            reader.match(token)
            stack.pop()
        elif token == '+':
            reader.match(token)
            stack.append(stack.pop() + stack.pop())
        elif token == '*':
            reader.match(token)
            stack.append(stack.pop() * stack.pop())
        elif token == 'i':
            reader.match(token)
            stack.append(returnstack[-1][1][0])
        elif token == 'loop':
            reader.match(token)
            returnstack[-1][1][0] += 1
            if returnstack[-1][1][0] < returnstack[-1][1][1]:
                reader.position = 0
            else:
                returnstack.pop()
                break
        elif token == '?do':
            reader.match(token)
            loop = reader.read_until('loop')
            start, end = stack.pop(), stack.pop()
            tos = ['do?', [start, end]]
            returnstack.append(tos)
            interpret(Reader(loop),
                      stack=stack,
                      env=env,
                      returnstack=returnstack)
        elif token == '.':
            print(stack.pop())
            reader.match(token)
        elif token in env:
            reader.match(token)
            interpret(Reader(env[token]), stack=stack, env=env,
                      returnstack=returnstack)
        else:
            raise SyntaxError("Unknown token {}".format(token))


if __name__ == "__main__":
    stack = []
    env = make_env()
    if stdin.isatty():
        try:
            while True:
                try:
                    raw = input('> ')
                    tokens = Reader(tokenize(raw))
                    interpret(tokens, stack=stack, env=env)
                except IndexError as e:
                    print(e)
                except KeyboardInterrupt as e:
                    print(e.__class__.__name__)
        except EOFError:
            pass
    else:
        tokens = tokenize(stdin.read())
        interpret(Reader(tokens), stack=stack, env=env)

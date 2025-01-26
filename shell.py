from main import Lexer, Parser, Interpreter

# while True:
with open('main.nat','r') as f:
    code = f.read()
# code = input('>>> ')
# if code == 'exit':
# 	break
lexer = Lexer(code)
parser = Parser(lexer.tokenize())
# print(f"Lexer: {lexer.tokenize()}")
# print(f"Parser: {parser.parse()}")
interpret= Interpreter(parser.parse())
interpret.interpret()
# except Exception as e:
#     print(e)

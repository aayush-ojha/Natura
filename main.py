from tokens import Integer, Float, String, Word, Operator, BuiltInFunction, Variable, Identifier, BoolOp, CompOp
variables = []
default_types = (int, float, str, list, tuple, dict, set, bool)
custom_classes = ['INT','FLT','STR','WRD','OPT','BIF','VAR','BOP','COP','IDT']


class Lexer:
    operators = '+-*/^()'
    reserved = ['if', 'else', 'while']
    builtin_func = ['show', 'listen']
    bool_operators = ['and', 'or', 'not']
    comp_operators = ['is?', '<', '>', '<=', '>=', '==']
    assignments = ['is']

    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.tokens = []
        self.end = False
        self.parans = 0
        if len(code) > 0:
            self.char = self.code[self.pos]
        else:
            self.char = ''
            self.end = True
        

    def tokenize(self):
        while not self.end:
            if self.char.isspace():
                self.move()
                continue
            token = self.evaluate()
            if isinstance(token, list):
                self.tokens.append(token[0])
                if token[1]:
                    second_tokens = Lexer(token[1]).tokenize()
                    self.tokens.extend(second_tokens)
                self.tokens.append(Operator('('))
                third_tokens = Lexer(token[2]).tokenize()
                self.tokens.extend(third_tokens)
                self.tokens.append(Operator(')'))
            elif token:
                self.tokens.append(token)
        return self.tokens

    def evaluate(self):
        if self.char.isspace():
            self.move()
        elif self.char.isdigit():
            return self.get_num()
        elif self.char.isalpha():
            word = self.get_word()
            if word in Lexer.builtin_func:
                return BuiltInFunction(word)
            elif word in Lexer.reserved:
                if word == 'else':
                    snippet = self.get_else_snippet()
                    return [Word(word), '', snippet]
                condition, snippet = self.get_condition()
                return [Word(word), condition, snippet]
            elif word in Lexer.bool_operators:
                return BoolOp(word)
            elif word == 'is?':
                return CompOp('is?')
            elif word == 'is':
                return Word('is')
            else:
                return Variable(word)
        elif self.char == '"':
            return(self.get_string())
        elif self.char in ['<', '>']:
            op = self.get_comp_op()
            return CompOp(op)
        elif self.char in Lexer.operators:
            char = self.char
            self.move()
            return Operator(char)
        else:
            raise Exception(f"Error: Invalid character '{self.char}'")

    def get_num(self):
        num = ''
        is_float = False
        while not self.end and (self.char.isdigit() or self.char == '.'):
            if self.char == '.':
                if is_float:
                    raise Exception("Error: Invalid number format")
                is_float = True
            num += self.char
            self.move()
        return Integer(num) if not is_float else Float(num)

    def get_word(self):
        word = ''
        while not self.end and (self.char.isalpha() or self.char == '?'):
            word += self.char
            self.move()
        return word

    def get_comp_op(self):
        op = self.char
        self.move()
        if not self.end and self.char == '=':
            op += self.char
            self.move()
        return op

    def get_string(self):
        self.move()
        string = ""
        while self.char != '"':
            string += self.char
            self.move()
        self.move()
        self.tokens.append(String(string))
        
    def get_condition(self):
        self.move()
        condition = ""
        
        while not self.end and self.char != '(':
            condition += self.char
            self.move()
            
        if self.char == '(':
            self.move()
            snippet = ""
            paren_count = 1
            
            while paren_count > 0:
                if self.end:
                    newline = input('... ')
                    self.code += '\n' + newline
                    self.pos = len(self.code) - len(newline)
                    self.char = self.code[self.pos]
                    self.end = False
                    continue
                    
                if self.char == '(':
                    paren_count += 1
                elif self.char == ')':
                    paren_count -= 1
                
                if paren_count > 0:
                    snippet += self.char
                self.move()
                
            return condition.strip(), snippet.strip()
            
        raise Exception("Expected '(' after condition")
    
    def get_else_snippet(self):
        while self.char.isspace():
            self.move()
            
        snippet = ""
        if not self.end and self.char == '(':
            self.move()
            paren_count = 1
            
            while paren_count > 0:
                if self.end:
                    newline = input('... ')
                    self.code += '\n' + newline
                    self.pos = len(self.code) - len(newline)
                    self.char = self.code[self.pos]
                    self.end = False
                    continue
                    
                if self.char == '(':
                    paren_count += 1
                elif self.char == ')':
                    paren_count -= 1
                
                if paren_count > 0:
                    snippet += self.char
                self.move()
                
            return snippet.strip()
            
        raise Exception("Expected '(' after else")

    def move(self):
        self.pos += 1
        if self.pos < len(self.code):
            self.char = self.code[self.pos]
        else:
            self.end = True
         

            
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.tok = self.tokens[self.pos] if tokens else None
        self.statements = []

    def parse(self):
        while self.pos < len(self.tokens):
            stmt = self.statement()
            if stmt:
                self.statements.append(stmt)
        return self.statements

    def statement(self):
        if isinstance(self.tok, Word) and self.tok.value in ['if', 'while']:
            return self.if_while_statement()
        elif self.tok.type == 'BIF':
            if self.tok.value == 'show':
                return self.show_statement()
            elif self.tok.value == 'listen':
                return self.listen_statement()
        elif isinstance(self.tok, Variable):
            return self.assignment()
        return self.comp_expression()

    def if_while_statement(self):
        op = self.tok
        self.move()
        
        condition = self.comp_expression()
        
        # if not self.tok or self.tok.value != '(':
        #     raise Exception(f"Expected '(' after {op.value} condition")
        self.move()
        
        if_statements = []
        else_statements = []
        current_list = if_statements
        
        while self.tok and self.tok.value != ')':
            if isinstance(self.tok, Variable):
                var = self.tok
                self.move()
                if self.tok and self.tok.value == 'is':
                    self.move()
                    value = self.expression()
                    current_list.append([Word('assign'), var, value])
            elif isinstance(self.tok, BuiltInFunction):
                if self.tok.value == 'show':
                    self.move()
                    expr = self.expression()
                    current_list.append([BuiltInFunction('show'), expr])
                    
            else:
                stmt = self.statement()
                if stmt:
                    current_list.append(stmt)
        # print(self.tok)
        # self.move()     
        # if not self.tok or self.tok.value != ')':
        #     raise Exception(f"Expected ')' after {op.value} action")
        # print(self.tok)
        # while self.tok == None:
        #     self.move()
        self.move()
        if self.tok and self.tok.value == 'else':
            self.move() 
            if not self.tok or self.tok.value != '(':
                raise Exception("Expected '(' after else")
            self.move()  
            
            current_list = else_statements
            while self.tok and self.tok.value != ')':
                stmt = self.statement()
                if stmt:
                    current_list.append(stmt)
                    
            if not self.tok or self.tok.value != ')':
                raise Exception("Expected ')' after else block")
            self.move()
            
        return [op, condition, [if_statements, else_statements] if else_statements else [if_statements]]
    
    def bool_expression(self):
        left = self.expression()
        while self.tok and self.tok.value in ['and', 'or', 'not']:
            op = self.tok
            self.move()
            left = [left, op, self.expression()]
        return left
    
    def comp_expression(self):
        left = self.bool_expression()
        while isinstance(self.tok, CompOp):
            op = self.tok
            self.move()
            left = [left, op, self.bool_expression()]
        return left

    def expression(self):
        if isinstance(self.tok, (Variable, Identifier)): 
            token = self.tok
            self.move()
            if self.tok and self.tok.value in ['+', '-', '*', '/', '^']:
                op = self.tok
                self.move()
                right = self.comp_expression()
                return [token, op, right]
            return token
        left = self.term()
        while self.tok and self.tok.value in ['+', '-']:
            op = self.tok
            self.move()
            left = [left, op, self.term()]
        return left
    
    def term(self):
        left = self.factor()
        while self.tok and self.tok.value in ['*', '/', '^']:
            op = self.tok
            self.move()
            left = [left, op, self.factor()]
        return left
        
    
    def factor(self):
        token = self.tok
        if self.tok.type in ["INT", "FLT", 'STR']:
            self.move()
            return token
        elif self.tok.value == '(':
            self.move()
            expr = self.comp_expression()
            self.move()
            return expr
        else:
            self.move()
    
    def show_statement(self):
        self.move()  
        expression = self.comp_expression()
        return [BuiltInFunction('show'), expression]
    
    def listen_statement(self):
        self.move()  
        variable = self.tok
        self.move()  
        return [BuiltInFunction('listen'), variable]
    
    def assignment(self):
        variable = self.tok
        self.move()
        if not self.tok or self.tok.value != 'is':
            raise Exception('Expected is')
        self.move()
        expression = self.comp_expression()
        return [Word('assign'), variable, expression]
        
    def move(self):
        self.pos += 1
    
        if self.pos < len(self.tokens):
            self.tok = self.tokens[self.pos]
        else:
            self.tok = None
    
    
    
    
class Interpreter:
    def __init__(self, tree):
        self.tree = tree
        
    def interpret(self, tree = None):
        if not tree:
            tree = self.tree
        result = None
        if isinstance(tree, list):
            for node in tree:
                result = self.evaluate(node)
        return result
            
    def evaluate(self, node):
        if isinstance(node, Integer) or isinstance(node, Float) or isinstance(node, String):
            return node
        elif isinstance(node, (Variable, Identifier)):
            return globals().get(node.value, 0) 
        elif isinstance(node, list):

            if isinstance(node[0], BuiltInFunction):
                if node[0].value == 'show':
                    value = self.evaluate(node[1])
                    print(value)
                    return value
                
                if node[0].value == 'listen':
                    value = input()
                    if value.isdigit():
                        value_token = Integer(value)
                    elif '.' in value and all(part.isdigit() for part in value.split('.')):
                        value_token = Float(value)
                    else:
                        value_token = String(value)
                    return self.evaluate([Word('assign'), node[1], value_token])

            elif isinstance(node[0], Word):
                if node[0].value == 'assign':
                    value = self.evaluate(node[2])
                    variables.append(Variable(node[1].value))
                    globals()[node[1].value] = value
                    return value
                
                elif node[0].value == 'if':
                    condition = self.compute_condition(node[1])
                    statements = node[2]
                    
                    if condition:
                        return self.interpret(statements[0])  
                    elif len(statements) > 1:
                        return self.interpret(statements[1])  
                
                elif node[0].value == 'while':
                    while self.compute_condition(node[1]):
                        self.interpret(node[2][0]) 
            
            
            elif len(node) == 3:
                left = self.evaluate(node[0])
                op = node[1]
                right = self.evaluate(node[2])
                return self.compute(left, op, right)         
            
            
     
    def compute(self,left,op,right):
        if isinstance(left, (Integer, Float)):
            left = int(left.value) if isinstance(left, Integer) else float(left.value)
        
        if isinstance(right, (Integer, Float)):
            right = int(right.value) if isinstance(right, Integer) else float(right.value)
        
        if op.value == '+':
            return left + right
        elif op.value == '-':
            return left - right
        elif op.value == '*':
            return left * right
        elif op.value == '/':
            return left / right
        elif op.value == '^':
            return left ** right
        elif op.value == ">":
            return 1 if left > right else 0
        elif op.value == ">=":
            return 1 if left >= right else 0
        elif op.value == "<":
            return 1 if left < right else 0
        elif op.value == "<=":
            return 1 if left <= right else 0
        elif op.value == "is?":
            return 1 if left == right else 0
        elif op.value == "and":
            return 1 if left and right else 0
        elif op.value == "or":
            return 1 if left or right else 0
        
    def compute_condition(self, condition):
        if not isinstance(condition, list):
            return bool(self.evaluate(condition))
            
        left = self.evaluate(condition[0])
        op = condition[1].value
        right = self.evaluate(condition[2])
        
        if isinstance(left, (Integer, Float)):
            left = int(left.value) if isinstance(left, Integer) else float(left.value)
        if isinstance(right, (Integer, Float)):
            right = int(right.value) if isinstance(right, Integer) else float(right.value)
        if op == '>': return bool(left > right)
        elif op == '<': return bool(left < right)
        elif op == '>=': return bool(left >= right)
        elif op == '<=': return bool(left <= right)
        elif op == '==': return bool(left == right)
        elif op == 'is?': return bool(left == right)
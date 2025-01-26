class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return self.value
    
class Float(Token):
    def __init__(self, value):
        super().__init__('FLT', value)
 
class Integer(Token):
    def __init__(self, value):
        super().__init__('INT', value)
               
class String(Token):
    def __init__(self, value):
        super().__init__('STR', value)
               
class Word(Token):
    def __init__(self, value):
        super().__init__('WRD', value)

class Operator(Token):
    def __init__(self, value):
        super().__init__('OPT', value)

class BuiltInFunction(Token):
    def __init__(self, value):
        super().__init__('BIF', value)
        
class Variable(Token):
    def __init__(self, value):
        super().__init__('VAR', value)
        
class BoolOp(Token):
    def __init__(self, value):
        super().__init__('BOP', value)

class CompOp(Token):
    def __init__(self, value):
        super().__init__('COP', value)
        
class Identifier(Token):
    def __init__(self, value):
        super().__init__('IDT', value)
        

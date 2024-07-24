from lexer import TokenKind
import time
import traceback
CurTok = 0

class ExprAST:
    def __repr__(self, indent=0):
        return ' ' * indent + self.__class__.__name__

class NumberExprAst(ExprAST):
    def __init__(self, val):
        self.val = val
    def __repr__(self, indent=0):
        return f"Number({self.val})"

class VariableExprAST(ExprAST):
    def __init__(self, name):
        self.name = name
    def __repr__(self, indent=0):
        return f"Variable({self.name})"


class BinaryExprAst(ExprAST):
    def __init__(self, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
    def __repr__(self, indent=0):
        return (f'{" " * indent}Binary({self.op})\n'
                f'{self.lhs.__repr__(indent + 2)}\n'
                f'{self.rhs.__repr__(indent + 2)}')

class IfExprAST(ExprAST):
    def __init__(self, cond, then, elsee):
        self.cond = cond
        self.then = then
        self.elsee = elsee
    def __repr__(self, indent=0):
        return f"If(cond: {self.cond}, then: {self.then}, else: {self.elsee})"

class CallExprAST(ExprAST):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args
    def __repr__(self, indent=0):
        return f"{' ' * indent}Call({self.callee}, args: {', '.join(map(str, self.args))})"

class PrototypeAST:
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self, indent=0):
        return f"{' ' * indent}Prototype({self.name}, args: {', '.join(self.args)})"

class FunctionAST:
    def __init__(self, proto, body):
        self.proto = proto
        self.body = body
    def __repr__(self, indent=0):
        return (f"{' ' * indent}Function (\n"
                f"{' ' * (indent + 2)}prototype: {self.proto}\n"
                f"{' ' * (indent + 2)}body: {self.body}\n"
                f"{' ' * indent})")

class ReturnAST(ExprAST):
    def __init__(self, expr):
        self.expr = expr
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self, indent=0):
        return f"{' ' * indent}Return({self.expr.__repr__(indent + 2)})"

class AssignAST(ExprAST):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self, indent=0):
        return (f"{' ' * indent}Assign(\n"
                f"{' ' * (indent + 2)}name: {self.name},\n"
                f"{' ' * (indent + 2)}expr: {self.expr.__repr__(indent + 2)}\n"
                f"{' ' * indent})")

class VarDefinitionAST(ExprAST):
    def __init__(self, name, expr=None, dims=None):
        self.name = name
        self.expr = expr
        self.dims = dims
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self, indent=0):
        expr_repr = "None" if self.expr is None else self.expr.__repr__(indent + 2)
        dims_repr = "None" if self.dims is None else repr(self.dims)
        return (f"{' ' * indent}VarDef(\n"
                f"{' ' * (indent + 2)}name: {self.name},\n"
                f"{' ' * (indent + 2)}expr: {expr_repr},\n"
                f"{' ' * (indent + 2)}dims: {dims_repr}\n"
                f"{' ' * indent})")

class TensorLiteralAST(ExprAST):
    def __init__(self, vals, dims):
        self.vals = vals
        self.dims = dims
    
    def __str__(self):
        return self.__repr__()
    
    def __repr__(self, indent=0):
        vals_repr = self._format_vals(self.vals, indent + 2)
        return (f"{' ' * indent}TensorLiteral(\n"
                f"{' ' * (indent + 2)}values: {vals_repr},\n"
                f"{' ' * (indent + 2)}dims: {self.dims}\n"
                f"{' ' * indent})")
    
    def _format_vals(self, vals, indent):
        if isinstance(vals, list):
            formatted = [self._format_vals(v, indent + 2) for v in vals]
            return ("[\n" + 
                    ",\n".join(f"{' ' * (indent + 2)}{v}" for v in formatted) +
                    f"\n{' ' * indent}]")
        else:
            return str(vals)

def NextToken(tokens):
    global CurTok
    CurTok += 1
    stack = traceback.extract_stack()
    filename, line, function_name, _ = stack[-2]
    print(f"NextToken {tokens[CurTok]} at {filename}, line {line} in {function_name}")
    return CurTok

def ParseTensorLiteralImpl(tokens):
    vals = []
    if tokens[CurTok].type != TokenKind.tok_open_array:
        raise Exception(f"Unexpected token at ParseTensorLiteral {tokens[CurTok]}")
    NextToken(tokens)

    if tokens[CurTok].type != TokenKind.tok_open_array:
        while True:
            if tokens[CurTok].type == TokenKind.tok_number:
                vals.append(tokens[CurTok].value)
            NextToken(tokens)
            if tokens[CurTok].type == TokenKind.tok_comma:
                NextToken(tokens)
                continue
            if tokens[CurTok].type != TokenKind.tok_close_array:
                raise Exception(f"Unexpected token at ParseTensorLiteral {tokens[CurTok]}")
            else :
                NextToken(tokens)
                break
        dims = [len(vals)]
    else:
        dim = 0
        dims_list = []
        while True:
            if tokens[CurTok].type == TokenKind.tok_open_array:
                vals_tmp, dims_tmp = ParseTensorLiteralImpl(tokens)
                vals.extend(vals_tmp)
                dims_list.append(dims_tmp)
                dim += 1
            if tokens[CurTok].type == TokenKind.tok_comma:
                NextToken(tokens)
                continue
            if tokens[CurTok].type != TokenKind.tok_close_array:
                raise Exception(f"Unexpected token at ParseTensorLiteral {tokens[CurTok]}")
            else :
                NextToken(tokens)
                break
        if len(set(tuple(dim) for dim in dims_list)) != 1:
            raise Exception(f"Invalid tensor literal at ParseTensorLiteral not matching Dimmension {tokens[CurTok]}")
        dims = [dim] + dims_list[0]

    return vals, dims
    
def ParseTensorLiteral(tokens):
    global CurTok
    vals, dims = ParseTensorLiteralImpl(tokens)
    return TensorLiteralAST(vals, dims)

def ParsePrimary(tokens):
    global CurTok
    print(f"ParsePrimary: {tokens[CurTok]}")
    if tokens[CurTok].type == TokenKind.tok_open_array:
        return ParseTensorLiteral(tokens)
    if tokens[CurTok].type == TokenKind.tok_identifier and tokens[CurTok + 1].type == TokenKind.tok_open_paren:
        return ParseCallExpr(tokens)
    elif tokens[CurTok].type == TokenKind.tok_identifier:
        name = tokens[CurTok].value
        NextToken(tokens)
        return VariableExprAST(name)
    else:
        raise Exception(f"Unexpected token at ParsePrimary {tokens[CurTok]}")
    
def ParseCallExpr(tokens):
    global CurTok
    callee = tokens[CurTok].value
    NextToken(tokens)
    if tokens[CurTok].type != TokenKind.tok_open_paren:
        raise Exception(f"Unexpected token at ParseCallExpr {tokens[CurTok]}")
    NextToken(tokens)
    args = []
    while True:
        if tokens[CurTok].type != TokenKind.tok_close_paren:
            args.append(ParseExpression(tokens))
            if tokens[CurTok].type == TokenKind.tok_comma:
                NextToken(tokens)
                continue
        else:
            NextToken(tokens)
            break
    return CallExprAST(callee, args)

def ParseExpression(tokens):
    global CurTok
    lhs = ParsePrimary(tokens)
    if not lhs:
        raise Exception(f"Unexpected token at ParseExpression {tokens[CurTok]}")
    if tokens[CurTok].type == TokenKind.tok_op_arithmetric:
        op = tokens[CurTok].value
        CurTok += len(op)
        rhs = ParsePrimary(tokens)
        if not rhs:
            return None
        return BinaryExprAst(op, lhs, rhs)
    elif tokens[CurTok].type == TokenKind.tok_endline:
        return lhs
    elif tokens[CurTok].type == TokenKind.tok_comma:
        return lhs
    elif tokens[CurTok].type == TokenKind.tok_close_paren:
        return lhs
    else:
        raise Exception(f"Unexpected token at ParseExpression {tokens[CurTok]}")
    

def ParseIfExpr(tokens):
    global CurTok
    NextToken(tokens)
    cond = ParseExpression(tokens)
    if not cond:
        return None
    if tokens[CurTok].type != TokenKind.tok_then:
        return None
    NextToken(tokens)

    then = ParseExpression(tokens)
    if not then:
        return None
    if tokens[CurTok].type != TokenKind.tok_else:
        return None
    NextToken(tokens)
    elsee = ParseExpression(tokens)
    if not elsee:
        return None
    return IfExprAST(cond, then, elsee)

def ParseReturn(tokens):
    global CurTok
    NextToken(tokens)
    expr = ParseExpression(tokens)
    return ReturnAST(expr)

def ParseAssign(tokens):
    global CurTok
    if tokens[CurTok].type != TokenKind.tok_identifier:
        raise Exception(f"Unexpected token at ParseAssign {tokens[CurTok]}")
    name = tokens[CurTok].value
    NextToken(tokens)
    if tokens[CurTok + 1].type != TokenKind.tok_assign:
        raise Exception(f"Unexpected token at ParseAssign {tokens[CurTok]}")
    NextToken(tokens)
    expr = ParseExpression(tokens)
    return AssignAST(name, expr)

def ParseDimmensionSpecifier(tokens):
    global CurTok
    if tokens[CurTok].type != TokenKind.tok_open_angle:
        raise Exception(f"Unexpected token at ParseDimmensionSpecifier {tokens[CurTok]}")
    NextToken(tokens)
    dims = []
    while True:
        if tokens[CurTok].type == TokenKind.tok_number:
            dims.append(int(tokens[CurTok].value))
        NextToken(tokens)
        if tokens[CurTok].type == TokenKind.tok_comma:
            NextToken(tokens)
            continue
        if tokens[CurTok].type != TokenKind.tok_close_angle:
            raise Exception(f"Unexpected token at Dimmension Spec {tokens[CurTok]}")
        else :
            NextToken(tokens)
            break
    return dims

def ParseVarDefinition(tokens):
    global CurTok
    if tokens[CurTok].type != TokenKind.tok_var:
        raise Exception(f"Unexpected token at ParseVarDefinition {tokens[CurTok]}")
    NextToken(tokens)
    if tokens[CurTok].type != TokenKind.tok_identifier:
        raise Exception(f"Unexpected token at ParseVarDefinition {tokens[CurTok]}")
    name = tokens[CurTok].value
    NextToken(tokens)

    with_dims = False
    if tokens[CurTok].type == TokenKind.tok_open_angle:
        dims = ParseDimmensionSpecifier(tokens)
        with_dims = True
    
    if tokens[CurTok].type != TokenKind.tok_assign:
        if with_dims:
            return VarDefinitionAST(name, None, dims)
        else:
            return VarDefinitionAST(name)
    NextToken(tokens)
    expr = ParseExpression(tokens)
    if with_dims:
        return VarDefinitionAST(name, expr, dims)
    elif expr is TensorLiteralAST:
        return VarDefinitionAST(name, expr, dims=expr.dims)
    return VarDefinitionAST(name, expr)

def ParseTopLevelExpr(tokens):
    global CurTok
    stmts = []
    while CurTok < len(tokens):
        if tokens[CurTok].type == TokenKind.tok_endline:
            NextToken(tokens)
        if tokens[CurTok].type == TokenKind.tok_close_brace:
            return stmts
        
        if tokens[CurTok].type == TokenKind.tok_var:
            stmts.append(ParseVarDefinition(tokens))
        elif tokens[CurTok].type == TokenKind.tok_return:
            stmts.append(ParseReturn(tokens))
        elif tokens[CurTok].type == TokenKind.tok_identifier and tokens[CurTok + 1].type == TokenKind.tok_assign:
            stmts.append(ParseAssign(tokens))
        elif tokens[CurTok].type == TokenKind.tok_identifier and tokens[CurTok + 1].type == TokenKind.tok_open_paren:
            stmts.append(ParseCallExpr(tokens))
        else:
            raise Exception(f"Unexpected token at parse {tokens[CurTok]}")
    return stmts
    
def ParsePrototype(tokens):
    global CurTok
    if tokens[CurTok].type != TokenKind.tok_identifier:
        raise Exception(f"Unexpected token at ParsePrototype {tokens[CurTok]}")
    name = tokens[CurTok].value
    NextToken(tokens)

    if tokens[CurTok].type != TokenKind.tok_open_paren:
        raise Exception(f"Unexpected token at ParsePrototype {tokens[CurTok]}")
    NextToken(tokens)
    args = []
    while True:
        if tokens[CurTok].type == TokenKind.tok_close_paren:
            NextToken(tokens)
            break
        if tokens[CurTok].type == TokenKind.tok_identifier:
            args.append(tokens[CurTok].value)
            NextToken(tokens)
            if tokens[CurTok].type == TokenKind.tok_comma:
                NextToken(tokens)
        else:
            raise Exception(f"Unexpected token at ParsePrototype {tokens[CurTok]}")

    return PrototypeAST(name, args)
    
def ParseDefinition(tokens):
    global CurTok
    if tokens[CurTok].type != TokenKind.tok_def:
        raise Exception(f"Unexpected token at ParseDefinition {tokens[CurTok]}")
    NextToken(tokens)
    proto = ParsePrototype(tokens)
    print(f"ParseDefinition {tokens[CurTok]}")
    if tokens[CurTok].type != TokenKind.tok_open_brace:
        raise Exception(f"Unexpected token at ParseDefinition {tokens[CurTok]}")
    NextToken(tokens)
    body = ParseTopLevelExpr(tokens)
    if tokens[CurTok].type != TokenKind.tok_close_brace:
        raise Exception(f"Unexpected token at ParseDefinition {tokens[CurTok]}")
    NextToken(tokens)
    print(f"END DEFINITION")
    return FunctionAST(proto, body)

def ParseExtern(tokens):
    global CurTok
    if tokens[CurTok].type != TokenKind.tok_extern:
        return None
    NextToken(tokens)

    return ParsePrototype(tokens)


def parse(tokens):
    global CurTok
    CurTok = 0
    asts = []
    while tokens[CurTok] != TokenKind.tok_eof:
        if tokens[CurTok].type == TokenKind.tok_def:
            print(f"parse {tokens[CurTok]}")
            asts.append(ParseDefinition(tokens))
            print(f"parse {tokens[CurTok]}")
            if tokens[CurTok].type == TokenKind.tok_eof:
                break
        else:
            raise Exception(f"Unexpected token at parse {tokens[CurTok]}")
    return asts

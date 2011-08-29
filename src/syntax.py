

import ast
import semantics

class Intrinsics(object):
    def load_attr(self,name):
        return '__intrinsic__.' + name

intrinsics = { '__intrinsic__': Intrinsics() }

class SyntaxVisitor(ast.NodeVisitor):
    
    def __init__(self,name,module_scope=True):
        super(SyntaxVisitor,self).__init__()
        self._globals = set()
        self._locals = set()
        self._module_scope = module_scope
        self.module_list = []
        self.function_list = []
        self._name = name

    def _collectOps(self,list):
        ops = []
        for node in list:
            op = self.visit(node)
            if op is not None:
                ops.append(op)
        return ops

    def visit_Module(self,node):
        print "Module node: %r, node._fields: %r" % (node,node._fields)
        sv = SyntaxVisitor(self._name,module_scope=True)
        ops = sv._collectOps(node.body)
        module = semantics.Module(self._name,ops)
        self.module_list.append(module)
    
    def visit_Assign(self,node):
        if len(node.targets) == 1:
            target = node.targets[0].id
            value = self.visit(node.value)
            if self._module_scope:
                ret = semantics.StoreGlobal(target,value)
            elif target in self._globals:
                ret = semantics.StoreGlobal(target,value)
            else:
                self._locals.add(target)
                ret = semantics.StoreLocal(target,value)
        else:
            raise NotImplementedError("Don't support assign with target len: %d" % len(node.targets))
        return ret
    
    def visit_Name(self,node):
        name = node.id
        if name in intrinsics:
            temp = intrinsics[name]
        elif self._module_scope:
            temp = semantics.LoadGlobal(name)
        elif name in _globals:
            temp = semantics.LoadGlobal(name)
        elif name in _locals:
            temp = semantics.LoadLocal(name)
        else:
            temp = semantics.LoadSmart(name)
        return temp
    
    def visit_Num(self,node):
        return node.n
    
    def visit_Expr(self,node):
        # Do nothing!
        return super(SyntaxVisitor,self).generic_visit(node)
    
    def visit_BinOp(self,node):
        left = self.visit(node.left)
        op = type(node.op)
        right = self.visit(node.right)
        
        if op == ast.Add:
            ret = semantics.Plus(left,right)
        else:
            raise NotImplementedError("BinOp not supported: %s" % op)
        return ret
    
    def visit_Return(self,node):
        value = self.visit(node.value)
        return semantics.Return(value)
    
    def visit_FunctionDef(self,node):
        name = node.name
        decorator_list = []
        for d in node.decorator_list:
            decorator_list.append(self.visit(d))
        print "Decorators: %r" % decorator_list
        sv = SyntaxVisitor(self._name,module_scope=False)
        ops = sv._collectOps(node.body)
        f = semantics.Function(self._name,name,ops)
        self.function_list.append(f)
        return StoreGlobal(name,f)
    
    def visit_Pass(self,node):
        return None
    
    def visit_Global(self,node):
        for n in node.names:
            self._globals.add(n)
        return None
    
    def visit_Attribute(self,node):
        value = self.visit(node.value)
        attr = node.attr
        return LoadAttr(value,attr)
        
    def visit_If(self,node):
        test = self.visit(node.test)
        ops = self._collectOps(self.body)
        return semantics.If(test,ops)
    
    def visit_Compare(self,node):
        left = self.visit(node.left)
        if len(node.comparators) != 1 or len(node.ops) != 1:
            raise NotImplementedError("Don't support this compare node: %s" % ast.dump(node))
        comparator = self.visit(node.comparators[0])
        op = type(node.ops[0])
        if op == ast.Eq:
            ret = semantics.CompareEq(left,comparator)
        else:
            raise NotImplementedError("Don't support this compare node: %s" % ast.dump(node))
        return ret
    
    def generic_visit(self,node):
        raise NotImplementedError("Don't support node type: %r" % node)
    

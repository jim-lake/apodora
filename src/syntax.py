

import ast
import semantics

class SyntaxVisitor(ast.NodeVisitor):
    
    _globals = set()
    _locals = set()
    _module_scope = True
    _semlist = semantics.SemanticList()
    
    def __init__(self,module_scope=True):
        super(SyntaxVisitor,self).__init__()
        self._module_scope = module_scope
    
    def visit_Module(self,node):
        # Do nothing!
        super(SyntaxVisitor,self).generic_visit(node)
    
    def visit_Assign(self,node):
        if len(node.targets) == 1:
            target = node.targets[0].id
            value = self.visit(node.value)
            if self._module_scope:
                self._semlist.store_global(target,value)
            elif target in self._globals:
                self._semlist.store_global(target,value)
            else:
                self._semlist.store_local(target,value)
                self._locals.add(target)
            self._semlist.release_temp(value)
        else:
            raise NotImplementedError("Don't support assign with target len: %d" % len(node.targets))
    
    def visit_Name(self,node):
        name = node.id
        if self._module_scope:
            temp = self._semlist.load_global(name)
        elif name in _globals:
            temp = self._semlist.load_global(name)
        elif name in _locals:
            temp = self._semlist.load_local(name)
        else:
            temp = self._semlist.load_smart(name)
        return temp
    def visit_Num(self,node):
        return node.n
    
    def visit_Expr(self,node):
        # Do nothing!
        super(SyntaxVisitor,self).generic_visit(node)
    
    def visit_BinOp(self,node):
        left = self.visit(node.left)
        op = type(node.op)
        right = self.visit(node.right)
        
        if op == ast.Add:
            ret = self._semlist.plus(left,right)
        else:
            raise NotImplementedError("BinOp not supported: %s" % op)
        
        self._semlist.release_temp(left)
        self._semlist.release_temp(right)
        return ret
    
    def visit_Return(self,node):
        value = self.visit(node.value)
        self._semlist.return_(value)
    
    def visit_FunctionDef(self,node):
        name = node.name
        cv = SyntaxVisitor(module_scope=False)
        for child in node.body:
            cv.visit(child)
        self._semlist.store_global(name,cv)
    
    def visit_Global(self,node):
        for n in node.names:
            self._globals.add(n)
    
    def generic_visit(self,node):
        raise NotImplementedError("Don't support node type: %r" % node)
    
    def get_semantic_list(self):
        return self._semlist;


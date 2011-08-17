

import ast
import semantics

class Intrinsics(object):
    def load_attr(self,name):
        return '__intrinsic__.' + name

intrinsics = { '__intrinsic__': Intrinsics() }

class Module(object):
    def __init__(self,name):
        self.name = name

class SyntaxVisitor(ast.NodeVisitor):
    _static_functions = {}
    _semlists = []
    _modules = {}
    
    def __init__(self,module=None,module_names=None,module_scope=True):
        super(SyntaxVisitor,self).__init__()
        self._globals = set()
        self._locals = set()
        if module is not None:
            self._module = module
        elif module_names is not None:
            module_name = module_names[0]
            if module_name in self._modules:
                self._module = self._modules[module_name]
            else:
                self._module = Module(module_name)
                self._modules[module_name] = self._module
        self._module_scope = module_scope
        self._semlist = semantics.SemanticList(self._module)

    @classmethod
    def get_static_functions(cls):
        return cls._static_functions

    @classmethod
    def get_semantic_lists(cls):
        return cls._semlists;

    def visit_Module(self,node):
        print "Module node: %r, node._fields: %r" % (node,node._fields)
        sv = SyntaxVisitor(module=self._module,module_scope=True)
        sv._semlist.start_module()
        for node in node.body:
            sv.visit(node)
        sv._semlist.end_module()
        self._semlists.append(sv._semlist)
    
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
        if name in intrinsics:
            temp = intrinsics[name]
        elif self._module_scope:
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
        decorator_list = []
        for d in node.decorator_list:
            decorator_list.append(self.visit(d))
        print "Decorators: %r" % decorator_list
        sv = SyntaxVisitor(module=self._module,module_scope=False)
        for child in node.body:
            sv.visit(child)
        if '__intrinsic__.staticfunction' in decorator_list:
            static_name = self._module.name + '.' + name
            self._static_functions[static_name] = sv
        else:
            self._semlist.store_global(name,sv)
    
    def visit_Pass(self,node):
        pass
    
    def visit_Global(self,node):
        for n in node.names:
            self._globals.add(n)
    
    def visit_Attribute(self,node):
        value = self.visit(node.value)
        attr = node.attr
        temp = value.load_attr(attr)
        return temp
    
    def generic_visit(self,node):
        raise NotImplementedError("Don't support node type: %r" % node)
    

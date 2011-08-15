# Main Entry Point

import argparse
import ast
import assembler
import asmhelper

def _hexdump(src, length=8):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*x" % (digits, ord(x))  for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
        result.append( b"%04x   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    return b'\n'.join(result)

class CompileVisitor(ast.NodeVisitor):

    _module_scope = True

    def __init__(self,module_scope=True):
        super(CompileVisitor,self).__init__()
        self._module_scope = module_scope
        self._assembler = assembler.Assembler()

    def visit_Module(self,node):
        # Do nothing!
        super(CompileVisitor,self).generic_visit(node)
    
    def visit_Assign(self,node):
        if len(node.targets) == 1:
            target = node.targets[0].id
            value = self.visit(node.value)
            if self._module_scope:
                self._assembler.store_global(target,value)
            else:
                self._assembler.store(target,value)
            self._assembler.release_temp(value)
        else:
            raise NotImplementedError("Don't support assign with target len: %d" % len(node.targets))

    def visit_Name(self,node):
        return self._assembler.load_global(node.id)
    
    def visit_Num(self,node):
        return node.n
    
    def visit_Expr(self,node):
        # Do nothing!
        super(CompileVisitor,self).generic_visit(node)
    
    def visit_BinOp(self,node):
        left = self.visit(node.left)
        op = type(node.op)
        right = self.visit(node.right)
        
        if op == ast.Add:
            ret = self._assembler.plus(left,right)
        else:
            raise NotImplementedError("BinOp not supported: %s" % op)

        self._assembler.release_temp(left)
        self._assembler.release_temp(right)
        return ret
    
    def visit_Return(self,node):
        value = self.visit(node.value)
        self._assembler.return_(value)

    def visit_FunctionDef(self,node):
        name = node.name
        cv = CompileVisitor(module_scope=False)
        for child in node.body:
            cv.visit(child)
        self._assembler.store_global(name,cv)
    
    def visit_Global(self,node):
        for n in node.names:
            self._assembler.add_global(n)
    
    def generic_visit(self,node):
        raise NotImplementedError("Don't support node type: %r" % node)

    def get_assembler(self):
        return self._assembler;

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Run some python')
    parser.add_argument('file',help='python file to run')
    args = parser.parse_args()

    print "Opening file: %s" % args.file
    file = open(args.file)
    source = file.read()
    root_node = ast.parse(source,args.file)
    
    print "Got root_node: %r" % root_node
    print "Dump: %s" % ast.dump(root_node)
    
    cv = CompileVisitor()
    cv.visit(root_node)
    
    assembler = cv.get_assembler()
    assembler.return_(-1)
    ops = assembler.get_op_string()
    
    print "ops: %r" % ops
    
    print "hexdump(ops): ----"
    print _hexdump(ops)
    print "----"
    
    ret = asmhelper.run_memory(ops)
    print "ret: ", ret
    
    print "Done"


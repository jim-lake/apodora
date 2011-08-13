# Main Entry Point

import argparse
import ast
import assembler

class ModuleVistor(ast.NodeVisitor):

    def __init__(self):
        super(ModuleVistor,self).__init__()
        self._assembler = assembler.Assembler()

    def visit_Module(self,node):
        # Do nothing!
        super(ModuleVistor,self).generic_visit(node)
    
    def visit_Assign(self,node):
        if len(node.targets) == 1:
            target = node.targets[0].id
            value = self.visit(node.value)
            self._assembler.store_global(target,value)
            self._assembler.release_temp(value)
        else:
            raise NotImplementedError("Don't support assign with target len: %d" % len(node.targets))

    def visit_Name(self,node):
        return self._assembler.load_global(node.id)
    
    def visit_Num(self,node):
        return node.n
    
    def visit_Expr(self,node):
        # Do nothing!
        super(ModuleVistor,self).generic_visit(node)
    
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
    
    def generic_visit(self,node):
        raise NotImplementedError("Don't support node type: %r" % node)

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
    
    cv = ModuleVistor()
    cv.visit(root_node)
    
    print "Done"


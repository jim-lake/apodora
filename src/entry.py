# Main Entry Point

import argparse
import ast

TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_OBJECT = 3

class PythonOp(object):
    pass

class GlobalStore(PythonOp):
    def __init__(self,target,type):
        self._target = target
        self._assumed_target_type = type

class GlobalStoreInt(GlobalStore):
    def __init__(self,target,type,num):
        self._target = target;
        self._assumed_target_type = type
        self._num = num

class GlobalStoreFloat(GlobalStore):
    def __init__(self,target,type,num):
        self._target = target;
        self._assumed_target_type = type
        self._num = num

class GlobalStoreCopy(GlobalStore):
    def __init__(self,target,type,source,source_type):
        self._target = target;
        self._assumed_target_type = type
        self._source = source
        self._assumed_source_type = source_type

        
class ModuleVistor(ast.NodeVisitor):
    ops = []
    module_global_types = {}
    
    def visit_Module(self,node):
        # Do nothing!
        super(ModuleVistor,self).generic_visit(node)
    
    def visit_Assign(self,node):
        value = node.value
        
        if len(node.targets) == 1:
            target = node.targets[0].id
            target_type = self.module_global_types.get(target,None)
            if type(value) == ast.Num:
                value = value.n
                if( int(value) == value ):
                    op = GlobalStoreInt(target,target_type,value)
                    self.module_global_types[target] = TYPE_INT
                else:
                    op = GlobalStoreFloat(target,target_type,value)
                    self.module_global_types[target] = TYPE_FLOAT
            elif type(value) == ast.Name:
                value = value.id
                source_type = self.module_global_types.get(value,None)
                op = GlobalStoreCopy(target,target_type,value,source_type)
                self.module_global_types[target] = source_type
            else:
                raise NotImplementedError("Don't support assign with value type: %s" % type(value))
        else:
            raise NotImplementedError("Don't support assign with target len: %d" % len(node.targets))
        
        print "Assign(%s): %s = %s" % (type(op),target,value)
        self.ops.append(op)
    
    def visit_Expr(self,node):
        # Do nothing!
        super(ModuleVistor,self).generic_visit(node)
    
    def visit_BinOp(self,node):
        left = node.left
        op = node.op
        right = node.right
        
        
        
    
    def generic_visit(self,node):
        raise NotImplementedError("Don't node type: %r" % node)
    

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
    
    print "ops = ", cv.ops
    
    print "Done"


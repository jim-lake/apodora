# Main Entry Point

import argparse
import ast

class CompileVisitor(ast.NodeVisitor):

    def visit_Module(self,node):
        print "Module: %s" % node
        for name,value in ast.iter_fields(node):
            print "  Field: %s,%s" % (name,value)
        super(CompileVisitor,self).generic_visit(node)

    def generic_visit(self,node):
        print "node: %s" % node
        super(CompileVisitor,self).generic_visit(node)


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
    
    print "Done"


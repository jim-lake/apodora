# Main Entry Point

import argparse
import ast


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Run some python')
    parser.add_argument('file',help='python file to run')
    args = parser.parse_args()

    print "Opening file: %s" % args.file
    file = open(args.file)
    source = file.read()
    file_ast = ast.parse(source,args.file)
    
    print "Got ast: %r" % file_ast

    print "Dump: %s" % ast.dump(file_ast)


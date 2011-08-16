# Main Entry Point

import argparse
import ast
import assembler
import asmhelper
import syntax

def _hexdump(src, length=8):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*x" % (digits, ord(x))  for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
        result.append( b"%04x   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    return b'\n'.join(result)

def read_file(name,module_name=None):
    if module_name is None:
        module_name = name
    print "Opening file: %s" % name
    file = open(name)
    source = file.read()
    root_node = ast.parse(source,name)
    
    print "Got root_node: %r" % root_node
    print "Dump: %s" % ast.dump(root_node)
    
    sv = syntax.SyntaxVisitor(module_name)
    sv.visit(root_node)
    sl = sv.get_semantic_list()
    sl.return_(-1)
    asm = sl.get_assembler()
    return asm.get_op_string()

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Run some python')
    parser.add_argument('file',help='python file to run')
    args = parser.parse_args()

    compiler_ops = read_file('lib/compiler.py','__compiler__')
    ops = read_file(args.file,'__main__')
    
    print "compiler_ops: %r" % compiler_ops
    print "ops: %r" % ops
    
    print "hexdump(ops): ----"
    print _hexdump(ops)
    print "----"
    
    ret = asmhelper.run_memory(ops)
    print "ret: ", ret
    
    print "Done"


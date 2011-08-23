# Main Entry Point

import argparse
import ast
import os.path

import assembler
import asmhelper
import syntax
import semantics

def _hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*x" % (digits, ord(x))  for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
        result.append( b"%04x   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    return b'\n'.join(result)


def get_premain():
    module = syntax.Module('__intrinsic__')
    semlist = semantics.SemanticList(module)
    semlist.premain()
    return semlist

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Run some python')
    parser.add_argument('file',help='python file to run')
    args = parser.parse_args()

    linker = assembler.Linker()
    premain = get_premain()
    linker.add_assembly(premain.get_assembler())

    def read_file(name,module_names=None):
        if module_names is None:
            module_names = [name]
        print "Opening file: %s" % name
        file = open(name)
        source = file.read()
        root_node = ast.parse(source,name)
        print "Got root_node: %r" % root_node
        print "Dump: %s" % ast.dump(root_node)
        sv = syntax.SyntaxVisitor(module_names=module_names)
        sv.visit(root_node)

    #read_file('lib/compiler.py',['__compiler__'])
    mod_name = os.path.splitext(os.path.basename(args.file))[0]
    read_file(args.file,['__main__',mod_name])

    sls = syntax.SyntaxVisitor.get_semantic_lists()
    for sl in sls:
        asm = sl.get_assembler()
        linker.add_assembly(asm)
    
    data_entries = assembler.DataSegment.get_data()
    for d in data_entries:
        linker.add_data(d)
    
    data_len = linker.get_data_len()
    data_base = asmhelper.alloc_memory(data_len)
    linker.set_data_address(data_base)
    
    print "Data len: %d, base address: 0x%016x" % (data_len,data_base)
    
    text = linker.get_text()
    
    print "Static Functions: ----"
    sfmap = syntax.SyntaxVisitor.get_static_functions()
    for k,v in sfmap.iteritems():
        print "  %s = %s" % (k,v)
    print "----"

    print "Modules: ----"
    module_map = syntax.SyntaxVisitor.get_modules()
    for k,v in module_map.iteritems():
        print "  %s = %s" % (k,v)
    print "----"

    
    #print "text: %r" % text
    
    print "hexdump(text): ----"
    print _hexdump(text)
    print "----"
    
    ret = asmhelper.run_memory(text)
    print "ret: ", ret
    
    print "Done"




import assembler

class AsmTemp(object):
    def __init__(self,semlist,name=None):
        self._name = name
        self._semlist = semlist
    
    def __str__(self):
        return "Temp(name=%s)" % self._name

    def load_attr(self,name):
        return self._semlist.load_attr(self,name)

TYPE_UNKNOWN = 0
TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_OBJECT = 3

class VariableStoreOp(object):
    def __init__(self,target,source):
        self.target = target
        self.source = source

class VariableInfo(object):
    def __init__(self,type=TYPE_UNKNOWN):
        self.type = type


class SemanticList(object):
    
    def __init__(self,module):
        self._module = module
        self._globals = dict()
        self._locals = dict()
        self._asm = assembler.Assembler()
    
    def get_assembler(self):
        return self._asm

    def start_module(self):
        module_start_label = self._module.name + ':__start__'
        self._asm.add_label(module_start_label)
        self.function_prefix()

    def end_module(self):
        self.function_cleanup()
        self._asm.RETQ()
    
    def store_global(self,target,source):
        if target in self._globals:
            pass
        else:
            pass
        print "Store Global: %s=%s" % (target,source)
    
    def store(self,target,source):
        if target in self._globals:
            self.store_global(target,source)
        else:
            self.store_local(target,source)

    def store_local(self,target,source):
        pass
    
    def load_global(self,name):
        temp = AsmTemp(self,name)
        print "Load Temp: %s" % temp
        return temp
    
    def load_local(self,name):
        pass
    
    def load_smart(self,name):
        pass
        
    def load_attr(self,object,name):
        temp = AsmTemp(self,"%s.%s" % (object,name)) 
        print "Load Attribute: %s" % temp
        return temp
    
    def release_temp(self,temp):
        if type(temp) == AsmTemp:
            print "Release Temp: %s" % temp
    
    def plus(self,left,right):
        temp = AsmTemp(self)
        print "Add: %s=%s + %s" % (temp,left,right)
        return temp
    
    def plus_equals(self,target,increment):
        pass
    
    def return_(self,value):
        print "Return: %s" % value
        if type(value) is int:
            self._asm.MOVQ_RAX_IMM(value)
        else:
            raise NotImplementedError("Unsupported return value")
        
        self.function_cleanup()
        self._asm.RETQ()
    
    def function_prefix(self):
        # Save RBP
        self._asm.PUSHQ_RBP()
        # Make RBP RSP
        self._asm.MOVQ_RBP_RSP()
    
    
    def function_cleanup(self):
        # Restore RBP
        self._asm.POPQ_RBP()
    
    
    
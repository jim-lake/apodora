

import struct

class AsmTemp(object):
    def __init__(self,name=None):
        self._name = name
        
    def __str__(self):
        return "Temp(name=%s)" % self._name

INT32_MAX = pow(2,31) - 1
INT32_MIN = -pow(2,31)

TYPE_UNKNOWN = 0
TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_OBJECT = 3

class VariableStoreOp(object):
    def __init__(self,target,source):
        self.target = target
        self.source = source

class VariableInfo(object):
    type = TYPE_UNKNOWN
    def __init__(self,type=TYPE_UNKNOWN):
        self.type = type

class Assembler(object):

    _globals = {}
    _locals = {}
    
    _ops = []

    def __init__(self):
        self.function_prefix()

    def get_op_string(self):
        return ''.join(self._ops)

    def add_global(self,name):
        self._globals[name] = VariableInfo()

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
            self._ops.append(VariableStoreOp(target,source))
    
    def store_local(self,target,source):
        pass
        
    
    def load_global(self,name):
        temp = AsmTemp(name)
        print "Load Temp: %s" % temp
        return temp
    
    def load_local(self,name):
        pass
    
    def load_smart(self,name):
        pass

    def release_temp(self,temp):
        if type(temp) == AsmTemp:
            print "Release Temp: %s" % temp
    
    def plus(self,left,right):
        temp = AsmTemp()
        print "Add: %s=%s + %s" % (temp,left,right)
        return temp
    
    def plus_equals(self,target,increment):
        pass
    
    def return_(self,value):
        print "Return: %s" % value
        if type(value) is int:
            self.MOVQ_RAX_IMM(value)
        else:
            raise NotImplementedError("Unsupported return value")

        self.function_cleanup()
        self.RETQ()

    def function_prefix(self):
        # Save RBP
        self.PUSHQ_RBP()
        # Make RBP RSP
        self.MOVQ_RBP_RSP()
        
    
    def function_cleanup(self):
        # Restore RBP
        self.POPQ_RBP()

    # Functions that equate to Intel x64 instructions

    def MOVQ_RAX_IMM(self,imm):
        if imm == 0:
            self.XOR_RAX_RAX()
        elif imm > 0 and imm < INT32_MAX:
            bytes = struct.pack("=i",imm)
            self._ops.append('\xb8' + bytes)
        elif imm < 0 and imm > INT32_MIN:
            bytes = struct.pack("=i",imm)
            self._ops.append('\x48\xc7\xc0' + bytes)
        else:
            raise NotImplementedError("Unsupported immediate: %d" % imm)

    def XOR_RAX_RAX(self):
        self._ops.append('\x31\xc0')

    def PUSHQ_RBP(self):
        self._ops.append('\x55')
        
    def MOVQ_RBP_RSP(self):
        self._ops.append('\x48\x89\xe5')
        
    def RETQ(self):
        self._ops.append('\xc3')
    
    def POPQ_RBP(self):
        self._ops.append('\x5d')
    
    
    
    



import struct

INT32_MAX = pow(2,31) - 1
INT32_MIN = -pow(2,31)

class TextLabel(object):
    name = ""
    def __init__(self,name):
        self.name = name

class Assembler(object):

    def __init__(self):
        self._ops = []

    def get_op_string(self):
        return ''.join(self._ops)

    def add_label(self,name):
        self._ops.append(TextLabel(name))
    
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
    
class Linker(object):
    _assemblies = []
    _data = []
    
    def add_assembly(self,asm):
        self._assemblies.append(asm)
    
    def add_data(self,data):
        self._data.append(asm)
    
    def get_data(self):
        return ''.join(_data)

    def set_data_address(self,addr):
        self._data_address = addr
    
    def get_text(self):
        text_segments = []
        for asm in self._assemblies:
            text_segments.append(asm.get_op_string())
        return ''.join(text_segments)




import struct

INT32_MAX = pow(2,31) - 1
INT32_MIN = -pow(2,31)

class RelativeAddress32(object):
    def __init__(self,label):
        self.label = label

class TextLabel(object):
    def __init__(self,name):
        self.name = name

class Assembler(object):

    def __init__(self):
        self.ops = []

    def add_label(self,name):
        self.ops.append(TextLabel(name))
    
    # Functions that equate to Intel x64 instructions

    def CALL_REL32(self,label):
        self.ops.append('\xe8')
        self.ops.append(RelativeAddress32(label))

    def MOVQ_RAX_IMM(self,imm):
        if imm == 0:
            self.XOR_RAX_RAX()
        elif imm > 0 and imm < INT32_MAX:
            bytes = struct.pack("=i",imm)
            self.ops.append('\xb8' + bytes)
        elif imm < 0 and imm > INT32_MIN:
            bytes = struct.pack("=i",imm)
            self.ops.append('\x48\xc7\xc0' + bytes)
        else:
            raise NotImplementedError("Unsupported immediate: %d" % imm)

    def XOR_RAX_RAX(self):
        self.ops.append('\x31\xc0')

    def PUSHQ_RBP(self):
        self.ops.append('\x55')
        
    def MOVQ_RBP_RSP(self):
        self.ops.append('\x48\x89\xe5')
        
    def RETQ(self):
        self.ops.append('\xc3')
    
    def POPQ_RBP(self):
        self.ops.append('\x5d')
    
class Linker(object):
    def __init__(self):
        self._assemblies = []
        self._data = []
    
    def add_assembly(self,asm):
        self._assemblies.append(asm)
    
    def add_data(self,data):
        self._data.append(asm)
    
    def get_data(self):
        return ''.join(_data)

    def set_data_address(self,addr):
        self._data_address = addr
    
    def get_text(self):
        labels = {}
        address_resolutions = []
        text = bytearray()
        for asm in self._assemblies:
            for op in asm.ops:
                if type(op) == str:
                    text.extend(op)
                elif type(op) == TextLabel:
                    labels[op.name] = len(text)
                elif type(op) == RelativeAddress32:
                    ar = { 'op': op, 'offset': len(text) }
                    address_resolutions.append(ar)
                    text.extend('\xDE\xAD\xBE\xEF')
                else:
                    raise NotImplementedError("Unsupported ASM OP: %r" % op)

        print "labels: %r" % labels
        print "address_resolutions: %r" % address_resolutions
        return str(text)




import struct

INT32_MAX = pow(2,31) - 1
INT32_MIN = -pow(2,31)

class AbsoluteAddress32(object):
    def __init__(self,label):
        self.label = label
    def __str__(self):
        return "AbsoluteAddress32(label=%s)" % self.label

class AbsoluteAddress64(object):
    def __init__(self,label):
        self.label = label
    def __str__(self):
        return "AbsoluteAddress64(label=%s)" % self.label

class RelativeAddress32(object):
    def __init__(self,label):
        self.label = label
    def __str__(self):
        return "RelativeAddress32(label=%s)" % self.label

class TextLabel(object):
    def __init__(self,name):
        self.name = name
    def __str__(self):
        return "TextLabel(name=%s)" % self._name

class DataPointer(object):
    def __init__(self,name,value):
        self.name = name
        self.value = value

class DataSegment(object):
    _values = []
    
    @classmethod
    def add_pointer(cls,name,value):
        cls._values = DataPointer(name,value)

    @classmethod
    def get_data(cls):
        cls._values

class Register(object):
    def __init__(self,name,bitmask):
        self.name = name
        self.bitmask = bitmask
        self.available = True
    
C_CALL_CLOBBER_REGS = ('RAX','RCX','RDX','RSI','RDI','R8','R9','R10','R11')

class RegisterAllocator(object):
    def __init__(self):
        regs = []
        regs.append(Register('RAX',0x0))
        regs.append(Register('RCX',0x1))
        regs.append(Register('RDX',0x2))
        regs.append(Register('RBX',0x3))
        regs.append(Register('RSI',0x6))
        regs.append(Register('RDI',0x7))
        regs.append(Register('R8',0x8))
        regs.append(Register('R9',0x9))
        regs.append(Register('R10',0xa))
        regs.append(Register('R11',0xb))
        regs.append(Register('R12',0xc))
        regs.append(Register('R13',0xd))
        regs.append(Register('R14',0xe))
        regs.append(Register('R15',0xf))
        self._registers = regs

    def allocate_reg(self):
        for r in self._registers:
            if r.available:
                print "Allocate reg: ",r.name
                r.available = False
                return r
        raise NotImplementedError("Out of registers!")
    
    def free_reg(self,reg):
        reg.available = True

    def used_c_call_clobber_regs(self):
        outs = []
        for r in self._registers:
            if r.name in C_CALL_CLOBBER_REGS and not r.available:
                outs.append(r)
        return outs

def _make_rex_modrm(rm=None,reg=None,offset=None,w=True):
    if offset == None:
        modrm = 0xc0
    elif offset == 0:
        modrm = 0
    elif abs(offset) < 128:
        modrm = 0x40
    else:
        raise NotImplementedError("Only support 64bit operation")
    
    rm = rm.bitmask if rm else 0
    reg = reg.bitmask if reg else 0
    w = 1 if w else 0
    rm_high = 1 if rm & 0x8 else 0
    reg_high = 1 if reg & 0x8 else 0
    
    rex = 0x40 | w << 3 | rm_high << 2 | reg_high
    modrm = modrm | (rm & 0x7) << 3 | (reg & 0x7)
    return struct.pack("=B",rex),struct.pack("=B",modrm)

def _make_rex_opcode(opcode,reg=None,w=True):
    reg = reg.bitmask if reg else 0
    reg_high = 1 if reg & 0x8 else 0
    
    rex = 0x40 | w << 3 | reg_high
    opcode = opcode | reg & 0x7
    return struct.pack("=B",rex),struct.pack("=B",opcode)


class Assembler(object):

    def __init__(self):
        self._regs = RegisterAllocator()
        self.ops = []

    def add_label(self,name):
        self.ops.append(TextLabel(name))
    
    def release_reg(self,reg):
        self._regs.free_reg(reg)
    
    def call_c_function(self,name,*args):
        pushs = self._regs.used_c_call_clobber_regs()
        for r in pushs:
            self.PUSH_REG(r)

        
        
        for r in reversed(pushs):
            self.POP_REG(r)
        

    
    # Functions that equate to Intel x64 instructions

    def CALL_REL32(self,label):
        self.ops.append('\xe8')
        self.ops.append(RelativeAddress32(label))

    def MOV_RAX_IMM(self,imm):
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

        
    def MOV_REG_IMM(self,imm):
        reg = self._regs.allocate_reg()
        rex,modrm = _make_rex_modrm(rm=reg)
        if abs(imm) < INT32_MAX:
            imm_bytes = struct.pack("=i",imm)
            self.ops.append(rex + '\xc7' + modrm + imm_bytes)
        else:
            raise NotImplementedError("Unsuppported immediate: %d" % imm)
        return reg

    def MOV_MEM_REG(self,dest,src,offset=0):
        rex,modrm = _make_rex_modrm(rm=dest,offset=offset,reg=src)
        if offset == 0:
            self.ops.append(rex + '\x89' + modrm)
        elif abs(offset) < 256:
            offset_bytes = struct.pack("=B",offset)
            self.ops.append(rex + '\x89' + modrm + offset_bytes)
        else:
            raise NotImplementedError("Unsupported offset: %d" % offset)

    def MOV_RIP_REL_REG(self,label,src):
        rex,modrm = _make_rex_modrm(rm='RIP',reg=src)
        self.ops.append(rex + '\x89' + modrm)
        self.ops.append(RelativeAddress32(label))

    def MOV_REG_ABS32(self,label):
        reg = self._regs.allocate_reg()
        rex,modrm = _make_rex_modrm(rm=reg)
        self.ops.append(rex + '\xc7' + modrm)
        self.ops.append(AbsoluteAddress32(label))
        return reg

    def MOV_REG_ABS64(self,label):
        reg = self._regs.allocate_reg()
        rex,opcode = _make_rex_opcode(0xb8,reg)
        self.ops.append(rex + opcode)
        self.ops.append(AbsoluteAddress64(label))
        return reg

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
        
    def PUSH_REG(self,reg):
        rex,opcode = _make_rex_opcode(0x50,reg)
        self.ops.append(rex + opcode)

    def POP_REG(self,reg):
        rex,opcode = _make_rex_opcode(0x58,reg)
        self.ops.append(rex + opcode)
        
    def JNE_REL32(self,label):
        self.ops.append('\x0f\x85')
        self.ops.append(RelativeAddress32(label))
    
    def CMP_REG_REG(self,reg1,reg2):
        raise NotImplementedError("Unsupported instruction type")
    
class Linker(object):
    def __init__(self):
        self._assemblies = []
        self._data = []
    
    def add_assembly(self,asm):
        self._assemblies.append(asm)
    
    def add_data(self,data):
        self._data.append(data)
    
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
                elif type(op) in (RelativeAddress32,AbsoluteAddress32):
                    ar = { 'op': op, 'offset': len(text) }
                    address_resolutions.append(ar)
                    text.extend('\xDE\xAD\xBE\xEF')
                elif type(op) == AbsoluteAddress64:
                    ar = { 'op': op, 'offset': len(text) }
                    address_resolutions.append(ar)
                    text.extend('\x12\x34\x56\x78\x90\xab\xcd\xef')
                else:
                    raise NotImplementedError("Unsupported ASM OP: %s" % op)

        print "labels: %s" % labels
        print "address_resolutions: %s" % address_resolutions
        print "text(pre-resolve): %r" % text

        for ar in address_resolutions:
            op = ar['op']
            if type(op) == RelativeAddress32:
                i = ar['offset']
                dst = labels[op.label]
                delta = dst - src
                bytes = struct.pack("=i",delta)
                text[i:i+4] = bytes
            elif type(op) == AbsoluteAddress32:
                i = ar['offset']
                dst = labels[op.label]
                bytes = struct.pack("=i",dst)
                text[i:i+4] = bytes
            elif type(op) == AbsoluteAddress64:
                i = ar['offset']
                dst = labels[op.label]
                bytes = struct.pack("=q",dst)
                text[i:i+8] = bytes
            else:
                raise NotImplementedError("Unknown address resolution type: %r" % op)

        print "text(post-resolve): %r" % text
        return str(text)


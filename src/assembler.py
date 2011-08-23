
import struct

import asmhelper

INT32_MAX = pow(2,31) - 1
INT32_MIN = -pow(2,31)

def _hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in xrange(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*x" % (digits, ord(x))  for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.'  for x in s])
        result.append( b"%04x   %-*s   %s" % (i, length*(digits + 1), hexa, text) )
    return b'\n'.join(result)


class AbsoluteAddress32(object):
    def __init__(self,label):
        self.label = label
    def __repr__(self):
        return str(self)
    def __str__(self):
        return "AbsoluteAddress32(label=%s)" % self.label

class AbsoluteAddress64(object):
    def __init__(self,label):
        self.label = label
    def __repr__(self):
        return str(self)
    def __str__(self):
        return "AbsoluteAddress64(label=%s)" % self.label

class RelativeAddress32(object):
    def __init__(self,label):
        self.label = label
    def __repr__(self):
        return str(self)
    def __str__(self):
        return "RelativeAddress32(label=%s)" % self.label

class TextLabel(object):
    def __init__(self,name):
        self.name = name
    def __repr__(self):
        return str(self)
    def __str__(self):
        return "TextLabel(name=%s)" % self.name

class DataPointer(object):
    def __init__(self,name,value):
        self.name = name
        self.value = value
    def __repr__(self):
        return str(self)
    def __str__(self):
        return "DataPointer(name=%s,initial value=%s)" % (self.name,self.value)

class DataSegment(object):
    _values = []
    
    @classmethod
    def add_pointer(cls,name,value):
        dp = DataPointer(name,value)
        print "Add pointer: %s" % dp
        cls._values.append(dp)

    @classmethod
    def get_data(cls):
        return cls._values

class Register(object):
    def __init__(self,name,bitmask):
        self.name = name
        self.bitmask = bitmask
        self.available = True
    def __str__(self):
        return self.name
    
C_CALL_CLOBBER_REGS = ('RAX','RCX','RDX','RSI','RDI','R8','R9','R10','R11')

C_CALL_REG_ARG_SEQUENCE = ('RDI','RSI','RDX','RCX','R8','R9')

C_CALL_REG_RETURN_SEQUENCE = ('RAX','RDX')

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
        print "Free reg: ", reg.name
        reg.available = True

    def used_c_call_clobber_regs(self):
        outs = []
        for r in self._registers:
            if r.name in C_CALL_CLOBBER_REGS and not r.available:
                outs.append(r)
        return outs

    def get_reg_by_name(self,name):
        for r in self._registers:
            if r.name == name:
                return r
        raise ValueError("Unknown register: %s" % name)

def _make_rex_modrm(rm=None,reg=None,offset=None,w=True,extension=0):
    if offset == None:
        modrm = 0xc0
    elif offset == 0:
        modrm = 0
    elif abs(offset) < 128:
        modrm = 0x40
    else:
        raise NotImplementedError("Only support 64bit operation")
    
    rm = rm.bitmask if rm else 0
    reg = reg.bitmask if reg else extension
    w = 1 if w else 0
    rm_high = 1 if rm & 0x8 else 0
    reg_high = 1 if reg & 0x8 else 0
    print "rm=%x,reg=%x,modrm=%x" % (rm,reg,modrm)
    rex = 0x40 | w << 3 | rm_high << 2 | reg_high
    modrm = modrm | (reg & 0x7) << 3 | (rm & 0x7)
    print "rex=%x,modrm=%x" % (rex,modrm)
    rex = struct.pack("=B",rex)
    modrm = struct.pack("=B",modrm)
    if not w and not reg_high and not rm_high:
        rex = ''
    return rex,modrm

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
    
    def call_c_function(self,function_name,*args):
        pushs = self._regs.used_c_call_clobber_regs()
        for r in pushs:
            self.PUSH_REG(r)
        arg_num = 0
        for a in args:
            if type(a) == int:
                reg_name = C_CALL_REG_ARG_SEQUENCE[arg_num]
                reg = self._regs.get_reg_by_name(reg_name)
                self.MOV_REG_IMM(reg,a)
            else:
                raise NotImplementedError("Non immediate arguments not implemented")
        rax = self._regs.get_reg_by_name('RAX')
        function_symbol = 'c-call:' + function_name
        self.MOV_REG_ABS64(rax,function_symbol)
        self.CALL_REG(rax)
        ret_reg = self._regs.allocate_reg()
        self.MOV_REG_REG(ret_reg,rax)
        for r in reversed(pushs):
            self.POP_REG(r)
        return ret_reg
    
    # Functions that equate to Intel x64 instructions

    def CALL_REG(self,reg):
        print "CALL_REG(%s)" % reg
        rex,modrm = _make_rex_modrm(rm=reg,w=False,extension=2)
        self.ops.append(rex + '\xFF' + modrm)
        print "OPCODE: %x,%x,%x" % (ord(rex if rex else '\x00'),ord('\xff'),ord(modrm))

    def CALL_REL32(self,label):
        print "CALL_REL32(%s)" % label
        self.ops.append('\xe8')
        self.ops.append(RelativeAddress32(label))

    def MOV_RAX_IMM(self,imm):
        print "MOV_RAX_IMM(%d)" % imm
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

        
    def MOV_REG_IMM(self,arg1,arg2=None):
        if arg2 is None:
            reg = self._regs.allocate_reg()
            imm = arg1
        else:
            reg = arg1
            imm = arg2
        print "MOV_REG_IMM(%s,%s)" % (reg,imm)
        rex,modrm = _make_rex_modrm(rm=reg)
        if abs(imm) < INT32_MAX:
            imm_bytes = struct.pack("=i",imm)
            self.ops.append(rex + '\xc7' + modrm + imm_bytes)
            print "OPCODE: %x,%x,%x" % (ord(rex),ord('\xc7'),ord(modrm))
        else:
            raise NotImplementedError("Unsuppported immediate: %d" % imm)
        return reg

    def MOV_MEM_REG(self,dest,src,offset=0):
        print "MOV_MEM_REG(dest=%s,src=%s,offset=%d)" % (dest,src,offset)
        rex,modrm = _make_rex_modrm(rm=dest,offset=offset,reg=src)
        if offset == 0:
            self.ops.append(rex + '\x89' + modrm)
        elif abs(offset) < 256:
            offset_bytes = struct.pack("=B",offset)
            self.ops.append(rex + '\x89' + modrm + offset_bytes)
        else:
            raise NotImplementedError("Unsupported offset: %d" % offset)

    def MOV_RIP_REL_REG(self,label,src):
        print "MOV_RIP_REL_REG(label=%s,src=%s)" % (label,src)
        rex,modrm = _make_rex_modrm(rm='RIP',reg=src)
        self.ops.append(rex + '\x89' + modrm)
        self.ops.append(RelativeAddress32(label))

    def MOV_REG_ABS32(self,label):
        print "MOV_REG_ABS32(%s)" % label
        reg = self._regs.allocate_reg()
        rex,modrm = _make_rex_modrm(rm=reg)
        self.ops.append(rex + '\xc7' + modrm)
        self.ops.append(AbsoluteAddress32(label))
        return reg

    def MOV_REG_ABS64(self,arg1,arg2=None):
        if arg2 == None:
            reg = self._regs.allocate_reg()
            label = arg1
        else:
            reg = arg1
            label = arg2
        print "MOV_REG_ABS64(reg=%s,label=%s)" % (reg,label)
        rex,opcode = _make_rex_opcode(0xb8,reg)
        self.ops.append(rex + opcode)
        self.ops.append(AbsoluteAddress64(label))
        return reg
        
    def MOV_REG_REG(self,dest,src):
        print "MOV_REG_REG(dest=%s,src=%s)" % (dest,src)
        rex,modrm = _make_rex_modrm(rm=dest,reg=src)
        self.ops.append(rex + '\x89' + modrm)

    def XOR_RAX_RAX(self):
        print "XOR_RAX_RAX()"
        self.ops.append('\x31\xc0')

    def PUSHQ_RBP(self):
        print "PUSHQ_RBP()"
        self.ops.append('\x55')
        
    def MOVQ_RBP_RSP(self):
        print "MOVQ_RBP_RSP()"
        self.ops.append('\x48\x89\xe5')
        
    def RETQ(self):
        print "RETQ()"
        self.ops.append('\xc3')
    
    def POPQ_RBP(self):
        print "POPQ_RBP()"
        self.ops.append('\x5d')
        
    def PUSH_REG(self,reg):
        print "PUSH_REG(%s)" % reg
        rex,opcode = _make_rex_opcode(0x50,reg)
        self.ops.append(rex + opcode)

    def POP_REG(self,reg):
        print "POP_REG(%s)" % reg
        rex,opcode = _make_rex_opcode(0x58,reg)
        self.ops.append(rex + opcode)
        
    def JNE_REL32(self,label):
        print "JNE_REL32(%s)" % label
        self.ops.append('\x0f\x85')
        self.ops.append(RelativeAddress32(label))
    
    def CMP_REG_REG(self,reg1,reg2):
        raise NotImplementedError("Unsupported instruction type")
    
class Linker(object):
    def __init__(self):
        self._assemblies = []
        self._data = []
        self._data_address = None
    
    def add_assembly(self,asm):
        self._assemblies.append(asm)
    
    def add_data(self,data):
        self._data.append(data)
    
    def get_data(self):
        for d in self._data:
            pass

    def get_data_len(self):
        return len(self._data)*8

    def set_data_address(self,addr):
        self._data_address = addr
    
    def get_text(self):
        if self._data_address is None:
            raise NotImplementedError("Data address needed before text generation")

        labels = {}
        data = bytearray()
        for d in self._data:
            labels[d.name] = len(data) + self._data_address
            bytes = struct.pack('=Q',d.value)
            data.extend(bytes)
        text_address_resolutions = []
        text = bytearray()
        for asm in self._assemblies:
            for op in asm.ops:
                if type(op) == str:
                    text.extend(op)
                elif type(op) == TextLabel:
                    labels[op.name] = len(text)
                elif type(op) in (RelativeAddress32,AbsoluteAddress32):
                    ar = { 'op': op, 'offset': len(text) }
                    text_address_resolutions.append(ar)
                    text.extend('*--*')
                elif type(op) == AbsoluteAddress64:
                    ar = { 'op': op, 'offset': len(text) }
                    text_address_resolutions.append(ar)
                    text.extend('**----**')
                else:
                    raise NotImplementedError("Unsupported ASM OP: %s" % op)

        print "labels: %s" % labels
        print "text_address_resolutions: %s" % text_address_resolutions
        print "text(pre-resolve): ----"
        print _hexdump(str(text))
        print "----"

        def get_addr_for_label(label):
            if label in labels:
                return labels[label]
            elif label.startswith('c-call:'):
                c_call = label[len('c-call:'):]
                print "getting address for c_call: ",c_call
                addr = asmhelper.get_symbol_address(c_call)
                print "got addr: %x" % addr
                return addr
            else:
                raise ValueError("Failed to find addr for name: %s" % label)
                

        for ar in text_address_resolutions:
            op = ar['op']
            if type(op) == RelativeAddress32:
                src = ar['offset']
                dst = get_addr_for_label(op.label)
                delta = dst - ( src + 4 )
                bytes = struct.pack("=i",delta)
                text[src:src+4] = bytes
            elif type(op) == AbsoluteAddress32:
                src = ar['offset']
                dst = get_addr_for_label(op.label)
                bytes = struct.pack("=i",dst)
                text[src:src+4] = bytes
            elif type(op) == AbsoluteAddress64:
                src = ar['offset']
                dst = get_addr_for_label(op.label)
                bytes = struct.pack("=q",dst)
                text[src:src+8] = bytes
            else:
                raise NotImplementedError("Unknown address resolution type: %r" % op)

        return str(text)


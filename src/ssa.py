
import assembler

class SSAList(object):
    def __init__(self):
        self.ssa_ops = []
        self.phi_list = []
        
    def add(self,ssa_class,*args,**kwargs):
        op = ssa_class(*args,**kwargs)
        self.ssa_ops.append(op)
        return op.return_value()

    def phi(self,*args):
        self.phi_list.append(args)

    def __iter__(self):
        return self.ssa_ops.__iter__()

class SSAOp(object):
    def __str__(self):
        return "SSA Op: %s: %s" % (type(self),self.__dict__)

    def return_value(self):
        return None
    
    def to_asm(self,asm,**kwargs):
        raise NotImplementedError("SSA to ASM not implemented for op type: %s" % type(self))

class FunctionStart(SSAOp):
    def __init__(self,name):
        self.name = name
    def to_asm(self,asm,**kwargs):
        asm.function_prefix(self.name)

class FunctionEnd(SSAOp):
    def to_asm(self,asm,**kwargs):
        asm.function_cleanup()
        asm.RETQ()

class Return(SSAOp):
    def __init__(self,value):
        self.value = value

    def to_asm(self,asm,**kwargs):
        print "Return: %s" % self.value
        if type(self.value) is int:
            asm.MOV_RAX_IMM(self.value)
        else:
            raise NotImplementedError("Unsupported return value")
        asm.function_cleanup()
        asm.RETQ()

class CallFunction(SSAOp):
    def __init__(self,name):
        self.name = name
    
    def to_asm(self,asm,**kwargs):
        asm.CALL_REL32(self.name)

class SSAVariable(object):
    def __init__(self):
        self.register = None

    def phi(self,other):
        other.alias = self
    
    def set_register(self,reg):
        self.register = reg

class SSAVariableOp(SSAOp):
    def return_value(self):
        self._return_value = SSAVariable()
        return self._return_value

    def reg(self):
        self._return_value.register

class Immediate(SSAVariableOp):
    def __init__(self,imm):
        self.imm = imm

    def to_asm(self,asm,**kwargs):
        reg = asm.MOV_REG_IMM(self.reg(),self.imm)
        self._return_value.set_register(reg)

class Add(SSAVariableOp):
    def __init__(self,left,right):
        self.left = left
        self.right = right

class WriteGlobalPointer(SSAOp):
    def __init__(self,label,value):
        self.label = label
        self.value = value

class ReadMemory(SSAVariableOp):
    def __init__(self,dest,address):
        self.dest = dest
        self.address = address

class WriteMemory(SSAOp):
    def __init__(self,address,value,offset=None):
        self.address = address
        self.value = value
        self.offset = offset

    def to_asm(self,asm,**kwargs):
        asm.MOV_MEM_REG(self.address,self.value,offset=self.offset)

class CallCFunction(SSAVariableOp):
    def __init__(self,name,*args):
        self.name = name
        self.args = args
        
    def to_asm(self,asm,**kwargs):
        reg = asm.call_c_function(self.name,*self.args)
        self._return_value.set_register(reg)

class CompareEQ(SSAOp):
    def __init__(self,left,right):
        self.left = left
        self.right = right
        
    def to_asm(self,asm,true_label=None,false_label=None):
        pass

class CompareLTE(SSAOp):
    def __init__(self,left,right):
        self.left = left
        self.right = right

class If(SSAOp):
    _counter = 0

    def __init__(self,test,true_ops,false_ops = []):
        self.test = test
        self.true_ops = true_ops
        self.false_ops = false_ops
    
    def to_asm(self,asm,**kwargs):
        false_label = 'If:False:%d' % self._counter
        end_label = 'If:End:%d' % self._counter
        self._counter += 1
        test.to_asm(asm,false_label)
        for op in true_ops:
            op.to_asm(asm)
        asm.add_label(false_label)
        if len(false_ops):
            asm.JMP_REL32(end_label)
            for op in false_ops:
                op.to_asm(asm)
        asm.add_label(end_label)

class DoWhile(SSAOp):
    _counter = 0

    def __init__(self,test,loop_ops):
        self.test = test
        self.loop_ops = loop_ops
        
    def to_asm(self,asm,**kwargs):
        start_label = 'DoWhile:Start:%d' % self._counter
        end_label = 'DoWhilite:End:%d' % self._counter
        self._counter += 1
        asm.add_label(start_label)
        for op in self.loop_ops:
            op.to_asm(asm,break_label=end_label)
        test.to_asm(asm,true_label=start_label)
        asm.add_label(end_label)

def ssa_to_asm(ssa):
    asm = assembler.Assembler()
    for op in ssa:
        op.to_asm(asm)
    return asm



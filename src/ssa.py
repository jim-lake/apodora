
import assembler

class SSAOp(object):
    def __str__(self):
        return "SSA Op: %s: %s" % (type(self),self.__dict__)

class FunctionStart(SSAOp):
    def __init__(self,name):
        self.name = name
    def to_asm(self,asm):
        asm.function_prefix(self.name)

class FunctionEnd(SSAOp):
    def to_asm(self,asm):
        asm.function_cleanup()
        asm.RETQ()

class Return(SSAOp):
    def __init__(self,value):
        self.value = value

    def to_asm(self,asm):
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
    
    def to_asm(self,asm):
        asm.CALL_REL32(self.name)

class SSAVariableOp(SSAOp):
    pass

class ReadMemory(SSAVariableOp):
    def __init__(self,dest,address):
        self.dest = dest
        self.address = address

class WriteMemory(SSAOp):
    def __init__(self,address,value):
        self.address = address
        self.value = value

class CallCFunction(SSAVariableOp):
    def __init__(self,name):
        self.name = name

class CompareEQ(SSAOp):
    def __init__(self,left,right):
        self.left = left
        self.right = right
        
    def to_asm(self,asm,false_label):
        pass

class If(SSAOp):
    _counter = 0

    def __init__(self,test,true_ops,false_ops = []):
        self.test = test
        self.true_ops = true_ops
        self.false_ops = false_ops
    
    def to_asm(self,asm):
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
        

def ssa_to_asm(ssa):
    asm = assembler.Assembler()
    for op in ssa:
        op.to_asm(asm)
    return asm



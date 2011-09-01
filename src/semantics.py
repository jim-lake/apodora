

import ssa
import assembler

TYPE_UNKNOWN = 0
TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_OBJECT = 3

LAYOUT_OBJECT_SIZE = 8 * 5
LAYOUT_OFFSET = {
    'size': 0,
    'parent': 8,
    'last_add_name': 16,
    'last_add_type': 24,
    'unused0': 25,
    'unused6': 31,
    'add_list': 32,
}

EMPTY_OBJECT_SIZE = 8
OBJECT_OFFSET = {
    'layout': 0,    # Pointer to layout for this object
    #'class_id': 8,  # Pointer to class id for this object
}

def sem_to_ssa(sem_object,ssa_list=None):
    if ssa_list is None:
        ssa_list = ssa.SSAList()
    sem_object.to_ssa(ssa_list)
    return ssa_list

def get_premain():
    ops = []
    ops.append( WriteGlobalPointer('__intrinsic__:layout_root',CreateLayoutObject(None)) )
    ops.append( LoadModule('__main__') )
    return Module('__premain__',ops)


class SemOp(object):
    def __str__(self):
        return "%s: %s" % (type(self),self.__dict__)
    
    def to_ssa(self,ssa_list):
        raise NotImplementedError("Semantic OP to SSA not implemented for type: %s" % type(self))


class WriteGlobalPointer(SemOp):
    def __init__(self,label,value):
        self.label = label
        self.value = value
    
    def to_ssa(self,ssa_list):
        value = self.value.to_ssa(ssa_list)
        ssa_list.add(ssa.WriteGlobalPointer,self.label,value)

def _memset(ssa_list,addr,value,size):
    
    start_counter = ssa_list.add(ssa.Immediate,0)
    value_reg = ssa_list.add(ssa.Immediate,value)

    ops = ssa.SSAList()
    ops.add(ssa.WriteMemory,addr,value_reg,offset=start_counter)
    new_counter = ops.add(ssa.Add,start_counter,8)
    start_counter.phi(new_counter)

    compare = ssa.CompareLTE(new_counter,size)
    
    ssa_list.add(ssa.DoWhile,compare,ops)

class Memset(SemOp):
    def __init__(self,addr,value,size):
        self.addr = addr
        self.value = value
        self.size 

class CreateLayoutObject(SemOp):
    def __init__(self,parent):
        self.parent = parent
    
    def to_ssa(self,ssa_list):
        addr = ssa_list.add(ssa.CallCFunction,'debug_malloc',LAYOUT_OBJECT_SIZE)
        _memset(ssa_list,addr,0,LAYOUT_OBJECT_SIZE)
        if self.parent is not None:
            ssa_list.add(ssa.WriteMemory,addr,self.parent,offset=LAYOUT_OFFSET['parent'])
        return addr

class Module(object):
    def __init__(self,name,ops):
        self.name = name
        self.ops = ops

    def to_ssa(self,ssa_list):
        ssa_list.add(ssa.FunctionStart,'module_start:' + self.name)
        for op in self.ops:
            sem_to_ssa(op,ssa_list)
        ssa_list.add(ssa.FunctionEnd)

class Function(object):
    def __init__(self,module,name,ops):
        self.name = module
        self.name = name
        self.ops = ops


class FindObjectProperty(SemOp):
    def __init__(self,obj,property):
        self.obj = obj
        self.property = property

class Store(SemOp):
    def __init__(self,target,value):
        self.target = target
        self.value = value

class StoreGlobal(Store):
    pass

class StoreLocal(Store):
    pass

class Load(SemOp):
    def __init__(self,target,value):
        self.target = target
        self.value = value

class LoadLocal(Load):
    pass
    
class LoadGlobal(Load):
    pass
    
class LoadSmart(Load):
    pass

class Return(SemOp):
    def __init__(self,value):
        self.value = value

    def to_ssa(self,ssa_list):
        ssa_list.add(ssa.Return,self.value)

class LoadModule(SemOp):
    def __init__(self,module):
        self.module = module
    
    def to_ssa(self,ssa_list):
        ssa_list.add(ssa.CallFunction,'module_start:' + self.module)

    

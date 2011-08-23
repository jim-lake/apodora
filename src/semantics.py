

import assembler

class SemTemp(object):
    def __init__(self,semlist,name=None):
        self._name = name
        self._semlist = semlist
    
    def __str__(self):
        return "SemTemp(name=%s)" % self._name

    def load_attr(self,name):
        return self._semlist.load_attr(self,name)

TYPE_UNKNOWN = 0
TYPE_INT = 1
TYPE_FLOAT = 2
TYPE_OBJECT = 3

LAYOUT_OBJECT_SIZE = 8 * 4
LAYOUT_OFFSET = {
    'size': 0,
    'last_add': 8,
    'prev_layout': 16,
    'add_list': 24,
}

class VariableInfo(object):
    def __init__(self,type=TYPE_UNKNOWN):
        self.type = type

class TestCookie(object):
    def __init__(self,is_static,static_value=True):
        self._is_static = is_static
        self._static_value = static_value
    def should_emit_if_body(self):
        if not self._is_static:
            return True
        elif self._static_value:
            return True
        else:
            return False
    def should_emit_else_body(self):
        if not self._is_static:
            return True
        elif self._static_value:
            return False
        else:
            return True
    def is_dynamic(self):
        return not self._is_static

class LabelCookie(object):
    _counter = 0
    def __init__(self,prefix):
        self._prefix = prefix
        self.label = "label:%s:%d" % (prefix,self._counter)
        self._counter += 1

class SemanticList(object):
    
    def __init__(self,module):
        self._module = module
        self._globals = dict()
        self._locals = dict()
        self._asm = assembler.Assembler()
    
    def get_assembler(self):
        return self._asm

    def module_start(self):
        module_start_label = self._module.name + ':__start__'
        self._function_prefix(module_start_label)
        temp = self._create_object()

    def module_end(self):
        self._function_cleanup()
        self._asm.RETQ()
    
    def function_start(self,name):
        function_start_label = self._module.name + ':' + name + ':entry'
        self._function_prefix(function_start_label)
    
    def function_end(self):
        self._function_cleanup()
        self._asm.RETQ()
    
    def premain(self):
        self.function_start('premain')
        assembler.DataSegment.add_pointer('__intrinsic__:layout_root',0)
        temp = self._create_layout()
        self._store_pointer('__intrinsic__:layout_root',temp)
        self._asm.release_reg(temp)
        self._call('__main__:__start__')
        self.function_end()
    
    def _create_layout(self):
        temp = self._malloc(LAYOUT_OBJECT_SIZE)
        self._memset(temp,0,LAYOUT_OBJECT_SIZE)
        return temp

    def _create_object(self):
        pass

    def _memset(self,dest,value,size):
        temp = self._asm.MOV_REG_IMM(value)
        for i in range(0,size,8):
            self._asm.MOV_MEM_REG(dest,temp,offset=i)
        self._asm.release_reg(temp)
        
    def _store_pointer(self,label,pointer):
        temp = self._asm.MOV_REG_ABS64(label)
        self._asm.MOV_MEM_REG(temp,pointer)
        self._asm.release_reg(temp)
    
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
        temp = SemTemp(self,name)
        print "Load Temp: %s" % temp
        return temp
    
    def load_local(self,name):
        pass
    
    def load_smart(self,name):
        pass
        
    def load_attr(self,object,name):
        temp = SemTemp(self,"%s.%s" % (object,name)) 
        print "Load Attribute: %s" % temp
        return temp
    
    def release_temp(self,temp):
        if type(temp) == SemTemp:
            print "Release Temp: %s" % temp
    
    def plus(self,left,right):
        temp = SemTemp(self)
        print "Add: %s=%s + %s" % (temp,left,right)
        return temp
    
    def plus_equals(self,target,increment):
        pass
    
    def return_(self,value):
        print "Return: %s" % value
        if type(value) is int:
            self._asm.MOV_RAX_IMM(value)
        else:
            raise NotImplementedError("Unsupported return value")
        self._function_cleanup()
        self._asm.RETQ()
    
    def cmp_eq(self,left,right):
        print "Compare EQ: %s == %s" % (left,right)
        if type(left) == SemTemp and type(right) == SemTemp:
            self._asm.CMP_REG_REG(left,right)
            return TestCookie(False)
        elif type(left) == int and type(right) == int:
            return TestCookie(True,left == right)
        else:
            raise NotImplementedError("Unsupported cmq_eq")
            
    
    def start_if(self,test_cookie):
        print "Start If"
        cookie = LabelCookie("If")
        if cmp_cookie.is_dynamic():
            self._asm.JNE_REL32(cookie.label)
        return cookie
    
    def end_if(self,cookie):
        print "End If"
        self._asm.add_label(cookie.label)
    
    def _malloc(self,size):
        return self._asm.call_c_function('debug_malloc',size)
    
    def _call(self,label):
        self._asm.CALL_REL32(label)
    
    def _function_prefix(self,label):
        self._asm.add_label(label)
        # Save RBP
        self._asm.PUSHQ_RBP()
        # Make RBP RSP
        self._asm.MOVQ_RBP_RSP()
    
    
    def _function_cleanup(self):
        # Restore RBP
        self._asm.POPQ_RBP()
    
    
    
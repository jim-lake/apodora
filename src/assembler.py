

class AsmTemp(object):
    def __init__(self,name=None):
        self._name = name
        
    def __str__(self):
        return "Temp(name=%s)" % self._name

class Assembler(object):

    _globals = {}

    def store_global(self,target,source):
        print "Store Global: %s=%s" % (target,source)
    
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
    
    

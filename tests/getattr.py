
# Get attribute

class A(object):
    foo = "class A, foo"
        
class B(A):
    foo = "class B, foo"

class C(B):
    def __getattribute__(self,name):
        return "class C, __getattribute__(%s)" % name

def object_getattribute(self,name):
    return "object_getattribute(%s)" % name

def class_getattribute(self,name):
    return "class_getattribute(%s)" % name


if __name__ == '__main__':
    a = A()
    print "a.foo = " + a.foo
    b = B()
    print "b.foo = " + b.foo
    c = C()
    print "c.foo = " + c.foo

    b2 = B()
    print "1. b2.foo = " + b2.foo
    b2.__getattribute__ = object_getattribute
    print "2. b2.foo = " + b2.foo

    b3 = B()
    print "1. b3.foo = " + b3.foo
    B.__getattribute__ = class_getattribute
    print "2. b3.foo = " + b3.foo



# Method Resolution Order Tests

class A:
    def method1(self):
        return "Class A, method1"
        
class B(A):
    def method1(self):
        return "Class B, method1"
        
def object_method1(self):
    return "object_method1"
    
def class_method1(self):
    return "class_method1"


if __name__ == '__main__':
    a = A()
    print "a.method1() = " + a.method1()
    b = B()
    print "b.method1() = " + b.method1()
    
    b2 = B()
    b2.method1 = object_method1
    print "b2.method1(b2) = " + b2.method1(b2)
    
    b3 = B()
    B.method1 = lambda this: "Class B Runtime, method1"
    print "b3.method1() = " + b3.method1()


    
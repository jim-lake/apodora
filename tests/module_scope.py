
x = 1

if True:
    y = 2
else:
    z = 3

def func():
    #print "  vars = ", vars()
    #print "  globals = ", globals()
    
#    exec('y = 22')

    print "  vars = ", vars()
    print "  globals = ", globals()
    
    print "  x = ", x
    print "  y = ", y

    exec('y = 22')
    
    print "  vars = ", vars()
    print "  globals = ", globals()

    print "  x = ", x
    print "  y = ", y

    

print "x = ", x
print "y = ", y

func()

print "x = ", x
print "y = ", y

if 'z' in vars():
    print "z = ", z

print "vars = ", vars()
print "globals = ", globals()


# Compiler Support

CLASS_LAYOUT_SIZE = 8 + 8



@__intrinsic__.staticfunction
def add_property_to_object(object,name_type_hash,value):
    class_layout = __intrinsic__.load_object_offset(object,0)
    object_size = __intrinsic__.load_object_offset(class_layout,0)
    object_adds = __intrinsic__.load_object_offset(class_layout,8)
    num_adds = __intrinsic__.load_object_offset(object_adds,0)
    num = 0
    next_class = None
    while num < num_adds:
        add = __intrinsic__.load_object_offset(object_adds,num * 16 + 8)
        if add == name_type_hash:
            next_class = __intrinsic__.load_object_offset(object_adds * 16 + 16)
            break
    
    if next_class is None:
        next_class_adds = __intrinsic__.malloc(8)
        __intrinsic__.write_object_offset(next_class_adds,0,0)

        next_class = __intrinsic__.malloc(CLASS_LAYOUT_SIZE)
        __intrinsic__.write_object_offset(next_class,0,object_size + 8)
        __intrinsic__.write_object_offset(next_class,8,next_class_adds)
        
        new_adds = __intrinsic__.malloc(num_adds * 16 + 8 + 16)
        __intrinsic__.memcpy(new_adds,object_adds,num_adds * 16 + 8)
        __intrinsic__.write_object_offset(new_adds,0,new_adds + 1)
        __intrinsic__.write_object_offset(new_adds,num_adds * 16 + 8,name_type_hash)
        __intrinsic__.write_object_offset(new_adds,num_adds * 16 + 8 + 8,next_class)
        
    new_object = __intrinsic__.malloc(object_size + 8)
    __intrinsic__.memcpy(new_object,object,object_size)
    __intrinsic__.write_object_offset(new_object,0,next_class)
    __intrinsic__.write_object_offset(new_object,object_size,value)
    return new_object

# Compiler Support

LAYOUT_OBJECT_SIZE = 8*5
LAYOUT_OFFSET_SIZE = 0
LAYOUT_OFFSET_PARENT = 8
LAYOUT_OFFSET_LAST_ADD_HASH = 16


EMPTY_OBJECT_SIZE = 8
OBJECT_OFFSET_LAYOUT = 0

@__intrinsic__.staticfunction
def create_layout():
    temp = __intrinsic__.malloc(LAYOUT_OBJECT_SIZE)
    __intrinsic__.memset(temp,0,LAYOUT_OBJECT_SIZE)
    __intrinsic__.write_object64(temp,LAYOUT_OFFSET_SIZE,EMPTY_OBJECT_SIZE)
    return temp

@__intrinsic__.staticfunction
def create_object():
    temp = __intrinsic__.malloc(EMPTY_OBJECT_SIZE)
    __intrinsic__.write_object64(temp,OBJECT_OFFSET_LAYOUT,EMPTY_OBJECT_SIZE)

@__intrinsic__.staticfunction
def find_property(obj,name_hash,type):
    layout = __intrinsic__.load_object64(obj,OBJECT_OFFSET_LAYOUT)
    while True:
        last_add_hash = __intrinsic__.load_object64(obj,LAYOUT_OFFSET_LAST_ADD_HASH)
        if last_add_hash == name_hash:
            offset = __intrinsic__.load_object64(obj,LAYOUT_OBJECT_SIZE)
            return offset - 8
        layout = __intrinsic__.load_object64(obj,LAYOUT_OFFSET_PARENT)
        if layout == 0
            return layout


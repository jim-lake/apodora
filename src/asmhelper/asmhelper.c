// asmhelper to run some memory
// Note: Dangerous!

#include <Python.h>

#include <dlfcn.h>
#include <sys/mman.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>

const size_t PAGE_SIZE = 4096;

static PyObject *alloc_memory(PyObject *self,PyObject *args);
static PyObject *write_memory(PyObject *self,PyObject *args);
static PyObject *run_memory(PyObject *self,PyObject *args);
static PyObject *get_symbol_address(PyObject *self,PyObject *args);
PyMODINIT_FUNC initasmhelper(void);

void *debug_malloc(size_t s);
long mytest_function(void);

typedef long (*user_func_t)(void);

static void *g_pointers[256];
static int g_num_pointers = 0;


static PyObject *alloc_memory(PyObject *self,PyObject *args)
{
    static bool once = true;
    if( once )
    {
        once = false;
        memset(g_pointers,0,sizeof(g_pointers));
    }
    size_t len = 0;
    if( !PyArg_ParseTuple(args,"k",&len) )
		return NULL;
    
    const size_t alloc_size = (len / PAGE_SIZE + 1) * PAGE_SIZE; 
    printf("valloc(%ld)\n",alloc_size);
    void *p = valloc(alloc_size);
    g_pointers[g_num_pointers++] = p;
    printf("Return address: 0x%016lx\n",(unsigned long)p);
    PyObject *obj = PyInt_FromSize_t((size_t)p);
	return obj;
}

static PyObject *write_memory(PyObject *self,PyObject *args)
{
    unsigned long pointer_long = 0;
    int len = 0;
	const char *pdata_block = NULL;
    
    if( !PyArg_ParseTuple(args,"kt#",&pointer_long,&pdata_block,&len) )
		return NULL;
    
    void *p = (void *)pointer_long;

    printf("Write data to 0x%016lx, len: %d\n",(unsigned long)p,len);
    memcpy(p,pdata_block,len);
    
    Py_INCREF(Py_None);
    return Py_None; 
}

static PyObject *run_memory(PyObject *self,PyObject *args)
{
	int len = 0;
	const char *pasm_block = NULL;

	if( !PyArg_ParseTuple(args,"t#",&pasm_block,&len) )
		return NULL;

    const size_t exec_size = (len / PAGE_SIZE + 1) * PAGE_SIZE; 

    void *pexec_block = valloc(exec_size);
	memcpy(pexec_block,pasm_block,len);
    mprotect(pexec_block,exec_size,PROT_READ|PROT_EXEC|PROT_WRITE);
    printf("pexec_block: %016lx\n",(unsigned long)pexec_block);

    // Here's where we run something
    user_func_t pfunc = (user_func_t)pexec_block;
    long i = 0;
    i = pfunc();
    //i = mytest_function();
    printf("Got return in C: %ld\n",i);
    PyObject *obj = PyInt_FromLong(i);
	return obj;
}

long mytest_function(void)
{
    malloc(1);
    return 0;
}
void *debug_malloc(size_t s)
{
    printf("debug_malloc(%ld)\n",s);
    return malloc(s);
}


static PyObject *get_symbol_address(PyObject *self,PyObject *args)
{
	char *symbol_name = NULL;
	if( !PyArg_ParseTuple(args,"s",&symbol_name) )
		return NULL;

    printf("get_symbol_address(%s)\n",symbol_name);
	void *symbol_addr = dlsym(RTLD_DEFAULT,symbol_name);
    printf("symbol_addr: %016lx\n",(unsigned long)symbol_addr);
	if( symbol_addr == NULL )
    {
        printf("Symbol not found!\n");
		Py_INCREF(Py_None);
        return Py_None;
	}
	//return Py_BuildValue("K",(unsigned long)symbol_addr);
    PyObject *obj = PyInt_FromSize_t((size_t)symbol_addr);
	return obj;
}

static PyMethodDef asmhelper_methods[] = 
{
    {"alloc_memory",alloc_memory, METH_VARARGS,
    "Allocate a block of memory"},
    
    {"write_memory",write_memory, METH_VARARGS,
    "Write to an allocted block of memory"},

	{"run_memory",run_memory, METH_VARARGS,
    "Run a chuck of memory"},
    
	{"get_symbol_address",get_symbol_address, METH_VARARGS,
	"Get an address of a symbol from a shared library or executable"},

    {NULL, NULL, 0, NULL}        // Sentinel
};

PyMODINIT_FUNC initasmhelper(void)
{
    PyObject *module = NULL;
    module = Py_InitModule("asmhelper",asmhelper_methods);
    
}

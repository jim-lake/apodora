// asmhelper to run some memory
// Note: Dangerous!

#include <Python.h>

#include <dlfcn.h>
#include <sys/mman.h>
#include <errno.h>
#include <string.h>
#include <stdio.h>

const size_t PAGE_SIZE = 4096;

static PyObject *run_memory(PyObject *self,PyObject *args);
static PyObject *get_symbol_address(PyObject *self,PyObject *args);
PyMODINIT_FUNC initasmhelper(void);

int mytest_function(void);

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

    // Here's where we run something

    mytest_function();

	Py_INCREF(Py_None);
	return Py_None;
}

int mytest_function(void)
{
    return -42;
}


static PyObject *get_symbol_address(PyObject *self,PyObject *args)
{
	char *symbol_name = NULL;
	if( !PyArg_ParseTuple(args,"s",&symbol_name) )
		return NULL;

	void *symbol_addr = dlsym(RTLD_DEFAULT,symbol_name);
	if( symbol_addr == NULL )
    {
		Py_INCREF(Py_None);
        return Py_None;
	}

	return Py_BuildValue("K",(unsigned long long)symbol_addr);
}

static PyMethodDef asmhelper_methods[] = 
{
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

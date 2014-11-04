#include "python2.7/Python.h"

static PyObject* diffuse( PyObject *self, PyObject *arg)
{
    char *patten;
    char *string;
    int tmp;
    int index;
    int last;
    int ret;
    if( !PyArg_ParseTuple(arg, "ss", &patten, &string ))
    {
        return NULL;
    }
    if ( (*patten) == '!' )
    {
        if( strcmp(patten +1, string) )
        {
            return (PyObject*)Py_BuildValue("i", 0);
        }
        else
        { 
            return (PyObject*)Py_BuildValue("i", -1);
        }
    }
    ret = 0;
    index = 0;
    last = 0;

    while( *string )
    {
        tmp = *patten - *string;
        if ( tmp == 32 || tmp == 0 )
        {
            patten++;
            ret = index - last + ret;
            if ( 0== *patten)
            {
                return (PyObject*)Py_BuildValue("i", ret);
            }
        }
        string++;
        index ++;
    }
    return (PyObject*)Py_BuildValue("i", -1);

}
static PyMethodDef fuzzy_methods[  ] = { 
    { "diffuse", (PyCFunction)diffuse, METH_VARARGS , NULL },
    { NULL, NULL, 0, NULL }
};


PyMODINIT_FUNC initfuzzy( )
{
    //printf( "IMPORT FUZZY\n");
    Py_InitModule( "fuzzy", fuzzy_methods);
}

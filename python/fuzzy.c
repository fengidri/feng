#include "Python.h"

static PyObject* diffuse( PyObject *self, PyObject *arg)
{
    char *patten;
    char *string;
    int tmp;
    if( !PyArg_ParseTuple(arg, "ss", &patten, &string ))
    {
        return NULL;
    }
    if ( (*patten) == '!' )
    {
        if( strcmp(patten +1, string) )
        {
            Py_RETURN_TRUE;
        }
        else
        { 
            Py_RETURN_FALSE;
        }
    }
    while( *string )
    {
        tmp = *patten - *string;
        if ( tmp == 32 || tmp == 0 )
        {
            patten++;
            if ( 0== *patten)
            {
                Py_RETURN_TRUE;
            }
        }
        string++;
    }
    Py_RETURN_FALSE;

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

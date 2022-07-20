#include <Python.h>

static PyObject* numSplit(PyObject* self, PyObject* args)
{
    unsigned long long number;
    if (!PyArg_ParseTuple(args, "K", &number))
        return NULL;
    PyObject* result = PyList_New(0);
    while (number)
    {
        unsigned long long tmp = number & (0 - number);
        PyObject* pyTmp = PyLong_FromUnsignedLongLong(tmp);
        PyList_Append(result, pyTmp);
        number -= tmp;
    }
    return result;
}

static PyObject* getPower(PyObject* self, PyObject* args)
{
    unsigned long long number;
    if (!PyArg_ParseTuple(args, "K", &number))
        return NULL;
    unsigned long counter = 0;
    while (number)
    {
        number >>= 1;
        ++counter;
    }
    return PyLong_FromUnsignedLong((unsigned long)(64 - counter));
}

static PyObject* getBitsCount(PyObject* self, PyObject* args)
{
    unsigned long long number;
    if (!PyArg_ParseTuple(args, "K", &number))
        return NULL;
    unsigned long counter = 0;
    while (number)
    {
        if (number & 1)
        {
            ++counter;
        }
        number >>= 1;
    }
    return PyLong_FromUnsignedLong(counter);
}

static PyMethodDef TestDLL_methods[] = {
    { "numSplit", (PyCFunction)numSplit, METH_VARARGS, "Splits a number into a sum of powers of 2"},
    { "getPower", (PyCFunction)getPower, METH_VARARGS, "Gets a number of the most right bit. Works with 64 bit variables. The most left bit is 0 the most right is 63"},
    { "getBitsCount", (PyCFunction)getBitsCount, METH_VARARGS, "Counts set bits in given number"},
    { NULL, NULL, 0, NULL }
};

static PyModuleDef TestDLL_module = {
    PyModuleDef_HEAD_INIT,
    "TestDLL",
    "Provides some fast functions to work with bitboards",
    -1,
    TestDLL_methods
};

PyMODINIT_FUNC PyInit_TestDLL() {
    return PyModule_Create(&TestDLL_module);
}

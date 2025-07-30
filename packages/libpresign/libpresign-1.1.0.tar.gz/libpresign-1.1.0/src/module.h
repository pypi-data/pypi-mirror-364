#ifndef S3PRESIGNPYTHON_MODULE_H
#define S3PRESIGNPYTHON_MODULE_H


#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "iostream"
#include "presign.h"

extern "C" {
    static PyObject *
            get(PyObject * self, PyObject * args, PyObject * kwargs);

    static PyMethodDef SpamMethods[] =
            {
                    // ...
                    {"get", (PyCFunction) get, METH_VARARGS | METH_KEYWORDS, "practice kwargs"},
                    {NULL, NULL, 0, NULL}
                    // ...
            };

    static struct PyModuleDef LibPresign = {
            PyModuleDef_HEAD_INIT,
            "libpresign",
            "Package that just pre-signs",
            -1,
            SpamMethods,
    };

    PyMODINIT_FUNC PyInit_libpresign(void) {
        return PyModule_Create(&LibPresign);
    }
}
#endif //S3PRESIGNPYTHON_MODULE_H

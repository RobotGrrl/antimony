#ifndef FAB_H
#define FAB_H

#include <Python.h>

namespace fab
{
    struct ParseError {};

    /** Callback that raises a Python runtime exception. */
    void onParseError(ParseError const& e);

    /** Loads the fab module in Python's namespace.
     *
     *  Must be called before Py_Initialize().
     */
    void preInit();

    /** Evaluates shapes.py and adds to the fab module.
     *
     *  Must be called after Py_Initialize().
     */
    void postInit();

    extern PyTypeObject* ShapeType;
}

#endif // FAB_H
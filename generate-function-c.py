#   Copyright 2011, 2012 David Malcolm <dmalcolm@redhat.com>
#   Copyright 2011, 2012 Red Hat, Inc.
#
#   This is free software: you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see
#   <http://www.gnu.org/licenses/>.

from cpybuilder import *
from wrapperbuilder import PyGccWrapperTypeObject

cu = CompilationUnit()
cu.add_include('gcc-python.h')
cu.add_include('gcc-python-wrappers.h')
cu.add_include('gcc-plugin.h')
cu.add_include("function.h")
cu.add_include("proposed-plugin-api/gcc-function.h")

modinit_preinit = ''
modinit_postinit = ''

def generate_function():
    #
    # Generate the gcc.Function class:
    #
    global modinit_preinit
    global modinit_postinit
    cu.add_defn("\n"
                "static PyObject *\n"
                "gcc_Function_get_cfg(struct PyGccFunction *self, void *closure)\n"
                "{\n"
                "    return gcc_python_make_wrapper_cfg(gcc_function_get_cfg(self->fun));\n"
                "}\n"
                "\n")
    getsettable = PyGetSetDefTable('gcc_Function_getset_table',
                                   [PyGetSetDef('cfg', 'gcc_Function_get_cfg', None,
                                                'Instance of gcc.Cfg for this function (or None for early passes)'),
                                    ],
                                   identifier_prefix='gcc_Function',
                                   typename='PyGccFunction')
    getsettable.add_simple_getter(cu,
                                  'decl', 
                                  'gcc_python_make_wrapper_tree(gcc_private_make_tree(self->fun.inner->decl))',
                                  'The declaration of this function, as a gcc.FunctionDecl instance')
    getsettable.add_simple_getter(cu,
                                  'local_decls',
                                  'VEC_tree_as_PyList(self->fun.inner->local_decls)',
                                  "List of gcc.VarDecl for the function's local variables")
    getsettable.add_simple_getter(cu,
                                  'funcdef_no',
                                  'gcc_python_int_from_long(gcc_function_get_index(self->fun))',
                                  'Function sequence number for profiling, debugging, etc.')
    getsettable.add_simple_getter(cu,
                                  'start',
                                  'gcc_python_make_wrapper_location(gcc_function_get_start(self->fun))',
                                  'Location of the start of the function')
    getsettable.add_simple_getter(cu,
                                  'end',
                                  'gcc_python_make_wrapper_location(gcc_function_get_end(self->fun))',
                                  'Location of the end of the function')
    cu.add_defn(getsettable.c_defn())

    pytype = PyGccWrapperTypeObject(identifier = 'gcc_FunctionType',
                          localname = 'Function',
                          tp_name = 'gcc.Function',
                          tp_dealloc = 'gcc_python_wrapper_dealloc',
                          struct_name = 'PyGccFunction',
                          tp_new = 'PyType_GenericNew',
                          tp_repr = '(reprfunc)gcc_Function_repr',
                          tp_str = '(reprfunc)gcc_Function_repr',
                          tp_getset = getsettable.identifier,
                                    )
    cu.add_defn(pytype.c_defn())
    modinit_preinit += pytype.c_invoke_type_ready()
    modinit_postinit += pytype.c_invoke_add_to_module()

generate_function()

cu.add_defn("""
int autogenerated_function_init_types(void)
{
""" + modinit_preinit + """
    return 1;

error:
    return 0;
}
""")

cu.add_defn("""
void autogenerated_function_add_types(PyObject *m)
{
""" + modinit_postinit + """
}
""")



print(cu.as_str())

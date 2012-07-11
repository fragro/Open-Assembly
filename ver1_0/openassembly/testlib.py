import os, sys, pdb, imp, re, inspect
from django.contrib.admin import site
from django.template import add_to_builtins


def get_module_list(start):
    all_files = os.walk(start)
    file_list = [(i[0], (i[1], i[2])) for i in all_files]
    file_dict = dict(file_list)

    curr = start
    modules = []
    pathlist = []
    pathstack = [[start]]

    while pathstack is not None:

        current_level = pathstack[len(pathstack)-1]
        if len(current_level) == 0:
            pathstack.pop()

            if len(pathlist) == 0:
                break
            pathlist.pop()
            continue
        pathlist.append(current_level.pop())
        curr = os.sep.join(pathlist)

        local_files = []
        for f in file_dict[curr][1]:
            if f.endswith(".py") and os.path.basename(f) not in ('tests.py', 'models.py'):
                local_file = re.sub('\.py$', '', f)
                local_files.append(local_file)

        for f in local_files:
            # This is necessary because all of the imports are repopulating the registry
            site._registry.clear()
            module = imp.load_module(f, *imp.find_module(f, [curr]))
            modules.append(module)

        pathstack.append([sub_dir for sub_dir in file_dict[curr][0] if sub_dir[0] != '.'])

    return modules


def get_doc_objs(module):
    ret_val = []
    for obj_name in dir(module):
        obj = getattr(module, obj_name)
        if callable(obj):
            ret_val.append(obj_name)
        if inspect.isclass(obj):
            ret_val.append(obj_name)

    return ret_val


def has_doctest(docstring):
    return ">>>" in docstring


def get_test_dict(package, locals):
    test_dict = {}
    for module in get_module_list(os.path.dirname(package.__file__)):
        for method in get_doc_objs(module):
            docstring = str(getattr(module, method).__doc__)
            if has_doctest(docstring):

                print "Found doctests(s) " + module.__name__ + '.' + method

                # import the method itself, so doctest can find it
                _temp = __import__(module.__name__, globals(), locals, [method])
                locals[method] = getattr(_temp, method)

                # Django looks in __test__ for doctests to run. Some extra information is
                # added to the dictionary key, because otherwise the info would be hidden.
                test_dict[method + "@" + module.__file__] = getattr(module, method)

    return test_dict


class TestPdb(pdb.Pdb):
    def __init__(self, *args, **kwargs):
        self.__stdout_old = sys.stdout
        sys.stdout = sys.__stdout__
        pdb.Pdb.__init__(self, *args, **kwargs)
        sys.stdout = self.__stdout_old

    def cmdloop(self, *args, **kwargs):
        sys.stdout = sys.__stdout__
        retval = pdb.Pdb.cmdloop(self, *args, **kwargs)
        sys.stdout = self.__stdout_old

def pdb_trace():
    debugger = TestPdb(stdin=sys.__stdin__, stdout=sys.__stdout__)
    debugger.set_trace(sys._getframe().f_back)

def pdb_test():
    debugger = TestPdb()
    debugger.set_trace(sys._getframe().f_back)


# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring



import time as _time



class BuiltIn():
    NoneType = type(None)
    NotImplementedType = type(NotImplemented)
    builtin_function_or_method = type(print)
    function = type(lambda: None)
    
    def __init__(self):
        pass
    
    def __getattr__(self, key):
        return getattr(self, key)



class _DataTransmitor():
    def __init__(self, instance):
        self.className = type(instance).__name__
        self.ldata = args
        self.mdata = kwargs



class BaseObject():
    def __init__(self, *_0, **_1):
        self._createdTime = str(round(_time.time(), 4))
        self._classNameOfSelf = f"{__name__}.{type(self).__name__}"
    
    def __repr__(self):
        return f"<class {self._classNameOfSelf} created at {self._createdTime}>"
    
    def __bool__(self):
        return True



class Number(BaseObject):
    pass



class Null(BaseObject):
    def __repr__(self):
        return f"<class {self._classNameOfSelf}>"
    
    def __bool__(self):
        return False

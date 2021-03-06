# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.8
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.





from sys import version_info
if version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_librainbow', [dirname(__file__)])
        except ImportError:
            import _librainbow
            return _librainbow
        if fp is not None:
            try:
                _mod = imp.load_module('_librainbow', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _librainbow = swig_import_helper()
    del swig_import_helper
else:
    import _librainbow
del version_info
try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.


def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr_nondynamic(self, class_type, name, static=1):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    if (not static):
        return object.__getattr__(self, name)
    else:
        raise AttributeError(name)

def _swig_getattr(self, class_type, name):
    return _swig_getattr_nondynamic(self, class_type, name, 0)


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except AttributeError:
    class _object:
        pass
    _newclass = 0



def rainbow_getNumberOfSlices(fname: 'char *') -> "int":
    return _librainbow.rainbow_getNumberOfSlices(fname)
rainbow_getNumberOfSlices = _librainbow.rainbow_getNumberOfSlices

def rainbow_getRangeResolution(fname: 'char *') -> "float":
    return _librainbow.rainbow_getRangeResolution(fname)
rainbow_getRangeResolution = _librainbow.rainbow_getRangeResolution

def rainbow_getStartRange(fname: 'char *') -> "float":
    return _librainbow.rainbow_getStartRange(fname)
rainbow_getStartRange = _librainbow.rainbow_getStartRange

def rainbow_getRangeSampling(fname: 'char *') -> "int":
    return _librainbow.rainbow_getRangeSampling(fname)
rainbow_getRangeSampling = _librainbow.rainbow_getRangeSampling

def rainbow_getSliceAngles(fname: 'char *', sliceangles: 'float *', len: 'int') -> "int":
    return _librainbow.rainbow_getSliceAngles(fname, sliceangles, len)
rainbow_getSliceAngles = _librainbow.rainbow_getSliceAngles

def rainbow_getAngleStep(fname: 'char *') -> "float":
    return _librainbow.rainbow_getAngleStep(fname)
rainbow_getAngleStep = _librainbow.rainbow_getAngleStep

def rainbow_getLongitude(fname: 'char *') -> "float":
    return _librainbow.rainbow_getLongitude(fname)
rainbow_getLongitude = _librainbow.rainbow_getLongitude

def rainbow_getLatitude(fname: 'char *') -> "float":
    return _librainbow.rainbow_getLatitude(fname)
rainbow_getLatitude = _librainbow.rainbow_getLatitude

def rainbow_getAltitude(fname: 'char *') -> "float":
    return _librainbow.rainbow_getAltitude(fname)
rainbow_getAltitude = _librainbow.rainbow_getAltitude

def rainbow_getWavelength(fname: 'char *') -> "float":
    return _librainbow.rainbow_getWavelength(fname)
rainbow_getWavelength = _librainbow.rainbow_getWavelength

def rainbow_getBeamwidth(fname: 'char *') -> "float":
    return _librainbow.rainbow_getBeamwidth(fname)
rainbow_getBeamwidth = _librainbow.rainbow_getBeamwidth

def rainbow_getSensorType(fname: 'char *') -> "char **":
    return _librainbow.rainbow_getSensorType(fname)
rainbow_getSensorType = _librainbow.rainbow_getSensorType

def rainbow_getSensorID(fname: 'char *') -> "char **":
    return _librainbow.rainbow_getSensorID(fname)
rainbow_getSensorID = _librainbow.rainbow_getSensorID

def rainbow_getSensorName(fname: 'char *') -> "char **":
    return _librainbow.rainbow_getSensorName(fname)
rainbow_getSensorName = _librainbow.rainbow_getSensorName

def rainbow_getNumberOfAngles(fname: 'char *', slicenum: 'int') -> "int":
    return _librainbow.rainbow_getNumberOfAngles(fname, slicenum)
rainbow_getNumberOfAngles = _librainbow.rainbow_getNumberOfAngles

def rainbow_getScanName(fname: 'char *') -> "char **":
    return _librainbow.rainbow_getScanName(fname)
rainbow_getScanName = _librainbow.rainbow_getScanName

def rainbow_getNumberOfRangeBins(fname: 'char *', slicenum: 'int') -> "int":
    return _librainbow.rainbow_getNumberOfRangeBins(fname, slicenum)
rainbow_getNumberOfRangeBins = _librainbow.rainbow_getNumberOfRangeBins

def rainbow_getSliceDate(fname: 'char *', slicenum: 'int') -> "char **":
    return _librainbow.rainbow_getSliceDate(fname, slicenum)
rainbow_getSliceDate = _librainbow.rainbow_getSliceDate

def rainbow_getSliceTime(fname: 'char *', slicenum: 'int') -> "char **":
    return _librainbow.rainbow_getSliceTime(fname, slicenum)
rainbow_getSliceTime = _librainbow.rainbow_getSliceTime

def rainbow_getSliceDatatype(fname: 'char *', slicenum: 'int') -> "char **":
    return _librainbow.rainbow_getSliceDatatype(fname, slicenum)
rainbow_getSliceDatatype = _librainbow.rainbow_getSliceDatatype

def rainbow_getFixedAngle(fname: 'char *', slicenum: 'int') -> "float *":
    return _librainbow.rainbow_getFixedAngle(fname, slicenum)
rainbow_getFixedAngle = _librainbow.rainbow_getFixedAngle

def rainbow_getStartAngles(fname: 'char *', slicenum: 'int', data: 'float *') -> "long":
    return _librainbow.rainbow_getStartAngles(fname, slicenum, data)
rainbow_getStartAngles = _librainbow.rainbow_getStartAngles

def rainbow_getStopAngles(fname: 'char *', slicenum: 'int', data: 'float *') -> "long":
    return _librainbow.rainbow_getStopAngles(fname, slicenum, data)
rainbow_getStopAngles = _librainbow.rainbow_getStopAngles

def rainbow_getSliceData(fname: 'char *', slicenum: 'int', data: 'float *') -> "long":
    return _librainbow.rainbow_getSliceData(fname, slicenum, data)
rainbow_getSliceData = _librainbow.rainbow_getSliceData

def rainbow_getAntSpeed(fname: 'char *', slicenum: 'int') -> "float *":
    return _librainbow.rainbow_getAntSpeed(fname, slicenum)
rainbow_getAntSpeed = _librainbow.rainbow_getAntSpeed

def rainbow_getNoisePowerZh(fname: 'char *', slicenum: 'int') -> "float":
    return _librainbow.rainbow_getNoisePowerZh(fname, slicenum)
rainbow_getNoisePowerZh = _librainbow.rainbow_getNoisePowerZh

def rainbow_getNoisePowerZv(fname: 'char *', slicenum: 'int') -> "float":
    return _librainbow.rainbow_getNoisePowerZv(fname, slicenum)
rainbow_getNoisePowerZv = _librainbow.rainbow_getNoisePowerZv

def rainbow_getRadarConstanth(fname: 'char *', slicenum: 'int', radarconstants: 'float *', len: 'int') -> "int":
    return _librainbow.rainbow_getRadarConstanth(fname, slicenum, radarconstants, len)
rainbow_getRadarConstanth = _librainbow.rainbow_getRadarConstanth

def rainbow_getRadarConstantv(fname: 'char *', slicenum: 'int', radarconstants: 'float *', len: 'int') -> "int":
    return _librainbow.rainbow_getRadarConstantv(fname, slicenum, radarconstants, len)
rainbow_getRadarConstantv = _librainbow.rainbow_getRadarConstantv

def rainbow_getPulseWidthIndex(fname: 'char *') -> "int":
    return _librainbow.rainbow_getPulseWidthIndex(fname)
rainbow_getPulseWidthIndex = _librainbow.rainbow_getPulseWidthIndex

def rainbow_compressData(nbytesudata: 'unsigned long const', udata: 'unsigned char const *', nbytescdata: 'unsigned long *', cdata: 'unsigned char *') -> "int":
    return _librainbow.rainbow_compressData(nbytesudata, udata, nbytescdata, cdata)
rainbow_compressData = _librainbow.rainbow_compressData

def rainbow_getCompressedDataSize(nbytesudata: 'unsigned long const', nbytescdata: 'unsigned long *') -> "int":
    return _librainbow.rainbow_getCompressedDataSize(nbytesudata, nbytescdata)
rainbow_getCompressedDataSize = _librainbow.rainbow_getCompressedDataSize
class floatp(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, floatp, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, floatp, name)
    __repr__ = _swig_repr

    def __init__(self):
        this = _librainbow.new_floatp()
        try:
            self.this.append(this)
        except Exception:
            self.this = this
    __swig_destroy__ = _librainbow.delete_floatp
    __del__ = lambda self: None

    def assign(self, value: 'float') -> "void":
        return _librainbow.floatp_assign(self, value)

    def value(self) -> "float":
        return _librainbow.floatp_value(self)

    def cast(self) -> "float *":
        return _librainbow.floatp_cast(self)
    __swig_getmethods__["frompointer"] = lambda x: _librainbow.floatp_frompointer
    if _newclass:
        frompointer = staticmethod(_librainbow.floatp_frompointer)
floatp_swigregister = _librainbow.floatp_swigregister
floatp_swigregister(floatp)

def floatp_frompointer(t: 'float *') -> "floatp *":
    return _librainbow.floatp_frompointer(t)
floatp_frompointer = _librainbow.floatp_frompointer

class floatArray(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, floatArray, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, floatArray, name)
    __repr__ = _swig_repr

    def __init__(self, nelements: 'size_t'):
        this = _librainbow.new_floatArray(nelements)
        try:
            self.this.append(this)
        except Exception:
            self.this = this
    __swig_destroy__ = _librainbow.delete_floatArray
    __del__ = lambda self: None

    def __getitem__(self, index: 'size_t') -> "float":
        return _librainbow.floatArray___getitem__(self, index)

    def __setitem__(self, index: 'size_t', value: 'float') -> "void":
        return _librainbow.floatArray___setitem__(self, index, value)

    def cast(self) -> "float *":
        return _librainbow.floatArray_cast(self)
    __swig_getmethods__["frompointer"] = lambda x: _librainbow.floatArray_frompointer
    if _newclass:
        frompointer = staticmethod(_librainbow.floatArray_frompointer)
floatArray_swigregister = _librainbow.floatArray_swigregister
floatArray_swigregister(floatArray)

def floatArray_frompointer(t: 'float *') -> "floatArray *":
    return _librainbow.floatArray_frompointer(t)
floatArray_frompointer = _librainbow.floatArray_frompointer


def malloc_char(*args) -> "char *":
    return _librainbow.malloc_char(*args)
malloc_char = _librainbow.malloc_char

def calloc_char(*args) -> "char *":
    return _librainbow.calloc_char(*args)
calloc_char = _librainbow.calloc_char

def realloc_char(ptr: 'char *', nitems: 'size_t') -> "char *":
    return _librainbow.realloc_char(ptr, nitems)
realloc_char = _librainbow.realloc_char

def free_char(ptr: 'char *') -> "void":
    return _librainbow.free_char(ptr)
free_char = _librainbow.free_char

_librainbow.sizeof_char_swigconstant(_librainbow)
sizeof_char = _librainbow.sizeof_char
# This file is compatible with both classic and new-style classes.



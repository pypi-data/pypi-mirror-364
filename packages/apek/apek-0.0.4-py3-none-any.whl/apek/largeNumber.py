# -*- coding: utf-8 -*-
# pylint: disable=missing-module-docstring



import math as _math
import re as _re
from mpmath import mp as _mp
from . import typing
from ._base import _showArgsError, _checkAndShowParamTypeError



class LargeNumber(typing.Number):
    """
    Handle large numbers through the class.
    
    Attributes:
        base (float): The base part of the number.
        exp (int): The exponent part of the number.
        cfg (dict): The dictionary that stores dispPrec, realPrec, reprUnits_en, and reprUnits_zh.
    
    Methods:
        parseString:
            Convert the LargeNumber instance to a string formatting.
        parseInt:
            Convert the LargeNumber instance to a integer.
        parseFloat:
            Convert the LargeNumber instance to a floating number.
        getBase:
            Get the base of the LargeNumber instance.
        getExp:
            Get the exponent of the LargeNumber instance.
        getConfig:
            Get the specified configuration item or all configuration information.
    """
    
    @staticmethod
    def _parseLargeNumberOrShowError(n):
        _checkAndShowParamTypeError("n", n, (LargeNumber, int, float, _mp.mpf))
        if not isinstance(n, LargeNumber):
            return LargeNumber(n)
        return n
    
    def __init__(
        self,
        base = 0,
        exp = 0,
        *args,
        dispPrec = 4,
        realPrec = 8,
        reprUnits_en = "KMBTPEZY",
        reprUnits_zh = "万亿兆京垓秭穰"
    ):
        """
        Provide parameters "base" and "exp" to create an instance of LargeNumber.
        
        The specific value of LargeNumber is set through "base" and "exp",
        and it also supports setting precision and display unit table.
        
        Args:
            base (int or float or LargeNumber, optional):
                "base" is used to control the base part of LargeNumber, that is the "X" in "XeY",
                and its range will be automatically calibrated to [1, 10).
                The corresponding "exp" will be modified.
                The default is 0.
            exp (int or LargeNumber, optional):
                "exp" is used to control the exponent part of LargeNumber, that is the "Y" in "XeY".
                The default is 0.
            dispPrec (int, optional):
                Keyword argument.
                Controls the decimal precision when displaying.
                Parts below the precision will be automatically rounded.
                It cannot be greater than "realPrec" and cannot be negative.
                The default is 4.
            realPrec (int, optional):
                Keyword argument.
                Controls the decimal precision during actual calculations.
                Parts below the precision will be discarded.
                It cannot be less than "dispPrec" and cannot be negative.
                The default is 8.
            reprUnits_en (str or list or tuple, optional):
                Keyword argument.
                Controls the English units used for the exponent part when converting a LargeNumber instance with a large "exp" to a string.
                When accepting a str, each character is treated as a unit.
                When accepting a list or tuple, each item is treated as a unit.
                The units are ordered from smallest to largest from the beginning to the end.
                The iterable object must not be empty.
            reprUnits_zh (str or list or tuple, optional):
                Keyword argument.
                Controls the Chinese units used for the exponent part when converting a LargeNumber instance with a large "exp" to a string.
                When accepting a str, each character is treated as a unit.
                When accepting a list or tuple, each item is treated as a unit.
                The units are ordered from smallest to largest from the beginning to the end. The iterable object must not be empty.
        
        Returns:
            None
        
        Raises:
            TypeError: A TypeError will be thrown when the number or type of the accepted arguments is incorrect.
            ValueError: A ValueError will be thrown when the value of the accepted arguments is incorrect.
        """
        if args:
            _showArgsError(args)
        _checkAndShowParamTypeError("base", base, (int, float, str, _mp.mpf))
        _checkAndShowParamTypeError("exp", exp, (int, str, _mp.mpf))
        if isinstance(exp, _mp.mpf):
            exp = int(exp)
        super().__init__()
        cfg = {}
        _checkAndShowParamTypeError("dispPrec", dispPrec, int)
        if dispPrec < 0:
            raise ValueError("The parameter 'dispPrec' cannot be less than 0.")
        cfg["dispPrec"] = dispPrec
        _checkAndShowParamTypeError("realPrec", realPrec, int)
        if realPrec < 0:
            raise ValueError("The parameter 'realPrec' cannot be less than 0.")
        if realPrec > 999999:
            raise ValueError("The parameter 'realPrec' is too large.")
        if realPrec < dispPrec:
            raise ValueError("The parameter 'realPrec' cannot be less than parameter 'dispPrec'.")
        cfg["realPrec"] = realPrec
        _checkAndShowParamTypeError("reprUnits_en", reprUnits_en, (list, tuple, str))
        if not reprUnits_en:
            raise ValueError(f"The paramter 'reprUnits_en' cannot be empty {type(reprUnits_en).__name__}.")
        cfg["reprUnits_en"] = reprUnits_en
        _checkAndShowParamTypeError("reprUnits_zh", reprUnits_zh, (list, tuple, str))
        if not reprUnits_zh:
            raise ValueError(f"The paramter 'reprUnits_zh' cannot be empty {type(reprUnits_zh).__name__}.")
        cfg["reprUnits_zh"] = reprUnits_zh
        self.config = cfg
        
        self.base = self._toMpf(base)
        self.exp = exp
        self.calibrate()
    
    
    def getBase(self, *args):
        """
        Get the base.
        
        Returns:
            float: The base.
        """
        
        if args:
            _showArgsError(args)
        return _mp.mpf(self.base)
    
    def setBase(self, base, *args):
        """
        Set the base.
        
        Returns:
            None
        """
        
        if args:
            _showArgsError(args)
        _checkAndShowParamTypeError("base", base, (int, float, str, _mp.mpf))
        self.base = _mp.mpf(base) if not isinstance(base, _mp.mpf) else base
    
    def getExp(self, *args):
        """
        Get the exponent.
        
        Returns:
            int: The exponent.
        """
        
        if args:
            _showArgsError(args)
        return int(self.exp)
    
    def setExp(self, exp, *args):
        """
        Set the exponent.
        
        Returns:
            None
        """
        
        if args:
            _showArgsError(args)
        _checkAndShowParamTypeError("exp", exp, (int, str))
        self.exp = int(exp) if not isinstance(exp, int) else exp
    
    def getConfig(self, key=None, *args):
        """
        Get the configs.
        
        Returns:
            dict: The configs.
        """
        
        if args:
            _showArgsError(args)
        _checkAndShowParamTypeError("key", key, (str, typing.BuiltIn.NoneType))
        if key is None:
            return self.config
        return self.config.get(key)
    
    def setConfig(self, key=None, value=None, *args):
        """
        Set the configs.
        
        Returns:
            None
        """
        
        if args:
            _showArgsError(args)
        _checkAndShowParamTypeError("key", key, (str, typing.BuiltIn.NoneType))
        _checkAndShowParamTypeError("key", key, (str, int, float, dict, list, tuple))
        if key is None:
            self.config = value
        self.config[key] = value
    
    def _toMpf(self, base):
        if isinstance(base, _mp.mpf):
            return base
        with _mp.workdps(self.getConfig("realPrec")):
            return _mp.mpf(str(base))
    
    def calibrate(self):
        "Calibrate the instance."
        
        rawBase, rawExp = self.base, self.exp
        
        if rawBase == 0:
            self.base = _mp.mpf(0)
            self.exp = 0
            return
        
        isNeg = True if rawBase < 0 else False
        absBase = abs(rawBase)
        
        expOfBase = int(_mp.floor(_mp.log10(absBase)))
        exp = rawExp + expOfBase
        calibratedBase = absBase / _mp.power(10, expOfBase)
        
        scale = _mp.power(10, self.getConfig("realPrec") - 1)
        calibratedBase = _mp.floor(calibratedBase * scale) / scale
        
        
        if calibratedBase >= 10:
            calibratedBase /= 10
            exp += 1
        
        self.base = -calibratedBase if isNeg else calibratedBase
        self.exp = exp
    
    def _insertUnit(self, number, mul, units):
        if number < mul:
            return str(number)
        for unit in units:
            number = round(number / mul, self.getConfig("realPrec"))
            if number < mul:
                return f"{number}{unit}"
        return f"{number}{units[-1]}"
    
    def hotCreate(self, base, exp):
        "Hot create an instance."
        
        new = object.__new__(LargeNumber)
        new.base = base
        new.exp = exp
        new.config = self.getConfig()
        new.calibrate()
        return new
    
    def parseString(self, *args, prec="default", expReprMode="none", template="{}e{}", alwaysUseTemplate=False):
        """
        Convert LargeNumber to a string
        
        Args:
            prec (int or "default"):
                Keyword argument.
                The precision of the converted string.
                Defaults to the value of dispPrec.
            expReprMode ("comma" or "byUnit_en" or "byUnit_zh" or "power"):
                Keyword argument.
                Controls the display mode of the exponent.
                Defaults to "comma".
            template (str):
                Keyword argument.
                Controls the template for inserting the base and exponent when converting to a string.
                Defaults to "{}e{}".
            alwaysUseTemplate (bool):
                Keyword argument.
                Controls whether to always use the template.
                Defaults to False.
        
        Returns:
            str: The converted string.
        
        Raises:
            TypeError:
                This error is raised when the number or position of the arguments is incorrect,
                or the argument type is wrong.
        """
        if args:
            _showArgsError(args)
        if prec == "default":
            prec = self.getConfig("dispPrec")
        elif prec == "real":
            prec = self.getConfig("realPrec")
        _checkAndShowParamTypeError("prec", prec, int)
        _checkAndShowParamTypeError("expReprMode", expReprMode, str)
        _checkAndShowParamTypeError("alwaysUseTemplate", alwaysUseTemplate, bool)
        base, exp = self.getBase(), self.getExp()
        if -4 <= exp <= 7 and not alwaysUseTemplate:
            return str(base * _mp.power(10, exp))
        dispBase = str(round(base * _mp.power(10, prec)) / _mp.power(10, prec))
        dispExp = None
        if exp >= 1_000_000_000_000_000 or exp <= -10:
            expReprMode = "power"
        if expReprMode == "comma":
            dispExp = f"{exp:,}"
        elif expReprMode == "none":
            dispExp = str(exp)
        elif expReprMode == "byUnit_en":
            dispExp = self._insertUnit(exp, 1000, self.getConfig("reprUnits_en"))
        elif expReprMode == "byUnit_zh":
            dispExp = self._insertUnit(exp, 10000, self.getConfig("reprUnits_zh"))
        elif expReprMode == "power":
            dispExp = str(LargeNumber(exp, 0))
        else:
            raise ValueError(f"Invalid expReprMode: {repr(expReprMode)}")
        return template.format(dispBase, dispExp)
    
    def parseInt(self, *args, mode="default"):
        """
        Convert the string to an integer.
        
        Args:
            mode (str):
                Keyword argument.
                Controls the behavior when converting to an integer.
                In "default" mode, it will be directly converted to an integer.
                In "power N" mode, when the exponent is greater than N, an error will be thrown, using only "power" defaults to "power 128".
        
        Returns:
            int:
                The converted integer.
        
        Raises:
            OverflowError:
                This error is raised when the exponent exceeds the specified range of power,
                or the limits of Python.
            ValueError:
                This error will be thrown when an unknown conversion mode is accepted.
        """
        if args:
            _showArgsError(args)
        _checkAndShowParamTypeError("mode", mode, str)
        if mode == "default":
            if self.getBase() == 0:
                return 0
            if -4 <= self.getExp() <= 7:
                return int(self.getBase() * _mp.power(10, self.getExp()))
            expSub = self.getExp() - self.getConfig("realPrec")
            base = str(self.getBase())
            if "." in base:
                base = base.replace(".", "")
            expSub -= len(base) - 1
            return int(base + "0" * expSub)
        if mode == "power" or _re.search("^power\\s+\\d{1,6}$", mode):
            if mode == "power":
                mode = "power 128"
            power = int(_re.split("\\s+", mode)[1])
            if self.getExp() > power:
                raise OverflowError(f"The exponent exceeds the allowed upper limit: {power}")
            return self.parseInt(mode="default")
        raise ValueError(f"Invalid mode: {repr(mode)}")
    
    def __str__(self):
        return self.parseString()
    
    def __bool__(self):
        if self.getBase() == 0 and self.getExp() == 0:
            return False
        return True
    
    def __int__(self):
        return self.parseInt()
    
    def __float__(self):
        return float(self.parseString())
    
    def __repr__(self):
        return f"{self.getBase()}e{int(self.getExp()):,}"
    
    def __iter__(self):
        yield self.getBase()
        yield self.getExp()
    
    def __neg__(self):
        return LargeNumber(-self.getBase(), self.getExp())
    
    def __pos__(self):
        return self
    
    def __abs__(self):
        return LargeNumber(abs(self.getBase()), self.getExp())
    
    def __eq__(self, other):
        other = self._parseLargeNumberOrShowError(other)
        return (self.getBase() == other.base) and (self.getExp() == other.exp)
    
    def __ne__(self, other):
        return not self == other
    
    def __lt__(self, other):
        other = self._parseLargeNumberOrShowError(other)
        if self.getExp() != other.exp:
            return self.getExp() < other.exp
        return self.getBase() < other.base
    
    def __le__(self, other):
        return self < other or self == other
    
    def __gt__(self, other):
        return not self <= other
    
    def __ge__(self, other):
        return not self < other
    
    def __add__(self, other):
        other = self._parseLargeNumberOrShowError(other)
        if self == other:
            return self.getBase() + other.base, self.getExp()
        big, small = 0, 0
        if self < other:
            big, small = other, self
        else:
            big, small = self, other
        if big.getExp() - small.getExp() > big.getConfig("realPrec"):
            return big.hotCreate(big.getBase(), big.getExp())
        expSub = big.getExp() - small.getExp()
        bigBase = big.getBase() * _mp.power(10, expSub)
        smallBase = small.getBase()
        return LargeNumber(bigBase + smallBase, small.getExp())
    
    def __radd__(self, other):
        return self + other
    
    def __iadd__(self, other):
        return self + other
    
    def __sub__(self, other):
        return -other + self
    
    def __rsub__(self, other):
        return -self + other
    
    def __isub__(self, other):
        return self - other
    
    def __mul__(self, other):
        if other == 0:
            return LargeNumber(0)
        if isinstance(other, (int, float)):
            new = self.hotCreate(self.getBase() * other, self.getExp())
            new.config = self.getConfig()
            return new
        other = self._parseLargeNumberOrShowError(other)
        return LargeNumber(
            self.getBase() * other.getBase(),
            self.getExp() + other.getExp()
        )
    
    def __rmul__(self, other):
        return self * other
    
    def __imul__(self, other):
        return self * other
    
    def __truediv__(self, other):
        if other == 0:
            raise ZeroDivisionError(f"{repr(self)} cannot be divided by 0.")
        if isinstance(other, (int, float)):
            new = self.hotCreate(self.getBase() / other, self.getExp())
            new.config = self.getConfig()
            return new
        other = self._parseLargeNumberOrShowError(other)
        return LargeNumber(
            self.getBase() / other.base,
            self.getExp() - other.exp
        )
    
    def __rtruediv__(self, other):
        return 1 / self * other
    
    def __itruediv__(self, other):
        return self / other
    
    def parseMpf(self, prec):
        with _mp.workdps(prec):
            return _mp.mpf(self.parseString(prec="real"))

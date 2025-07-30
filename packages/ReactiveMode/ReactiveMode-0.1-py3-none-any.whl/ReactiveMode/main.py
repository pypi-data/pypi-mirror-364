class SimpleEvent:
    """Used To Invoke Functions that don`t have any parameters. _Funcs - private list for storing these functions"""

    _Funcs = []

    def __init__(self, *funcs):
        self._Funcs = list(funcs)
    
    def AddListener(self, func):
        """Adds Function To Executing List (Subscribing)"""
        if func not in self._Funcs:
            self._Funcs.append(func)
    
    def RemoveListener(self, func):
        """Removes Subscriber"""
        if func in self._Funcs:
            self._Funcs.remove(func)
        
    def Invoke(self):
        """Executes All Subscribers"""
        for func in self._Funcs:
            func()

    def ViewSubscribers(self):
        """Prints All Subscribers"""
        for func in self._Funcs:  
            print(func.__name__)

    def GetSubscribers(self):
        """Returns All Subscribers In Tuple"""
        TempSubs = []
        for func in self._Funcs:  
            TempSubs.append(func)
        Subscribers = tuple(TempSubs)
        return Subscribers

    def InvokeSpecific(self, num):
        """Invokes Specific Subscriber By Number"""
        Subscriber = self._Funcs[num]
        Subscriber()






class Event:
    """Main Event Class. Executes All Functions That Have The Same Parameters Count. Also Returning Return Values. If Function Is Not Returning Anything 'None' Will Be Added To The Returning List."""
    PCount = 1
    
    ret: bool = False

    _Subs = []

    _Rets = []
    
    def __init__(self, ret: bool = False, PCount: int = 1):
        self.ret = ret
        self.PCount = PCount

    
    def AddSubscriber(self, func: callable):
        """"""
        if func not in self._Subs:
            self._Subs.append(func)

    def RemoveSubscriber(self, func: callable):
        if func in self._Subs:
            self._Subs.remove(func)

    def Invoke(self, *parameter):
        if len(parameter) != self.PCount:
            raise ValueError(f"Expected {self.param_count} arguments, got {len(parameter)}")
        else:
            if self.ret == True:
                for func in self._Subs:
                    ReturnVal = func(*parameter)
                    self._Rets.append(ReturnVal)
            else:
                for func in self._Subs:
                    func(*parameter)


    def GetReturns(self):
        return self._Rets


    def ViewSubscribers(self):
        for func in self._Subs:
            print(func.__name__)


    def GetSubscribers(self):
        SubsHolder = []
        for func in self._Subs:
            SubsHolder.append(func)
        SubsToReturn = tuple(SubsHolder)
        return SubsToReturn




class AdvancedEvent:
    """Used To Invoke Multiple Functions With Their Custom Parameters. All Functions In This Class Can Have Different Parameters Count."""
    _Subs = []

    _Rets = []

    def AddSubscriber(self, func: callable):
        """Adding Function To Event"""
        if func not in self._Subs:
            self._Subs.append(func)

    def RemoveSubscriber(self, func: callable):
        """Removing Function From Event"""
        if func in self._Subs:
            self._Subs.remove(func)

    def Invoke(self, *prop: tuple):
        """Invoking All Functions. Type The Parameters Of Functions In Tuples. Also Returning All Values In A List If Function Is Returning Anything"""
        for func, params in zip(self._Subs, prop):
            Params: tuple = params
            ret = func(*params)
            self._Rets.append(ret)
        self._Rets = [n for n in self._Rets if n is not None]

    def GetSubscribers(self):
        """Returning All Functions That Are Subsribed To The Event"""
        return self._Subs



#Decorators:

def SimpleEventPoint(*funcs: callable):
    """Exeutes All Functions That Dont Have Any Parameters Or Return Value. Insert Functions That You Want To Execute When You Are Running The Decorated Function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            for f in funcs:
                f()
        return wrapper
    return decorator


def EventPoint(*Tup: tuple):
    """Executes All Functions With Parameters But Not Storing Return Value. To Use It, Add Tuples In Decorator Parameters, Where 1st Element Is Function And Others Are Its Parameters."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            for f in Tup:
                Func : callable = f[0]
                Params: tuple = f[1:]
                Func(*Params)
        return wrapper
    return decorator


class SimplePipeLine:
    """Simple Class For Creating PipeLines. Functions In This Class DO NOT Support Parameters. If You Need To Use Functions With Parameters, Use 'PipeLine' Class"""
    _pipeLineFuncs = []

    def AddFunc(self, func: callable):
        """Add Function To PipeLine"""
        if func not in self._pipeLineFuncs:
            self._pipeLineFuncs.append(func)

    def RemoveFunc(self, func: callable):
        """Remove Function From PipeLine"""
        if func in self._pipeLineFuncs:
            self._pipeLineFuncs.remove(func)

    def Start(self, value: any):
        """To Start The PipeLine, Insert Value In This Method That You Want To Modify With Your PipeLine"""
        val = []
        if self._pipeLineFuncs[0] != None:
            firstF = self._pipeLineFuncs[0]
            process = firstF(value)
            val.append(process)
            for f in self._pipeLineFuncs[1:]:
                r = f(val[0])
                val.clear()
                val.append(r)
            
        return val[0]


    def GetFuncs(self):
        """Returns All The Functions In A List"""
        return self._pipeLineFuncs
            




class PipeLine:
    """Main PipeLine Class. To Start It, Change Current Value With 'ChangeCurrentVal' Method, Then Add Some Functions And Use 'Start' Method With Tuples As Parameters For Your Functions. PipeLines Do Not Store Returning Values."""
    _pipeLineFuncs = []

    _currentVal: any

    def AddFunc(self, func: callable):
        """Add Function To PipeLine"""
        if func not in self._pipeLineFuncs:
            self._pipeLineFuncs.append(func)

    def RemoveFunc(self, func: callable):
        """Remove Function From PipeLine"""
        if func in self._pipeLineFuncs:
            self._pipeLineFuncs.remove(func)

    def ChangeCurrentVal(self, value):
        """Change Current Value Of PipeLine. Current Value Will Be Modified By PipeLine."""
        self._currentVal = value


    def Start(self, *Tup: tuple):
        """Insert Tuples As The Parameters Of Your Functions To Execute The Method And Whole PipeLine."""
        val = []
        if self._pipeLineFuncs[0] != None:
            firstF = self._pipeLineFuncs[0]
            process = firstF(self._currentVal, Tup[0])
            val.append(process)
            for f, p in zip(self._pipeLineFuncs[1:], Tup[1:]):
                r = f(val[0], *p)
                val.clear()
                val.append(r)
            
        return val[0]


    def GetFuncs(self):
        """Returns All The Functions In A List"""
        return self._pipeLineFuncs





class color_out:
    def __init__(self):
        self.color_switch = True

    def on(self):
        self.color_switch = True
    def off(self):
        self.color_switch = False

    def black(self,s):  return self.__color(30, s)
    def red(self,s):    return self.__color(31, s)
    def green(self,s):  return self.__color(32, s)
    def yellow(self,s): return self.__color(33, s)
    def blue(self,s):   return self.__color(34, s)
    def purple(self,s): return self.__color(35, s)
    def white(self,s):  return self.__color(37, s)

    def __color(self, color_int, s):
        if self.color_switch:
            return  "%s[%d;2m%s%s[0m" %(chr(27), color_int, s, chr(27))  
        else:
            return  s
          
    def highlight(self,s):  
        if self.color_switch:
            return  "%s[30;2m%s%s[1m"%(chr(27), s, chr(27))
        else:
            return  s
 

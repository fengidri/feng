# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2015-03-15 17:50:46
#    email     :   fengidri@yeah.net
#    version   :   1.0.1
class Word( object ): 
    "词法对象"
    TEX_CHAR = ['%','#','$','&','{','}', '^', '_', '~', '[', ']', ' ', '\n']
    TEX_CONTROL_CHAR = ['#', '$', '%', '^', '&', '_', '{', '}', '~', '\\']


    TYPE_CONTROL = 1  # 控制序列
    TYPE_PUNC    = 2  # 特殊符号
    TYPE_TEXT    = 3  # 文字
    TYPE_CPUNC   = 4  # 形如\# \$ \% \^ \& \_ \{ \} \~ \\

    def __init__(self, t, l, name, pos):
        self.pos = pos 

        self.len = l   # 长度
        self.type = t   # 对应类型
        self.nm = name


    def name(self):
        return self.nm
           


class Source(object): # 对于souce 进行包装
    def __init__(self, source):
        self.pos = 0
        self.source = source
        self.length = len(source)

    def getchar(self): # 得到当前的char
        if self.pos >= self.length:
            return None
        return self.source[self.pos]

    def update(self): # 记数器+1
        self.pos += 1



class PostionCounter(object): # 计算当前的位置
    def __init__(self, source):
        self.line = 1
        self.col = 0
        self.source = source
        self.col_start = 0

    def update(self, char):
        if char == '\n':
            self.line += 1
            self.col_start = self.source.pos

    def get_pos(self):
        col = self.source.pos - self.col_start
        return (self.line, col, self.source.pos)


def get_control(source, pos):
    length = 1

    name = []
    name.append(source.getchar())

    source.update()
    tp = Word.TYPE_CONTROL

    while source.getchar():
        char = source.getchar()
        if length == 0:
            if char in Word.TEX_CONTROL_CHAR:
                length += 1
                name.append(char)
                source.update()
                tp = Word.TYPE_PUNC
                break
        elif char.islower():
            length+=1
            name.append(char)
            source.update()
            continue
        else:
            break
            # 序列结束
    name = ''.join(name)

    return Word(tp, length, name, pos)

             
class Words(list):# 对于进行词法分析的结果进行包装, 是语法分析中的依赖
    def __init__(self, source):
        list.__init__(self)
        self.pos = 0
        self.source = source # 记录source, 不是source 对象

    def getcontext(self, word): 
        # 依据word 的pos 与length 得到对应的source
        pos = word.pos[2]
        length = word.len
        return self.source[pos: pos + length]

    def get_context_between(self, w1, w2): # 得到两个word 中间的context, 开区间
        s = w1.pos[2] + w1.len
        e = w2.pos[2] 
        return self.source[s: e]

    def find_end_by_name(self, name):
        for index, w in enumerate(self[self.pos:]):
            if w.name() == name:
                pos = self.pos + index + 1
                ws = Words(self.source)
                ws.extend(self[self.pos: pos])
                self.pos = pos
                return ws
        else:
            w = self[self.pos]
            msg = "NOT FOUND:%s from %s, %s" % (name, w.pos[0], w.pos[1])
            raise Exception(msg)

    def find_same(self, name):
        for index, w in enumerate(self[self.pos:]):


            if w.name() != name:
                pos = self.pos + index 
                break
        else:
            pos = self.pos + index  + 1

        ws = Words(self.source)
        ws.extend(self[self.pos: pos])
        self.pos = pos
        return ws

    def slice(self, start, end):
        ws = Words(self.source)
        ws.extend(self[start: end])
        return ws

    def getword(self):
        if self.pos >= len(self):
            return None
        return self[self.pos]

    def update(self):
        self.pos += 1

    def back(self): # 使用要注意
        self.pos -= 1







def split(src): # 对于src 进行词法分解
    source = Source(src)
    poscounter = PostionCounter(source) # 统计当前的行号, 位置信息

    words = Words(src)
    text_pos = poscounter.get_pos()
    
    while True:
        char =  source.getchar()
        if not char : break
        # start

        if char in Word.TEX_CHAR or char == '\\':
            # 处理普通文本
            if text_pos:
                l = poscounter.get_pos()[2] - text_pos[2]
                w = Word(Word.TYPE_TEXT,  l, 'text', text_pos)
                words.append(w)
                text_pos = None

            if char in Word.TEX_CHAR:# 特殊字符

                w = Word(Word.TYPE_PUNC, 1, char, poscounter.get_pos())
                words.append(w)
                poscounter.update(char)  # 更新行
                source.update()


            elif char == '\\': # 控制序列
                w = get_control(source, poscounter.get_pos())
                words.append(w)

                
                # 处理结束的char 不是序列的, 再次进入循环
                continue
        else:
            if text_pos == None:
                text_pos = poscounter.get_pos()
            
            poscounter.update(char)  # 更新行
            source.update()
    return words

def show_word_details(words):
    for w in words:

        name = w.name()
        if w.type == Word.TYPE_PUNC:
            if name == '\n':
                name = '\\n'
            elif name == ' ':
                name = 'space'

        print "%s|%s,%s" % (name, w.pos[0], w.pos[1])


if __name__ == "__main__":
    pass


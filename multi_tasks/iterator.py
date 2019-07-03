from collections import Iterable, Iterator

class Classmate(object):

    def __init__(self):
        self.names = list()
        self.current = 0

    def add(self, name):
        self.names.append(name)

    def __iter__(self):
        return ClassIterator(self)

        # 若返回self，则调用自己类下的__next__()函数
        # return self  
 
    def __next__(self):
        if self.current < len(self.names):
            ret = self.names[self.current]
            self.current += 1
            return ret

        else:
            raise StopIteration 


class ClassIterator(object):

    def __init__(self, obj):
        self.obj = obj
        self.current = 0

    def __iter__(self):
        pass

    def __next__(self):
        if self.current < len(self.obj.names):
            ret = self.obj.names[self.current]
            self.current += 1
            return ret

        else:
            raise StopIteration 

classmate  = Classmate()
classmate.add('Tom')
classmate.add('Jack')
classmate.add('from')
classmate.add('Fred')

for each in classmate:
    print(each)



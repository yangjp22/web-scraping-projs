# coding = 'utf-8'

class FabIterator(object):

    def __init__(self, max_num):
        self.max_num =  max_num
        self.a = 0
        self.b = 1
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):

        if self.current < self.max_num:
            self.a, self.b = self.b, self.a + self.b
            self.current += 1
            return self.a

        else:
            raise StopIteration

fab = FabIterator(10)

for i in fab:
    print(i)
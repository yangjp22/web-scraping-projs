# coding = utf - 8
# 


def create_fab(number):

    a, b = 0, 1
    current = 0

    while current < number:
        a, b = b, a + b
        current += 1
        yield a

fab = create_fab(10)

for i in fab:
    print(i)


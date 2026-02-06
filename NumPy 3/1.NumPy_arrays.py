import numpy as np
# a = [1,2,3,4,5,6,7]
# print(a[3])

a = np.array([1,2,3,4,5,6,7])
print(a)
print(type(a))
print(a[1])
print(a[1:])
print(a[:-2])
a[3] = 45
print(a)

a_mul = np.array([1,2,3],
                 [4,5,6],
                 [7,8,9])
print(a_mul)

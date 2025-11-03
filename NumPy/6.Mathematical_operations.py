import numpy as np 

l1 = [1,2,3,4,5]
l2 = [6,7,8,9,0]

print(l2)
print(l1)
a1 = np.array(l1)
a2 = np.array(l2)

print(l1*5)
print(a1*5)

print(l1+l2)
print(a1+a2)

# print(l1*l2)
print(a1*a2)

a1 = np.array([1,2,3])
a2 = np.array([[1],
              [2]])

print(a1+a2)

a = np.array([[1,2,4],
             [4,5,6],
             [7,8,9]])
print(np.log10(a))
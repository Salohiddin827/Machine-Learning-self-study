import numpy as np

a = np.array([1,2,3])
a = np.append(a,[7,8,9])
a = np.insert(a,3,[4,5,6])

print(a)

a = np.array([[1,2,3],
              [4,5,6],
              ])


#this removes raws
print(np.delete(a,1,0))

#this removes columns
print(np.delete(a,1,1))

import numpy as np

a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6]])

# Concatenate arrays a and b along axis 0
result = np.concatenate((a, b), axis=0)

print(result)

# Now, try to concatenate a and b along axis 1
# (Write the code below to complete this part)

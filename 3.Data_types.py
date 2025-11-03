import numpy as np
d = {'1':'A'}
a = np.array([[1,2,3],
         [4,"Hello",6],
         [7,8,9]], dtype="<U7")


print(a.dtype)
print(a[0][0].dtype)


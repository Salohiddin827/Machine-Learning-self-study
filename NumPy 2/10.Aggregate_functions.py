import numpy as np

a = np.array([[1,2,3,4,5],
              [6,7,8,9,10],
              [11,12,13,14,15],
              [16,17,18,19,20]])
print(a.min())
print(a.max())
print(a.mean())
print(a.std())
print(a.sum())
print(np.median(a))
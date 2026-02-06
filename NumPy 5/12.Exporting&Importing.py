import numpy as np

a = np.array([[1,2,3,4,5,6],
              [7,8,9,10,11,12],
              [13,14,15,16,17,18],
              [19,20,21,22,23]])
np.save("myarray.npy", a)
np.savetxt("myarray.csv",a, delimiter=",")
a = np.load("myarray.npy")
a = np.load("myarray.csv", delimiter=",")
print(a)
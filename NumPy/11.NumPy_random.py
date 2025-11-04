import numpy as np

number = np.random.randint(100)
print(number)

numbers = np.random.randint(90,100,size=(2,3,4))
print(numbers)

numbers1 = np.random.binomial(10, p= 0.5,size=(5,10))
print(numbers1)

number2 = np.random.normal(loc=170, scale=15,size=(5,10))
print(number2)

number3 = np.random.choice([10,20,30,40,50,60],size=(5,10))
print(number3)
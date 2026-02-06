print("Sherxonning kalkulyotoriga Xush kelibsiz!!!")
a = int(input("Birinchi raqamni kiriting: "))
c = input("Amalni kiriting: \n+\n-\n*\n/\n ")
b = int(input("Ikkinchi raqamni kiriting: "))

if c =="+":
    print(f"{a}+{b} = {a+b}")
elif c =="-":
    print(f"{a}-{b} = {a-b}")
if c =="*":
    print(f"{a}*{b} = {a*b}")
if c =="/":
    if b== 0:
        print("0 ga bo'lish mumkin emas ")
    else:
        print(f"{a}/{b} = {a/b}")


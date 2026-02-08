arr1 = [1,2,4,5,9]
arr2 = [2,3,4,23,43]

n = len(arr1)
m = len(arr2)

i = 0
j = 0
result = []
while i<n and j<m:
    if arr1[i]<arr2[j]:
        result.append(arr1[i])
        i +=1
    else:
        result.append(arr2[j])
        j+=1
while i<n:
    result.append(arr1[i])
    i +=1
while j<m:
    result.append(arr2[j])
    j +=1
print(result)

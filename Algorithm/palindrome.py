# word = "aziza"
# if word==word[::-1]:
#     print("Palindrome")
# else:
#     print("not palindrome")
word = "kiyik"
low, high = 0, len(word)-1
while low<high:
    if word[low ]!=word[high]:
        return False

    low+=1
    high-=1

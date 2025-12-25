sen = input("enter the sentence:")

print("Number of characters:",len(sen))

newsen = sen.split()
num_word = len(newsen)
print("Number of words:",num_word)

vowel = "aeiouAEIOU"
count = 0
for ch in sen:
    if ch in vowel:
        count = count + 1
print("Number of vowels:",count)


nums = input("enter the numbers that you want:")


my_list = [int(n) for n in nums.split(",")]

print(my_list)

for num in my_list:
    if num%2 == 0:
        print(f"{num} is Even")
    else:
        print(f"{num} is odd")
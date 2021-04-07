last = ['a', 'a', 'v', 'u']

print(last)
unique = set()
for i in last:
    if i not in unique:
        unique.add(i)
diff = len(last) - len(unique)

if diff > 0:
    unique = set()
    for i in last:
        if i not in unique:
            unique.add(i)
    last = unique
print(last)

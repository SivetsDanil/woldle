a = open("words.txt", 'r', encoding='utf8').readlines()
b = set()
for r in a:
    b.add(r.strip().lower().replace("ё", "е"))
print(b)
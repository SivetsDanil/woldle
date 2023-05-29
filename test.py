import json
top_file = json.load(open("mysite/users/1_users_top.json", encoding='utf8')).values()
users_top = []
for r in sorted(top_file, key=lambda x: x[0], reverse=True)[:5]:
    users_top.append(r[1])
print(users_top)
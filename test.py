import json
top_file = json.load(open("mysite/users/1_users_top.json", encoding='utf8'))
users_top = []
for r in top_file:
    if len(users_top) == 5:
        break
    users_top.append(top_file[r])
print(users_top)
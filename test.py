import json
top_file = json.load(open("mysite/users/1_users_top.json", encoding='utf8'))
top_list = list(map(int, list(top_file)))
users_top = []
for r in sorted(top_list, reverse=True):
    if len(users_top) == 5:
        break
    users_top.append(top_file[str(r)])
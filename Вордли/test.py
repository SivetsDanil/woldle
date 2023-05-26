import csv
users_top = list(csv.DictReader(open("users/1_users_top.csv", "r"), delimiter=';'))
users_top.sort(key=lambda x: -int(x["exp"]))
for r in users_top:
    print(r)
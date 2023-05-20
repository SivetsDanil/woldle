import texts
k = {'sun', 'box', 'fax', 'oil', 'fox', 'cat', 'bad', 'tee', 'car', 'die', 'pig', 'ice', 'big', 'bee', 'one', 'try', 'bus', 'two', 'end', 'jam', 'ski', 'cow', 'pet', 'aid', 'can', 'joy', 'men', 'key', 'guy', 'fog', 'pie', 'bit', 'axe', 'pin', 'job', 'fit', 'air', 'fix', 'cap', 'arm', 'eye', 'bar', 'fun', 'kid', 'mum', 'dog', 'boy', 'toy', 'egg', 'sky'}
s = []
while len(s) != 50:
  x = input()
  if len(x) == 3 and x not in s and x in texts.eng_play_words[3] and x not in k:
    s.append(x)
    print("complete!")

print(set(s))
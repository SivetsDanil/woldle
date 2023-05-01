import pymorphy2
import json
lst = ["ыфаыафыа"]
threshold = 0.4

morph = pymorphy2.MorphAnalyzer()
for word in lst:
    p = morph.parse(word)
    score = p[0].score
    print(f'{word} - {"осмысленное" if score >= threshold else "бред"}')

json.dump({"a": 0}, open('b.json', 'w'))
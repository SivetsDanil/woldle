f = open("words.txt", "r").readlines()



print({i.strip().split(" ")[-1].lower() for i in f if len(i.strip())})
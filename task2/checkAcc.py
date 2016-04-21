c = open('corrected.txt', 'r')
one = 0
total = 0.0
for line in c:
	total += 1
	data = line.strip().split('\t')[0]
	if data == "1":
		one += 1

print one/total

train = open("spelling_error.edits", "r")
words = " "
cmd = { 'delete': {},
		'insert': {},
		'substitute': {},
		'transpose': {}
	}

def process_line(line):
	#take line, strip off characters, split by tab
	word = "#" + line.strip().split('\t')[0]
	data = line.strip().split('\t')[2]
	t, first, second = data.split(',')

	return word, t, first, second

for line in train:
	word, t, first, second = process_line(line)

	words += word + " "

	key = (first, second)
	cmd[t][key] = cmd[t].get(key, 0) + 1

for key1, value1 in cmd.iteritems():
	for key2, value2 in cmd[key1].iteritems():
		if key1 == 'insert' or key1 == 'substitute':
			lu = key2[0]
		elif key1 == 'delete' or key1 == 'transpose':
			lu = ''.join(key2)

		if lu in words:
			cmd[key1][key2] = value2 / float(words.count(lu))
		else:
			cmd[key1][key2] = 0

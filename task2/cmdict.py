train = open("spelling_error.edits", "r")
words = " "
cmf = { 'delete': {},
		'insert': {},
		'substitute': {},
		'transpose': {}
        }
correct = {}
cmd = { 'delete': {},
		'insert': {},
		'substitute': {},
		'transpose': {}
        }

def process_line(line):
    #take line, strip off characters, split by tab
    word = line.strip().split('\t')[0]
    data = line.strip().split('\t')[2]
    t, first, second = data.split(',')

    return word, t, first, second

for line in train:
    word, t, first, second = process_line(line)

    words += word + " "

    key = (first, second)
    cmf[t][key] = cmf[t].get(key, 0) + 1

    if t == 'insert' or t == 'substitute':
        correct[first] = words.count(first)
    elif t == 'delete' or t == 'transpose':
        nc = first + second
        correct[nc] = words.count(nc)

for key1, value1 in cmf.iteritems():
    for key2, value2 in cmf[key1].iteritems():
        if key1 == 'insert' or key1 == 'substitute':
            lu = key2[0]
        elif key1 == 'delete' or key1 == 'transpose':
            lu = ''.join(key2)

        if correct[lu] == 0:
            cmd[key1][key2] = 0
        else:
            cmd[key1][key2] = value2 / float(correct[lu])

# if __name__ == '__main__':
#     main()

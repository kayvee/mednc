"""
Interpolated Kneser-Ney Smoothing:

-m train equivalent to running SRILM's ngram-count
with -vocab [file] -unk -kndiscount -interpolate
-m test equivalent to running SRILM's ngram
with -vocab [file] -unk
"""

__author__ = """Hahn Koo (hahn.koo@sjsu.edu)"""

import sys, re, time, math, getopt, pickle

def vocab_file(file):
	"""Create vocabulary from file.

	Args:
	- file: lines of words
	Returns:
	- set([... word ...])
	"""
	out = []
	for line in open(file).readlines():
		out.append(line.strip())
	special = set(['<s>', '</s>', '<unk>'])
	out = set(out).union(special)
	return out

def lower(hwd):
	"""Lower order n-gram.

	Args:
	- hwd: {h : {w : C(hu)}}
	Returns:
	- {h' : {w : N1+(*h'w)}}
	"""
	out = {}
	for h in hwd:
		hl = h.split(); v = hl[0]; bh = ' '.join(hl[1:])
		if not bh in out: out[bh] = {}
		if re.match('<s>', bh):
			for w in hwd[h]:
				if not w in out[bh]: out[bh][w] = 0.0
				out[bh][w] += hwd[h][w]
		else: 
			for w in hwd[h]:
				if hwd[h][w] > 0:
					if not w in out[bh]: out[bh][w] = []
					out[bh][w].append(v)
	for bh in out:
		if not re.match('<s>', bh):
			for w in out[bh]: out[bh][w] = len(out[bh][w])
	return out 

def params(ngd):
	"""Get all smoothing parameters."""
	nd = {}; nhd = {}
	for i in range(1, 5): nd[i] = 0.0
	for h in ngd:
		nhd[h] = [0.0, 0.0, 0.0, 0.0] # N1, N2, N3+, C(h,*)
		for w in ngd[h]:
			c = ngd[h][w]
			nhd[h][3] += c
			if c in nd: nd[c] += 1
			if c == 1: nhd[h][0] += 1
			elif c == 2: nhd[h][1] += 1
			elif c >= 3: nhd[h][2] += 1
	d1, d2, d3p = discounts(nd[1], nd[2], nd[3], nd[4])
	return d1, d2, d3p, nhd

def discounts(n1, n2, n3, n4):
	"""Get discounts:

	Y = n1/(n1+2*n2)
	D1 = 1-2*Y*n2/n1
	D2 = 2-3*Y*n3/n2
	D3+ = 3-4*Y*n4/n3

	Args:
	- ngd: {h : {w : C(hw)}}
	Returns:
	- D1, D2, D3+
	"""
	d1 = None; d2 = None; d3p = None 
	if n1 > 0:
		y = n1/(n1+2*n2)
		d1 = 1-2*y*n2/n1
		if n2 > 0: d2 = 2-3*y*n3/n2
		if n3 > 0: d3p = 3-4*y*n4/n3
	return d1, d2, d3p

def alpha(d1, d2, d3p, t, w, h, ngd):
	"""Calculate alpha(w|h):

	alpha(w|h) = max{C(hw)-D, 0} / C(h*)
	"""
	sc = ngd[h][w]
	if sc == 1: sc -= d1
	elif sc == 2: sc -= d2
	elif sc >= 3: sc -= d3p
	sc = max(sc, 0.0)
	return sc/t

def bow(n1, n2, n3p, d1, d2, d3p, t):
	"""Calculate back-off-weight, bow(h):

	bow(h) = {D1*N1(h*) + D2*N2(h*) + D3+*N3+(h*)} / C(h*) 
	"""
	out = (d1*n1 + d2*n2 + d3p*n3p) / t
	return out

def train(n, ngd, v):
	"""Train an n-gram language model -- modified Kneser-Ney style

	P(w|h) = alpha(w|h) + bow(h)*P(w|h') 

	alpha(w|h) = max{C(hw)-D, 0} / C(h*)
	bow(h) = D * N_1+(h*) / C(h*) 

	Args:
	- n: n in n-grams in ngd
	- ngd: {h : {w : C(hw)}}
	- v: vocabulary (a set of words)
	Returns:
	- {'alpha': {n : alpha(w|h)}, 'bow': {n : bow(h)}}
	"""
	ad = {}; bd = {}
	ad[0] = {}; ad[0][''] = {}
	for w in v: ad[0][''][w] = 1.0/len(v)
	for i in range(n):
		k = n-i; ad[k] = {}; bd[k] = {}
		d1, d2, d3p, nhd = params(ngd)
		if d1 and d2 and d3p:
			for h in ngd:
				n1, n2, n3p, t = nhd[h]
				if t > 0: 
					bd[k][h] = bow(n1, n2, n3p, d1, d2, d3p, t)
					ad[k][h] = {}
					for w in ngd[h]:
						# alpha(w|h)
						ad[k][h][w] = alpha(d1, d2, d3p, t, w, h, ngd)
		if k > 1: ngd = lower(ngd)
	return {'alpha':ad, 'bow':bd}

def ngram_seq(pad, n, seq, v):
	"""List n-grams in seq."""
	for i in range(len(seq)):
		if not seq[i] in v: seq[i] = '<unk>'
	if pad: seq = ['<s>']*(n-1)+seq+['</s>']
	out = []
	for i in range(len(seq)-(n-1)): out.append(' '.join(seq[i:i+n]))
	return out

def ngram_data(pad, n, data, v):
	"""List n-grams and their weights found in data.

	Args:
	- data: [... [seq, weight] ...] where seq is a string
	Returns:
	- {u : {w : sum(weights(uw))}
	"""
	out = {}
	for seq, weight in data:
		seq = seq.strip().split()
		ngl = ngram_seq(pad, n, seq, v)
		for uw in ngl:
			wl = uw.split()
			u = ' '.join(wl[:-1]); w = wl[-1]
			if not u in out: out[u] = {}
			if not w in out[u]: out[u][w] = 0.0
			out[u][w] += weight
	return out 

def load(weighted, lines):
	"""Load lines into compatible data format.

	Args:
	- weighted: whether each sequence in line is weighted
	- lines: [... '(weight \t) seq' ...]
	Returns:
	- [... [seq, weight] ...] where seq is a string
	"""
	out = []
	for line in lines:
		ll = line.strip().split('\t')
		if weighted:
			w = float(ll[0]); seq = ll[1]
		else:
			w = 1.0; seq = ll[0]
		out.append([seq, w])
	return out

def p_ngram(n, hw, lmd):
	"""P(w|h)

	P(w|h) = alpha(w|h) + bow(h) * P(w|h')
	
	Args:
	- n: n in n-gram
	- hw: an n-gram string
	- lmd: {'alpha':{alpha(w|h)}, 'bow':{bow(h)}} 
	Returns:
	- P(w|h) 
	"""
	wl = hw.split(); w = wl[-1]
	ad = lmd['alpha']; bd = lmd['bow']
	out = ad[0][''][w] 
	for i in range(1, n+1):
		h = ' '.join(wl[-i:-1])
		if not h in lmd['bow'][i]: break
		bow = lmd['bow'][i][h]
		out *= bow
		try: out += lmd['alpha'][i][h][w]
		except KeyError: out += 0.0
	return out

def logP(pad, n, seq, ngd, v):
	"""Calculate logP(seq).

	Args:
	- pad: whether to pad input sequence
	- n: n in n-gram
	- seq: a string
	- ngd: {'alpha': {n : alpha(w|h_n)}, 'bow': {n : bow(h)}, 'smooth': P_smooth}
	Returns:
	- logP(seq) 
	"""
	out = 0.0
	for hw in ngram_seq(pad, n, seq.split(), v):
		p = p_ngram(n, hw, ngd)
		if p == 0: out += -1e+100
		else: out += math.log(p)
	return out

def display(ngd):
	"""Display language model in ARPA format.

	log_10 P(w|h) \t hw \t log_10 bow(h)

	Args:
	- ngd: {'alpha' : alpha(w|h), 'bow': back-off weight, 'smooth': P_smooth}
	"""
	ad = ngd['alpha']; bd = ngd['bow']
	n = len(bd)
	for i in range(1, n+1):
		print '\n\\'+str(i)+'-grams:'
		for h in ad[i]:
			for w in ad[i][h]:
				hw = (h+' '+w).strip()
				p = p_ngram(i, hw, ngd)
				lp = str(math.log(p, 10))
				try:
					bow = bd[i+1][hw]
					if bow > 0: bow = str(math.log(bd[i+1][hw], 10))
					else: bow = '-1e+100'
				except KeyError: bow = ''
				out = lp+'\t'+hw+'\t'+bow
				print out.strip()

def usage():
	print
	print "USAGE: python kn.py"
	print
	print "Option\t\tDefault\t\tDescription"
	print " -n\t\t2\t\tn of n-gram"
	print " -m\t\ttrain\t\tmode: train or test"
	print " -p\t\t./2gram.kn\tpickle file containing n-gram dictionary"
	print " -v\t\t./vocab\t\tvocabulary file"
	print " -w\t\tFalse\t\tData specifies weight of each word"
	print

def main(argv):
	n = 2; m = 'train'; pf = './2gram.kn'; vf = './vocab'; use_weight = False
	try:
		opts, args = getopt.getopt(argv, "n:m:p:v:w")
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	except ValueError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-n"): n = int(arg)
		elif opt in ("-p"): pf = arg
		elif opt in ("-v"): vf = arg 
		elif opt in ("-m"):
			if arg == 'train' or arg == 'test': m = arg
			else:
				usage(0)
				sys.exit(2)
		elif opt in ("-w"): use_weight = True
	pad = True; held_ratio = 0.1
	lines = sys.stdin.readlines()
	data = load(use_weight, lines)
	v = vocab_file(vf)

	if m == 'train': 
		sys.stderr.write('# Building language model ...\n')
		uwd = ngram_data(pad, n, data, v)
		ngd = train(n, uwd, v)
		pickle.dump(ngd, open(pf, 'w'))
	elif m == 'test':
		sys.stderr.write('# Testing language model ...\n')
		ngd = pickle.load(open(pf))
		lp = 0.0
		for seq, w in data:
			lpi = logP(pad, n, seq, ngd, v)
		#	print str(lpi)+'\t'+seq
			lp += lpi
		lp /= math.log(10)
		sys.stderr.write('# logprob(base10) = '+str(lp)+'\n')


if __name__ == '__main__': main(sys.argv[1:])

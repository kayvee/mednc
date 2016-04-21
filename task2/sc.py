"""LING 165 Lab 2: Spelling Correction"""

import sys, pickle, re, math
import kn
import cmdict2

def edit(x):
	"""List ways to that x could have been derived."""
	alphabet = 'abcdefghijklmnopqrstuvwxyz'
	n = len(x)
	dd = {}; di = {}; ds = {}; dr = {}
	for i in range(n):
		# reverse insertion error
		xi = x[:i] + x[i+1:]
		di[xi] = (('#' + x)[i], x[i])
		# reverse substitution error
		for c in alphabet:
			xs = x[:i] + c + x[i + 1:]
			ds[xs] = (c, x[i])
	for i in range(n - 1):
		# reverse transposition error
		xr = x[:i] + x[i + 1] + x[i] + x[i + 2:]
		dr[xr] = (x[i + 1], x[i])
	for i in range(n + 1):
		# reverse deletion error
		for c in alphabet:
			xd = x[:i] + c + x[i:]
			dd[xd] = (('#' + x)[i], c)
	return dd, di, ds, dr

def candidates(t, v):
	"""Get real-word candidates of t."""
	dd, di, ds, dr = edit(t)
	out = {}
	for x in dd:
		if x in v: out[x] = ('delete', dd[x])
	for x in di:
		if x in v: out[x] = ('insert', di[x])
	for x in ds:
		if x in v: out[x] = ('substitute', ds[x])
	for x in dr:
		if x in v: out[x] = ('transpose', dr[x])
	return out

def lm(w, lw, rw, v, d):
	"""Language model"""
	seq = ' '.join([lw, w, rw])
	lp = kn.logP(False, 2, seq, d, v)
	return lp

def cm(e, (x, y), v, d):
	"""Channel model"""
	p = d[e].get((x, y), 0.0)
	lp = -1e+100
	if p > 0.0: lp = math.log(p)
	return lp

def argmax(t, lw, rw, v, cmd, lmd):
	"""argmax_c P(t|c)*P(c)
	where
	P(c) ~= P(lw, c, rw)
	and lw: word to the left, rw: word to the right
	"""
	cd = candidates(t, v)
	out = []
	for c in cd:
		e, (x, y) = cd[c]
		lpc = cm(e, (x, y), v, cmd) # apply channel-model
		lpc += lm(c, lw, rw, v, lmd) # apply language-model
		out.append((lpc, c))
	out.sort()
	if out != []: return out[-1][1]
	else: return None

def vocab():
	v = []
	for line in open('vocab'):
		w = line.strip()
		v.append(w)
	return set(v)

if __name__ == '__main__':
	v = vocab()
	lmd = pickle.load(open('2gram.kn'))

	## Provide the cmd dictionary in the line below:
	cmd = cmdict2.cmd

## Don't mess with the lines below:
	f = open('correct_me.txt')
	for line in f:
		lc, e, rc = line.strip().split('\t')
		t = re.findall('>(.+?)<', e)[0].strip()
		c = re.findall('targ=(.+?)>', e)[0].strip()
		lw = lc.split()[-1]
		rw = rc.split()[0]
		pred = argmax(t, lw, rw, v, cmd, lmd)
		label = '0'
		if c == pred: label = '1'
		print '\t'.join([label, pred, line.strip()])
	f.close()

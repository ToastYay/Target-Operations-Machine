#!/usr/bin/env python
import datetime
from urllib import unquote_plus
import random
from wsgiref.handlers import CGIHandler

def calcoffsets(n):
	allposs = []
	for a in range(2,n):
		for b in range(a+1,n):
			for c in range(b+1,n):
				dists = [-1] * n
				iters = 1;
				prevlist = [0]
				while -1 in dists:
					#print "iters = ",str(iters)
					nextlist = []
					for i in prevlist:
						t0 = (i+1) % n
						t1 = (i+a) % n
						t2 = (i+b) % n
						t3 = (i+c) % n
						if dists[t0]==-1:
							dists[t0] = iters
							nextlist.append(t0)
						if dists[t1]==-1:
							dists[t1] = iters
							nextlist.append(t1)
						if dists[t2]==-1:
							dists[t2] = iters
							nextlist.append(t2)
						if dists[t3]==-1:
							dists[t3] = iters
							nextlist.append(t3)
					iters += 1
					prevlist = nextlist
				allposs.append(dists)
				total = sum(dists) - dists[0]
#				print "total =",total, "\ttotal/self =", float(total)/float(dists[0]), "\tself =",dists[0], "\toffsets =",[1,a,b,c],dists
	# Now we have all the possible lists
	besttotal = 999999999
	bestlist = []
	bestrat = 0
	for list in allposs:
		tot = sum(list) - list[0]
		if tot < besttotal:
			bestrat = float(tot)/float(list[0])
			besttotal = tot
			bestlist = list
		elif tot == besttotal:
			rat = float(tot)/float(list[0])
			if rat < bestrat:
				bestrat = rat
				bestlist = list
#	sys.stderr.write("Best one found:")
	bestoffsets = []
	for i in xrange(len(bestlist)):
		if bestlist[i] == 1:
			bestoffsets.append(i)
#	print "total =",besttotal,"\ttotal/self =", float(besttotal)/float(bestlist[0]), "\tself =",bestlist[0], "\n",bestlist,"\nOffsets: ",bestoffsets 
	return (bestoffsets, bestrat)

def genpage(start_response, output):
	# Send post reply
	status = '200 OK'
	response_headers = [('Content-type', 'text/plain'),
					  ('Content-Length', str(len(output)))]
	start_response(status, response_headers)
	return [output]



# WSGI stuff
def application(environ, start_response):
	if environ["REQUEST_METHOD"] == "POST":
		body = environ['wsgi.input'].read(int(environ['CONTENT_LENGTH']))
		parameter_pairs = body.split('&')
		parameter = dict()
		for parameter_pair in parameter_pairs:
			parameter_pair = parameter_pair.split('=')
			parameter[unquote_plus(parameter_pair[0])] = unquote_plus(parameter_pair[1])
#		output = repr(parameter)

		# TODO: IMPLEMENT CODE HERE
		players = parameter["players"]


		retval = ""
		people = {}
		lines = players.split('\n')
		for line in lines:
			try:
				(codename, realname) = line.strip().split(':')
			except:
				continue
			if codename in people.keys() and people[codename] != realname:
				return genpage(start_response, "Error: duplicate codename %s refers to players %s and %s.  Please check your input and resubmit." % (codename, realname, people[codename]))
			if realname in people.values():
				return genpage(start_response, "Error: duplicate real name %s has multiple codenames.  Please check your input and resubmit." % (realname))
			people[codename] = realname
			
			#retval = retval + codename + "\n"
		(offsets, ratio) = calcoffsets(len(people))
		codenames = people.keys()
		random.shuffle(codenames)
		if len(codenames) < 10:
			return genpage(start_response, "Error: too few people.  This game really sucks when there's not enough players, and %s doesn't cut it.  Go for at least 10 players." % len(codenames))
		retval = retval + "Game notes:\n" + ("There are %d people playing.  Each person has 4 targets, at circle offsets %s.\n" % (len(codenames), offsets)) #+ ("The ratio of minimum distance to duplicate over distance to self is %s." % str(ratio))
		retval = retval + "Target lists follow.\n\n\n\n"
		for i in xrange(len(codenames)):
			codename = codenames[i]
			realname = people[codename]
			targets = map( lambda x: ((x+i) % len(codenames)) , offsets)
			targetnames = map( lambda x: codenames[x] , targets)
			retval = retval + realname + (" (%s) " % codename) + "has targets:\n" + "\t".join(targetnames) + "\n\n"

		return genpage(start_response, retval)

	else:
		response_headers = [("Allow", "POST")]
		status = "405 Method not allowed"
		start_response(status, response_headers)
		return [""]

if __name__ == "__main__":
    CGIHandler().run(application)

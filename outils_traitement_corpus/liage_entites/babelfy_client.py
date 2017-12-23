#coding=utf8

"""
Calls Babelfy for the text of the file whose full path is given as an argument,
or for the string of text specified below.
Requires the requests library (pip install requests or easy_install requests
from cmd)
The language can be changed inside "params" below.
"""

import codecs
import json
import re
import requests
import sys


__author__ = 'Pablo Ruiz'
__date__ = '08/04/16'


DBPRESPREF = u'http://dbpedia.org/resource/'
SORT = True
MAXCANDS = 3

# IO
try:
    text = codecs.open(sys.argv[1], "r", "utf8").read()
except IndexError:
    #text = """I still have a dream, a dream deeply rooted in the American dream. MLK"""
    #text = u"""Toledo est un ville au mid-ouest américain"""
    #text = u"""Buenos dias, mon nom est Inigo Montoya, je viens de Toledo, tu as tué mon père, prépare-toi à mourir"""
    text = u"""Buenos dias, mon nom est Inigo Montoya, je viens de Toledo, j'aime l'escrime."""
    #text = """Thomas and Mario are strikers playing in Munich"""
    # try next one with TagMe as well
    #text = """London in Ontario is a small city in Canada, near Ottawa and has a university with a science campus. """
    #text = "The Paris Hilton hotel is a good place"
    #text = "Paris Hilton is a TV presenter"
    # try next one with and without partial match
    #text = "Paris is a city in Texas"

# options
params = {
    'url': 'https://babelfy.io/v1/disambiguate',
    'text': text.encode("utf8"),
    'lang': 'FR',
    'match': 'PARTIAL_MATCHING',
    'cands': 'ALL',
    'key': ''  # 100 calls per day without a key, register at Babelnet site for a key
}

# retrieving data
res = requests.post(params["url"], headers={'Accept-encoding': 'gzip'},
                    data=params)

annotations = json.loads(res.content)

outls = []
# parse response
print u"MENTION\tDEBUT\tFIN\tCAND_ENTITE\tCONF\tCOHER\tORIGINE"
for an in annotations:
    link = an['DBpediaURL']
    # cases where mention is not an entity, but a word-sense
    if link in (None, ""):
        continue
    span = an['charFragment']
    start = span['start']
    end = span['end']
    # normalize before display cos babelfy does not remove whitespace
    norm_mention = re.sub(r"\s{2,}|[\r\n]+", " ", text[start:end+1])
    confidence = an['score']
    coherence = an['coherenceScore']
    source = an['source'] # Most-Common-Sense baseline (MCS) or not
    outl = u"{}\t{}\t{}\t{}\t{}\t{}\t{}".format(norm_mention,
        str(start), str(end), link.replace(DBPRESPREF, ''),
        str(confidence), str(coherence), source)
    if not SORT:
        print outl.encode("utf8")
    else:
        outls.append(outl)

if not SORT:
    sys.exit()


# sort by position, then by confidence
outd = {}
for ll in outls:
    # hash infos by mention
    outd.setdefault(ll.split("\t")[0], []).append(ll.split("\t"))
# sort mentions by mention position as given in first candidate-entity
for ke, va in sorted(outd.items(), key=lambda keva: int(keva[-1][0][1])):
    # sort entity candidates by confidence (index 4), restrict output to
    # MAXCANDS candidates
    for candinfo in sorted(va, key=lambda cinfo:-float(cinfo[4]))[0:MAXCANDS]:
        print "\t".join([unicode(info) for info in candinfo])

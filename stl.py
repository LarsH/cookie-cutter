import math
import numpy as np

def parseVector(i):
   assert i[0] in ['vertex','normal'], "Found" + ' '.join(i[:7])
   [a,b,c] = map(float,i[1:4])
   del i[:4]
   return (a,b,c)

def parseFacet(i):
   if i[0] != 'facet':
      return None
   del i[0]
   n = parseVector(i)
   assert i[0]=='outer' and i[1]=='loop', "Found" + ' '.join(i[:7])
   del i[:2]
   a = parseVector(i)
   b = parseVector(i)
   c = parseVector(i)
   assert i[0]=='endloop' and i[1]=='endfacet', "Found" + ' '.join(i[:7])
   del i[:2]
   # Todo: check n vs a,b,c
   return (n,a,b,c)

def parseAsciiStl(i):
   i = i.split()
   assert i[0]=='solid', "Found" + ' '.join(i[:7])
   name = i[1]
   del i[:2]
   l = []
   while True:
      f = parseFacet(i)
      if f == None:
         return (name,l)
      else:
         l += [f]

import struct
class StlObject():
   def __init__(self,buf=None):
      self.name = ''
      self.facets = []
      if buf != None:
         assert type(buf) == str, "Can only initialize with stl file contents"
         stl =  parseAsciiStl(buf)
         self.name = stl[0]
         self.facets = stl[1]

   def __iadd__(self, facet):
      "Adds a facet to the object. The normal points according to the right\
      hand rule, add vertices counter-clockwise for an upwards pointing normal"

      assert len(facet) == 3, "Facet does not have three corners"
      for v in facet:
         assert len(v) == 3, "Corner in facet does not have three coordinates"

      a,b,c = map(np.array,facet)
      v = b-a
      w = c-a
      n = np.cross(v,w)
      n = n / math.sqrt(n.dot(n))
      self.facets += [(n,a,b,c)]
      return self

   def save(self,filename):
      f = open(filename,'w')
      f.write((self.name+'\x00'*80)[:80])
      f.write(struct.pack('I',len(self.facets)))
      for y in self.facets:
         for v in y:
            for e in v:
               f.write(struct.pack('f',e))
         f.write(struct.pack('H',0))
      f.close()

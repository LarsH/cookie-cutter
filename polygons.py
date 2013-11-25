import math
import numpy as np

def pointOut(a,b,c):
   v = b-a
   w = b-c
   v = v / math.sqrt(v.dot(v))
   w = w / math.sqrt(w.dot(w))
   o = v + w
   o = o / math.sqrt(o.dot(o))

   assert 0.9 < math.sqrt(v.dot(v)) < 1.1, repr(v) + repr([a,b])
   assert 0.9 < math.sqrt(w.dot(w)) < 1.1, repr(w) + repr([c,b])
   # |v| = |w| = 1
   cosVW = v.dot(w)

   # Half the angle
   cosVWhalf = math.sqrt((cosVW+1)/2)

   o/= cosVWhalf

   z = np.array([0,0,1])
   if z.dot(np.cross(v,o)) < 0:
      # Concave part here...
      o = -o

   return o

def expandPolygon(l,width):
   """2d to 2d"""
   l2 = [np.array([a,b,0]) for (a,b) in l]
   l1 = l2[-1:] + l2[:-1]
   l3 = l2[1:] + l2[:1]

   lo = []

   for a,b,c in zip(l1,l2,l3):

      d = pointOut(a,b,c)
      o = b+width*d
      lo += [(o[0], o[1])]

   return lo

def drawLists(stlobj, l1,z1, l2,z2):
   """Accepts lists of 2d tuples"""

   l1 = [np.array([a,b,z1]) for (a,b) in l1]
   l2 = [np.array([a,b,z2]) for (a,b) in l2]

   l1n = l1[1:] + l1[:1]
   l2n = l2[1:] + l2[:1]

   for ((a,ao),(b,bo)) in zip(zip(l1,l1n),zip(l2,l2n)):
      stlobj += (a,bo,b)
      stlobj += (a,ao,bo)

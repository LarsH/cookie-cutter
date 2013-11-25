from polygons import drawLists, expandPolygon
import math


# Expand polygon

def compare(l1, l2):
   for a,b in zip(l1, l2):
      dx = a[0] - b[0]
      dy = a[1] - b[1]
      if dx*dx + dy*dy > 0.001:
         print "Got: %r, expected: %r"%(a,b)
         return False

for n in range(3,10):
   k = 2*math.pi/n
   vs = [k*x for x in range(n)]

   r1 = 1
   d = 1

   b = (math.pi/180) * (90 - 180/n)
   r2 = r1 + d/math.sin(b)
   l1= [(r1*math.sin(v), r1*math.cos(v)) for v in vs]
   l2= [(r2*math.sin(v), r2*math.cos(v)) for v in vs]
   l3 = expandPolygon(l1, d)

   rl = [math.sqrt(x*x+y*y) for (x,y) in l3]
   re = sum(rl)/len(rl)

   print n, r2, re
   compare(l3, l2)

from polygons import drawLists, expandPolygon
from stlFromImage import removeStraightSections
import math


# Expand polygon

def compare(l1, l2):
   retval = True
   if len(l1) != len(l2):
      print 'Lists are not of equal lenght!'
      l = min(len(l1), len(l2))
      print 'Stray elements:', l1[l:], l2[l:]
      retval = False

   for a,b in zip(l1, l2):
      dx = a[0] - b[0]
      dy = a[1] - b[1]
      if dx*dx + dy*dy > 0.001:
         print "Got: %r, expected: %r"%(a,b)
         return False
   return retval

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

#removeSTraightSections
print "RemoveStraight---"
l1 = [(0,0), (1,0), (2,0), (3,1), (4,2)]
l2 = [(0,0), (2,0), (4,2)]
l3 = removeStraightSections(l1)
print compare(l3, l2)


l1 = [(293, 8), (292, 9), (291, 9), (290, 9), (289, 9), (288, 9), (287, 9), (286, 9), (285, 10), (284, 10), (303, 8), (302, 8), (301, 8), (300, 8), (299, 8), (298, 8), (297, 8), (296, 8), (295, 8), (294, 8)]
l2 = [(293, 8), (292, 9), (286, 9), (285, 10), (284, 10), (303, 8)]
l3 = removeStraightSections(l1)
print compare(l3, l2)
l1 = [(293, 66), (335, 66), (336, 67), (280, 67), (291, 67), (292, 66)]
l2 = [(335, 66), (336, 67), (280, 67), (291, 67), (292, 66)]
l3 = removeStraightSections(l1)
print compare(l3, l2)



from polygons import getMaxExpand
print "getMaxExpand"
l1 = [(0,0), (1,0), (1,1), (0,1)]
print getMaxExpand(l1)

print "All tests done"

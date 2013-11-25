import stl
from polygons import drawLists, expandPolygon

# Expand polygon
l = [(1,2), (2,2), (2,1), (1,1)]
lo = expandPolygon(l, 1)
e = [(0,3), (3,3), (3,0), (0,0)]
for a,b in zip(lo,e):
   dx = a[0] - b[0]
   dy = a[1] - b[1]
   if dx*dx + dy*dy > 0.001:
      print "Got: %r, expected: %r"%(a,b)

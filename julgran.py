import stl
from polygons import drawLists, expandPolygon

l = [(2,12), (1,12), (4,8), (2,8), (5,4), (3,4), (6,0),(1,0),(1,-3)]

l += [(-x,y) for x,y in l[::-1]]
l += [(0,16)]

scale = 80/18.0
l = [(a*scale, b*scale) for a,b in l]

d = 2
h = 4.7
a = 20
b = 10

lo = expandPolygon(l, d)
lo2 = expandPolygon(lo,b)

s = stl.StlObject()

drawLists(s,lo,0, l,-h)
drawLists(s,l,-h, l,a-h)
drawLists(s,l,a-h, lo2,a-h)
drawLists(s,lo2,a-h, lo2,a-h-d)
drawLists(s,lo2,a-h-d, lo,a-h-d)
drawLists(s,lo,a-h-d, lo,0)

s.save('julgran.stl')

import stl
from polygons import drawLists, expandPolygon

l = [(2,12), (1,12), (4,8), (2,8), (5,4), (3,4), (6,0),(1,0),(1,-3)]

l += [(-x,y) for x,y in l[::-1]]
l += [(0,15)]

scale = 80/18.0
l = [(a*scale, b*scale) for a,b in l]

d = 2
h = 4.7
a = 20
b = 5

lo = expandPolygon(l, d)
lo2 = expandPolygon(lo,b)

s = stl.StlObject()

drawLists(s,l,0,l,a)
drawLists(s,lo ,0, l,0)
drawLists(s,lo2 ,0, lo,0)
drawLists(s,lo2,b,lo2,0)
drawLists(s,lo, b, lo2,b)
drawLists(s,lo, a-h, lo, b)
drawLists(s,l,a,lo, a-h)

s.save('julgran.stl')

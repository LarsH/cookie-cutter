#!/usr/bin/env python
import sys
import scipy.misc.pilutil as pilutil
from scipy import ndimage
import numpy, Image


globalScale = 10

import stl
from polygons import drawLists, expandPolygon
import polygons

def show(im):
   """Shows a numpy array image"""
   Image.fromarray(im.astype(numpy.uint8)).show()

def calculateThreshold(arr):
   """k-means threshold calculation for numpy arrray arr.
   Returns the threshold value"""
   T = numpy.mean(arr)
   T = int(T)
   oldT = T-1
   while oldT != T:
      oldT = T
      mask1 = 255 * (arr<=T)
      mask2 = 255 * (arr>T)
      T = int((numpy.mean(mask1) + numpy.mean(mask2))/2)
   return T

def binarize(im):
   """Converts an intensity image to binary"""
   #back = ndimage.gaussian_filter(im, sigma=40)

   norm = im.astype(numpy.float) # - back
   norm = 255*((norm - norm.min())/(norm.max()-norm.min()))
   norm = norm.astype(numpy.uint8)

   binary = (norm > calculateThreshold(norm))
   return binary


def getNeighbour(edgeIm, x,y):
   """
   returns the coordinates of the first pixel found around x,y
   starting from top right going down line by line
   returns None, None if no neighbour is found
   """
   edgeIm[y,x] = False
   for i in range(-1,2):
      for j in range(-1,2)[::-1]:
         if edgeIm[y+i,x+j]:
            return x+j, y+i
   return None, None

def getBorderLists(edgeIm):
   """ edgeIm is a binary edge image, might be modified
   returns a list of lists with coordinates for points on edges
   edges are visited clockwise

   Precond: every set pixel in edgeIm has exactly 2 8-connected neighbours
   """

   #  Sweep ---->
   #  ---------->
   #  -->#a
   #    bcd
   #
   #  When we hit the first pixel, it might be connected to either
   #  (a,b), (a,c) or (d,b)  We should continue at a or d.

   xs, ys = edgeIm.shape
   for y in range(ys):
      for x in range(xs):
         if edgeIm[y,x]:
            l = []
            while True:
               l += [(x*globalScale,y*globalScale)]
               x,y = getNeighbour(edgeIm, x,y)
               # XXX something is wrong here, the border gets traversed
               # in the wrong direction. Fixing by returning the reverse of l
               if x == None:
                  # XXX hotfix with [::-1]
                  return [l[::-1]] + getBorderLists(edgeIm)
   # No edges left
   return []


def removeDuplicates(l):
   while len(l) > 1 and l[0] == l[-1]:
      l = l[:-1]
   r = l[:1]
   for e in l[1:]:
      if e != r[-1]:
         r += [e]
   return r

def drawCutter(s, l):
   '''
   <-b-->
   +----+   ^  ^
   |    |   |  d
   | +--+   |  V
   | |      a
   | |      |
   | |      |
   | /      | ^
   |/       | h
   /        v v
   <d>
   '''
   d = 10
   h = 20
   a = 60
   b = 25 
   assert h + d < a
   assert d < b
   scale = globalScale
   [a,b,d,h] = [x*scale for x in [a,b,d,h]]

   # Draw first vertical part
   drawLists(s,l,0,l,a)

   t = 0 # how much we have expanded
   last = removeStraightSections(l)
   lastheight = 0 
   while t < d:

      e = polygons.getMaxExpand(last)
      if e != None and e < (d-t):
         # We are restricted
         pass
      else:
         # We can go all way
         e = d-t

      nxt = (expandPolygon(last, e))
      t += e

      drawLists(s,last,a, nxt,a)

      atheight = (float(t)/d) * h
      drawLists(s,nxt,atheight,last,lastheight)
      lastheight = atheight
      last = removeStraightSections(nxt)

   # loop done

   # We are now expanded, draw second vertical part
   drawLists(s,last,a-d,last,h)

   t = d # how much we have expanded
   # Our target is now b
   while t < b:
      e = polygons.getMaxExpand(last)
      if e != None and e < (b-t):
         # We are restricted
         pass
      else:
         # We can go all way
         e = b-t

      #print 'last', last
      nxt = expandPolygon(last, e)
      #print 'nxt', nxt
      t += e

      drawLists(s,last,a, nxt,a)
      drawLists(s,nxt,a-d,last,a-d)
      last = removeStraightSections(nxt)
      if len(nxt) < 3:
         # We have expanded a concave part down to nothing, we are done
         return

   # Loop done

   # We are now expanded, draw third and final vertical part
   drawLists(s,last,a,last,a-d)

def removeStraightSections(larg):
   ret = []
   l = removeDuplicates(larg)
   if len(l) < 3:
      return []

   # Initial dx/dy is take from last element to the first
   dx = l[0][0] - l[-1][0]
   dy = l[0][1] - l[-1][1]

   for a,b in zip(l, l[1:]+l[:1]):
      ndx = b[0] - a[0]
      ndy = b[1] - a[1]
      #print repr(((ndx, ndy), (dx, dy))), ndy * dx == dy * ndx
      if ndy * dx == dy * ndx:
         continue

      dx = ndx
      dy = ndy
      ret += [a]

   ret = removeDuplicates(ret)
   if len(l) != len(ret):
      # Solve problem with this type:
      #\   +   /    \        /
      # +--+--+   -> +------+
      return removeStraightSections(ret)
   else:
      return ret

def main(imname, outputFile):
   print "Loading image..."
   im = pilutil.fromimage(Image.open(imname).convert('I'))

   print "Binarizing..."
   bim = -binarize(im)

   nshape = (bim.shape[0] + 10, bim.shape[1] + 10)
   t = numpy.zeros(nshape, numpy.bool)
   t[5:-5,5:-5] = bim

   t2 = ndimage.binary_erosion(t)
   edge = t-t2

   #show(255*(edge + larger))
   #show(255*(edge))
   bl = getBorderLists(edge)

   # The first border is the outer one, the following are holes and should
   # be reversed
   bl = bl[:1] + [l[::-1] for l in bl[1:]]

   bl = map(removeStraightSections, bl)

   s = stl.StlObject()
   for l in bl:
      drawCutter(s,l)
   s.save(outputFile)

   return

if __name__ == '__main__':
   if len(sys.argv) == 3:
      main(sys.argv[1], sys.argv[2])
   else:
      print "Usage: %s [image filename] [output filename]"%sys.argv[0]

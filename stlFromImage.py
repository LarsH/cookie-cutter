#!/usr/bin/env python
import sys
import scipy.misc.pilutil as pilutil
from scipy import ndimage
import numpy, Image


ANSI_CURSOR_UP = "\033[1A"
globalScale = 25

import stl
from polygons import drawLists, expandPolygon
import polygons

def show(im):
   """Shows a numpy array image"""
   Image.fromarray(im.astype(numpy.uint8)).show()

def showrgb(r,g,b):
   arr = numpy.array([r,g,b]).swapaxes(0,2).swapaxes(0,1)
   show(arr)

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

def drawConnection(stlobj, p, l):
   "Draws a connection from p to l"
   d = 10
   h = 10
   a = 60
   b = 25
   assert h + d < a
   assert d < b
   scale = globalScale
   [a,b,d,h] = [x*scale for x in [a,b,d,h]]


   p1 = numpy.array([p[0],p[1],d])
   p2 = numpy.array([p[0],p[1],0])
   l1 = [numpy.array([x,y,d]) for (x,y) in l]
   l2 = [numpy.array([x,y,0]) for (x,y) in l]

   def f(stlobj, p, l):
      for i,j in zip(l, l[1:]):
         stlobj += (p,i,j)
   stlobj += (p1, p2, l1[-1])
   stlobj += (p2, l2[-1], l1[-1])
   f(stlobj, p1,l1[::-1])
   f(stlobj, p2,l2)


def drawCutter(s, l, avoidlist=[]):
   '''
   <-b-->
   +----+   ^  ^
   X    |   |  d
   + +--+   |  V
   | |      a
   | |      |
   | |      |
   | /      | ^
   |/       | h
   /        v v
   <d>

   X is not drawn if current (x,y) is in avoidlist
   '''
   d = 10
   h = 10
   a = 60
   b = 25
   assert h + d < a
   assert d < b
   scale = globalScale
   [a,b,d,h] = [x*scale for x in [a,b,d,h]]

   # Draw first vertical part
   drawLists(s,l,0,l,d,avoidlist)
   drawLists(s,l,d,l,a)

   t = 0 # how much we have expanded
   last = removeStraightSections(l)
   lastheight = a
   while t < d:
      print "Expansion 1, %3.2f%% done..."%(100*t/d), ANSI_CURSOR_UP
      e = polygons.getMaxExpand(last)
      if e != None and e < (d-t):
         # We are restricted
         pass
      else:
         # We can go all way
         e = d-t

      nxt = (expandPolygon(last, e))
      t += e

      drawLists(s,nxt,0, last,0)

      atheight = a - (float(t)/d) * h
      drawLists(s,last,lastheight,nxt,atheight,nxt)
      lastheight = atheight
      last = removeStraightSections(nxt)
   print
   # loop done

   # We are now expanded, draw second vertical part
   drawLists(s,last,a-h,last,d)

   t = d # how much we have expanded
   # Our target is now b
   while t < b:
      print "Expansion 2, %3.2f%% done..."%(100*(t-d)/(b-d)), ANSI_CURSOR_UP
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

      drawLists(s,nxt,0, last,0)
      drawLists(s,last,d,nxt,d)
      last = removeStraightSections(nxt)
      if len(nxt) < 3:
         # We have expanded a concave part down to nothing, we are done
         return
   print
   # Loop done

   # We are now expanded, draw third and final vertical part
   drawLists(s,last,d,last,0)

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

def getPixels(im):
   xs, ys = im.shape
   l = []
   for y in range(ys):
      for x in range(xs):
         if im[y,x]:
            l += [(x*globalScale,y*globalScale)]
   return l

def main(imname, outputFile):
   print "Loading image..."
   rgbimage = Image.open(imname)
   tmp = rgbimage.split()
   tmp = map(pilutil.fromimage, tmp)

   redband, greenband = tmp[:2] # ignore blue and alpha channel

   print "Binarizing..."
   bim = -binarize(redband)
   connections = binarize(greenband)

   # The cutterparts should not be included in the connection parts
   connections *= bim

   #show(255*bim)

   nshape = (bim.shape[0] + 10, bim.shape[1] + 10)
   t = numpy.zeros(nshape, numpy.bool)
   t[5:-5,5:-5] = bim

   c = numpy.zeros(nshape, numpy.bool)
   c[5:-5,5:-5] = connections


   t2 = ndimage.binary_erosion(t)
   edge = t-t2

   c2 = ndimage.binary_erosion(c)
   connEdge = c-c2

   sharedEdges = connEdge * edge

   conn8 = [[1,1,1], [1,1,1],[1,1,1]]
   (labelShared, nshared) = ndimage.measurements.label(sharedEdges, conn8)
   (labelConns, nconns) = ndimage.measurements.label(c, conn8)
   (labelCuts, ncuts) = ndimage.measurements.label(edge, conn8)

   bridges = {}
   for i in range(1,nshared+1):
      mask = (labelShared == i)
      cutindex = (labelCuts * mask).max()
      connindex = (labelConns * mask).max()
      if not connindex in bridges:
         bridges[connindex] = [cutindex]
      else:
         bridges[connindex] += [cutindex]

   for k in bridges:
      assert len(bridges[k]) == 2, "A connection must have exactly two ends!"
   '''
   for arr in [labelShared, labelConns, labelCuts]:
      sr = arr & 1
      sg = arr & 2
      sb = arr & 4
      k  = 255
      showrgb(k*sr, k*sg, k*sb)
   '''

   bl = []
   for i in range(1, ncuts+1):
      mask = (labelCuts == i)
      bl += getBorderLists(mask)
      #print map(len, bl)

   avoidlist = getPixels(sharedEdges)

   # The first border is the outer one, the following are holes and should
   # be reversed
   bl = bl[:1] + [l[::-1] for l in bl[1:]]

   bl = map(removeStraightSections, bl)

   s = stl.StlObject()
   for i,l in enumerate(bl):
      print "Creating cut %u of %u..."%(i+1, len(bl))
      drawCutter(s,l, avoidlist)

   for k in bridges:
      print k
      cut1, cut2 = bridges[k]
      # Labels use zero for background, numbering starts at one.
      # rebase to zero for the lists
      l1 = bl[cut1-1]
      l2 = bl[cut2-1]

      # Get the set of pixels that should be used in the connection
      cutpixels_image = (labelCuts==cut1) + (labelCuts==cut2)
      cutpixels_image *= (labelConns==k)
      pixellist = getPixels(cutpixels_image)
      #show(255*cutpixels_image)
      print len(pixellist)
      #+++---  1
      #++---+  2
      #--+++-  3
      #---+++  4
      # Four cases; Shift until to case 1 then strip the tail.
      def trimList(l, pl):
         retval = [] 
         s = l[-1] in pl
         for i,j in enumerate(l):
            if j in pl and not s:
               retval = l[i:] + l[i:]
               break
            s = j in pl
         for i,j in enumerate(retval):
            if not j in pl:
               retval = retval[:i]
               break
         return retval

      l1 = trimList(l1, pixellist)
      l2 = trimList(l2, pixellist)
      for x in l1 + l2:
         assert x in pixellist

      drawConnection(s, l1[0], l2)
      drawConnection(s, l2[0], l1)

   s.save(outputFile)

   return

if __name__ == '__main__':
   if len(sys.argv) == 3:
      main(sys.argv[1], sys.argv[2])
   else:
      print "Usage: %s [image filename] [output filename]"%sys.argv[0]

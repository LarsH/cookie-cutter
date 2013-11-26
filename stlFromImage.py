#!/usr/bin/env python
import sys
import scipy.misc.pilutil as pilutil
from scipy import ndimage
import numpy, Image

import stl
from polygons import drawLists, expandPolygon

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
   back = ndimage.gaussian_filter(im, sigma=40)

   norm = im.astype(numpy.float) - back
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
   for i in range(-1,2)[::-1]:
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
               l += [(x,y)]
               x,y = getNeighbour(edgeIm, x,y)
               if x == None:
                  return [l] + getBorderLists(edgeIm)
   # No edges left
   return []


def drawCutter(s, l):

   d = 1
   h = 2
   a = 10
   b = 5
   '''
   lo = expandPolygon(l, d)
   lo2 = expandPolygon(lo,b)
   drawLists(s,lo,0, l,-h)
   '''
   drawLists(s,l,-h, l,a-h)
   '''
   drawLists(s,l,a-h, lo2,a-h)
   drawLists(s,lo2,a-h, lo2,a-h-d)
   drawLists(s,lo2,a-h-d, lo,a-h-d)
   drawLists(s,lo,a-h-d, lo,0)
   '''


def main(imname, outputFile):
   print "Loading image..."
   im = pilutil.fromimage(Image.open(imname).convert('I'))

   print "Binarizing..."
   bim = -binarize(im)

   nshape = (bim.shape[0] + 10, bim.shape[1] + 10)
   larger = numpy.zeros(nshape, numpy.bool)
   larger[5:-5,5:-5] = bim

   t = ndimage.binary_dilation(larger)
   t = ndimage.binary_dilation(t)
   t = ndimage.binary_dilation(t)
   t2 = ndimage.binary_erosion(t)

   edge = t-t2

   #show(255*(edge + larger))
   #show(255*(edge))
   bl = getBorderLists(edge)

   # TODO: remove straight parts

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
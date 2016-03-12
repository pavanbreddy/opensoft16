import cv2
import numpy as np
from matplotlib import pyplot as plt
from graph import graph
min_length = 0.1
threshold = 230
delta=10
graphThresholdIntensity=1
tboxThreshhold=0.20
whlimit = 35
class Lines:
	def __init__(self):
		self.total_vertical =0
		self.vert_x = []
		self.vert_topy = []
		self.vert_bottomy = []

		self.total_horizontal =0
		self.hor_y = []
		self.hor_leftx = []
		self.hor_rightx = []
	def length(self, type, i):
		if ( type == 'v'):
			return self.vert_bottomy[i] - self.vert_topy[i]
		if (type =='h'):
			return self.hor_rightx[i]- self.hor_leftx[i]


# This class process a single page of the document
class page:
	def __init__(self,document,pageno):
		self.pdfImage=None
		self.graphList = []
		self.document=document
		self.pageno=pageno
	def process(self):
		rectangles=self.findAllRectangles()
		self.filterGraphsFromRectangles(rectangles)# populate graphList
		self.processGraphList()

	def findAllRectangles(self):
		img = cv2.cvtColor(self.pdfImage,cv2.COLOR_BGR2GRAY)
		kernel = np.ones((2,2), np.uint8)
		img = cv2.erode(img, kernel, iterations=1)
	    
		width = np.size(img,1)
		heigth = np.size(img,0)

		#DP matrix 
		vert_dp = np.zeros((heigth,width), dtype=np.uint16)
		hor_dp = np.zeros((heigth,width), dtype=np.uint16)
		lines = Lines();
		for i in range(1,heigth):
			for j in range(1,width):
				if img[i][j] <= threshold :
					vert_dp[i][j] = vert_dp[i-1][j] + 1
					hor_dp[i][j] = hor_dp[i][j-1] + 1

				if img[i][j] > threshold:
					if vert_dp[i-1][j] >= min_length * heigth:
						if not (vert_dp[i-1][j-1] <= vert_dp[i-1][j] +2 and vert_dp[i-1][j-1]>= vert_dp[i-1][j] /2 ):
							
							k = lines.total_vertical
							lines.vert_x.append(j)
							lines.vert_bottomy.append(i-1)
							lines.vert_topy.append(i - vert_dp[i-1][j] )
							lines.total_vertical = lines.total_vertical +1 
							#print 'added vertical line '

					if hor_dp[i][j-1] >= min_length * heigth:
						if not (hor_dp[i-1][j-1] <= hor_dp[i][j-1] +2 and hor_dp[i-1][j-1]>= hor_dp[i][j-1] / 2 ):
							 
							k = lines.total_horizontal
							lines.hor_y.append(i)
							lines.hor_rightx.append(j-1)
							lines.hor_leftx.append(j- hor_dp[i][j-1] )	
							lines.total_horizontal = lines.total_horizontal +1

		
		#print lines.total_vertical
		#print lines.total_horizontal	
		# Merge close lines 
		todelete=[]
		for i in range(0,lines.total_vertical):
			for j in range(i+1,lines.total_vertical):
				if((abs(lines.vert_topy[i]-lines.vert_topy[j])<=delta) and (abs(lines.vert_bottomy[i]-lines.vert_bottomy[j])<=delta) and (abs(lines.vert_x[i]-lines.vert_x[j])<=delta)):
					todelete.append(j)
		todelete.sort(reverse=True)
		for i in todelete:
			del lines.vert_x[i]
			del lines.vert_bottomy[i]
			del lines.vert_topy[i]
			lines.total_vertical=lines.total_vertical-1
		todelete=[]
		for i in range(0,lines.total_horizontal):
			for j in range(i+1,lines.total_horizontal):
				if((abs(lines.hor_leftx[i]-lines.hor_leftx[j])<=delta) and (abs(lines.hor_rightx[i]-lines.hor_rightx[j])<=delta) and (abs(lines.hor_y[i]-lines.hor_y[j])<=delta)):
					todelete.append(j)
		todelete.sort(reverse=True)
		for i in todelete:
			del lines.hor_y[i]
			del lines.hor_rightx[i]
			del lines.hor_leftx[i]
			lines.total_horizontal=lines.total_horizontal-1

		
		rectangles=[]
		for i in range(0,lines.total_vertical):
			for j in range(0,lines.total_vertical):
				if(i==j):
					continue
				if(lines.vert_x[j]<lines.vert_x[i]):
					continue
				if((abs(lines.vert_topy[i]-lines.vert_topy[j])<=delta) and (abs(lines.vert_bottomy[i]-lines.vert_bottomy[j])<=delta)):
					for k in range(0,lines.total_horizontal):
						if((abs(lines.hor_y[k]-lines.vert_topy[j])<=delta) and (abs(lines.hor_y[k]-lines.vert_topy[i])<=delta) and (abs(lines.hor_rightx[k]-lines.vert_x[j])<=delta) and (abs(lines.hor_leftx[k]-lines.vert_x[i])<=delta)):
							for l in range(0,lines.total_horizontal):
								if(k==l):
									continue
								if(lines.hor_y[l]<lines.hor_y[k]):
									continue
								if((abs(lines.hor_y[l]-lines.vert_bottomy[j])<=delta) and (abs(lines.hor_y[l]-lines.vert_bottomy[i])<=delta) and (abs(lines.hor_rightx[l]-lines.vert_x[j])<=delta) and (abs(lines.hor_leftx[l]-lines.vert_x[i])<=delta)):
									rectangles.append(((lines.hor_y[k],lines.vert_x[i]),(lines.hor_y[l],lines.vert_x[j])))

		todelete=[]
		for i in rectangles:
			for j in rectangles:
				if(i==j):
					continue
				if(i[0][0]<=j[0][0] and i[0][1]<=j[0][1] and i[1][0]>=j[1][0] and i[1][1]>=j[1][1]):
					todelete.append(j)
		for i in todelete:
			try:
				rectangles.remove(i)
			except ValueError:
				pass

		#print len(rectangles)
		return rectangles

	def filterGraphsFromRectangles(self,rectangles):
		img=self.pdfImage
		for r in rectangles:
			# r is ((row1,col1),(row2,col2)) 1->Top left, 2->Bottom Right
			#print r
			crop_img = img[r[0][0]:r[1][0], r[0][1]:r[1][1]]
			print crop_img[0][0]
			print r[1][1],r[0][1],r[1][0],r[0][0]
			graphObj=graph(self.document,self.pageno,r[1][1],r[0][1],r[1][0],r[0][0],img,crop_img)
			#graphObj.image=crop_img
			gray = cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY)
			_,thresh = cv2.threshold(gray,180,255,cv2.THRESH_BINARY_INV) # threshold
			height = np.size(crop_img, 0)
			width = np.size(crop_img, 1)

			
			'''
			# first erosin then dilation

			kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(2,2))
			eroded = cv2.dilate(thresh,kernel,iterations = 10) # erode
			'''
			'''
			
			#if height<=300 or width<=300:
			kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(1,1))
			#if (height>=300 and height <=600) or (width>=300 and width <= 600):
			dilated = cv2.dilate(thresh,kernel,iterations = 15) # dilate
			#eroded = cv2.dilate(dilated,kernel,iterations = 10) # dilate
			contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) # get contours
			

			index =1
			# for each contour found, draw a rectangle around it on original image
			flag=True
			for contour in contours:
			    # get rectangle bounding contour
			    [x,y,w,h] = cv2.boundingRect(contour)

			    # discard areas that are too large
			    if h>0.9*height and w>0.9*width:
			       continue
			    
			    # discard areas that are too small
			    if h<whlimit or w<whlimit:
			        continue

			    if(x<tboxThreshhold*crop_img.shape[0] and y+h>crop_img.shape[1]*(1-tboxThreshhold)):
			    	flag=False
			    	break

			    cropped_text = crop_img[y :y +  h , x : x + w]
			    graphObj.textBoxImages.append(cropped_text)
			  
			if flag :
				self.graphList.append(graphObj)

			'''
			kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(1,1))
			dilated = cv2.dilate(thresh,kernel,iterations = 1) # dilate

			for i in range(15):
				
				
				index = 0
				# for each contour found, draw a rectangle around it on original image
				contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) # get contours
				height = np.size(crop_img, 0)
				width = np.size(crop_img, 1)
				flag=True
				for contour in contours:
				    # get rectangle bounding contour
				    [x,y,w,h] = cv2.boundingRect(contour)

				    # discard areas that are too large
				    if h>0.7*height and w>0.7*width:
				       continue
				    
				    # discard areas that are too small
				    if h<whlimit or w<0.2*width:
				        continue

				    #if(x<tboxThreshhold*crop_img.shape[0] and y+h>crop_img.shape[1]*(1-tboxThreshhold)):
				    	#flag=False
				
				    index = index +1
				    W = w
				    H = h
				    X = x
				    Y = y 
				if index ==1 :
				    cropped_text = crop_img[Y :Y +  H , X : X + W]
				    print i
				    graphObj.textBoxImages.append(cropped_text)
				    break
				kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
				dilated = cv2.dilate(dilated,kernel,iterations = 1) # dilate
				  
			
			if flag :
				self.graphList.append(graphObj)
			
	def processGraphList(self):

		for g in self.graphList:
			print "ok"
			g.findLabel()
			g.findLabelText()
			g.findGradient()
			g.findMarkings()
			g.findCrop()
			g.findColorNnumOfPlots()
			#g.fillData()



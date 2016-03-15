import curve
import math
from curve import curve
import numpy as np 
import cv2
# from SimpleCV import *
from pytesseract import image_to_string
from PIL import Image as IMAGE
#from matplotlib import pyplot as plt
# import matplotlib.pyplot as plt
import re
import time
from sklearn.cluster import KMeans



class graph:
    def __init__(self,document,pageno,x2,x4,y2,y4,imagename,crop_image):

        # reference to the document
        self.document = document

        # page in which the graph is present
        self.pageno = pageno

        #coordinates
        self.x2 = x2
        self.x4 = x4
        self.y2 = y2
        self.y4 = y4

        #scale
        self.dx = 0                         #get it by calling findGradient(marking_imageurl) method
        self.dy = 0                         #get it by calling findGradient(marking_imageurl) method

        #marking
        self.minx = 0                       #get it by calling findMarkings(marking_imageurl)method twice.  
        self.maxx = 0                       #one time each for x and y axes
        self.miny = 0                       #not working for bad quality images. 
        self.maxy = 0                       #markings on image must be sharp and clear enough.

        # is it a log graph
        self.isLog = False

        #poll
        self.pollDistance = 0

        #curve point data for
        self.curveList = []
        
        self.xlabel = None                  #get it by calling findLabel(label_imageurl) method twice.
        self.ylabel = None                  #one time each for x and y axes.
        self.description = None             #even description can be obtained by the same method.

        self.graphboundX=None
        self.graphboundY=None
        self.image=imagename
        self.rectangle=crop_image


        self.textBoxImages=[]

    
    
    # to find x axis label and values
    def findxaxis_width(self,x1,y1,x2,y2):
        #cv2.imwrite("x_width.png",self.image)
        #img = IMAGE.open("x_width.png")
        #w,h=img.size
        #print'img size w=%d h=%d' %(w,h)
        #im = img.load()
        im=self.image
        #print self.image
        # print "x_width"
        # print "x1=%d y1=%d x2=%d y2=%d"%(x1,y1,x2,y2)
        y_temp=y1
        y_array=[]
        alternate_flag=1
        while(len(y_array)<3):
            x_temp=x1
            #print "husdh"
            #print x_temp,x1,x2
            a=np.array([200,200,200])
            flag=1
            while(x_temp<x2-1):
                # print "x_temp=%d y_temp=%d x2=%d"%(x_temp,y_temp,x2)
                #print (im[y_temp,x_temp].tolist())
                if( (im[y_temp,x_temp+1].tolist() < [200,200,200]or im[y_temp,x_temp+1].tolist()<[200,200,200])):
                    #print "failed"
                    flag=0
                    break
                x_temp=x_temp+1
                # print "out of loop flag=%d"%(flag)
                # print x_temp,y_temp
            if(flag==1 and alternate_flag==1):
                y_array.append(y_temp)
                alternate_flag=0
            elif(flag==0):
                alternate_flag=1
            y_temp+=1
        self.graphboundY=y_array[2]   
        return y_array

    def findyaxis_width(self,x4,y4,x1,y1):
        # img = Image.open(self.image)
        # w,h=img.size
        # im = img.load()
        im=self.image
        digit_pixel_size=(self.x2-x1)*9/236
        marking_pixel_distance=(self.x2-x1)*10/488
        print digit_pixel_size,marking_pixel_distance
        x_temp=x4
        x_array=[]
        count =0
        alternate_flag=1
        while(x_temp>=0 and count<3):
            y_temp=y4
            flag=1
            while(y_temp<y1-1):
                if((im[y_temp,x_temp].tolist()<[200,200,200] or im[y_temp+1,x_temp].tolist()<[200,200,200])):
                    flag=0
                    break
                y_temp+=1
            if(flag==1 and alternate_flag==1):
                if(count==0):
                    #print "count 0"
                    #print x4-x_temp,marking_pixel_distance
                    if(x4-x_temp>marking_pixel_distance):
                        return -1
                if(count==2):
                    #print "count 2"
                    #print x_array[1],x_temp
                    #print x_array[1]-x_temp,digit_pixel_size
                    if(x_array[1]-x_temp>digit_pixel_size):
                        x_array.append(x_temp)
                        count+=1
                    else:
                        x_array[1]=x_temp
                else:
                    print "count 1/0"
                    print count
                    x_array.append(x_temp)  
                    count+=1    
                alternate_flag=0
            elif(flag==0):
                alternate_flag=1
            x_temp-=1
        print x_array
        self.graphboundX=x_array[2]
        return x_array
        



    def findLabel(self):
        
        x1=self.x4
        y1=self.y2

        img=self.image
        #print self.x2,self.x4,self.y2,self.y4
        y=self.findxaxis_width(x1,y1,self.x2,self.y2)
        #print y

        iterator=0
        y_array_len=len(y)
        if(y_array_len==2):
            y.insert(2,y[1]+100)
            y_array_len+=1
            #print y
        #print 'len of y1 %d' % (y_array_len)

        while iterator<y_array_len-1:
            #print "iterator"+str(iterator)
            cropped = img[y[iterator] :y[iterator+1] ,x1:self.x2]
            s =  'images/temp_x' +str(iterator+1)+'.jpg' 
            cv2.imwrite(s , cropped)
            iterator+=1

        x=self.findyaxis_width(self.x4,self.y4,x1,y1)
        print x

        if(x!=-1):
            x_array_len=len(x)
            if(x_array_len==2):
                x.insert(x_array_len,0)
                x_array_len+=1
                #print x
            iterator=x_array_len-1
            #print 'len of x1 %d' % (x_array_len)

            i=0
            while iterator>0:
                if(iterator==2 and x_array_len==4):
                    cropped = img[self.y4:y1, x[iterator]: x[iterator-2]]
                    iterator=1
                else:
                    cropped = img[self.y4:y1, x[iterator]: x[iterator-1]]

                s =  'images/temp_y'+str(i+1)+'.jpg' 
                cv2.imwrite(s , cropped)
                iterator-=1
                i+=1
        else:
            print 'not a graph'










    #OCR for text labels and description of the graph. Call this method once for each of the three values.
    def findLabelText(self):
        for i in range(0,2):
            flag=0
            if i==0:                  
                img = Image("images/temp_x2.jpg",0)
            else:
                img = Image("images/temp_y1.jpg",0)
                        
            #print str(img.width) +"  " + str(img.height)
            if img.width<img.height:
                img = img.rotate(-90,fixed = False)
                flag=1
            #if img.width/img.height<3 : #crop image 

            
            #print str(img.width) +"  " + str(img.height)
            #if img.width<400 :
                #img = img.resize(img.width*5,img.height*5) 

            if img.height<50 :
                #print "ok"
                img = img.resize(img.width*2,img.height*4)
                img_inv = img.invert()
                img_inv.scale(100,100)
                img_bin = img_inv.binarize()
                img_bin = img_bin.dilate(2)
                img_bin = img_bin.erode(1)



            else:    
                img_inv = img.invert()
                img_inv.scale(100,100)
                img_bin = img_inv.binarize()


            
            #elif flag!=1:
            img_bin.save("images/temp.jpg")

            img = cv2.imread("images/temp.jpg") 
            dst = cv2.fastNlMeansDenoisingColored(img,None,10,10,7,21) 
            

            label = image_to_string(IMAGE.fromarray(dst),lang='eng')
            
            if flag==1:
                self.ylabel = label
                print label
            else:
                self.xlabel = label    
                print label
            #return label
            #pass


    #OCR for markings on x and y axes.Returns min & max value of the markings on an axis in that order.Call this method once for each axis. 
    def findMarkings(self):
            #flag=0
        for i in range(0,2):        
            if i == 0:    
                img = Image("images/temp_x1.jpg",0)
            else:
                img = Image("images/temp_y2.jpg",0) 

            if i==0:
                num_marking = int(img.width/self.dx+1)
            else:
                num_marking = int(img.height/self.dy+1)       
            #print str(img.width) +"  " + str(img.height)
           
            #if img.width/img.height<3 : #crop image 

            if img.width<70:
                #print "ok"
                img = img.resize(img.width*4,img.height*4)
                img_inv = img.invert()
                img_inv.scale(100,100)
                img_bin = img_inv.binarize()
                img_bin = img_bin.dilate(2)
                img_bin = img_bin.erode(1)
                #img_bin.erode().show()
            
            #print str(img.width) +"  " + str(img.height)
            #if img.width<400 :
                #img = img.resize(img.width*5,img.height*5)    
            
            else:
                img_inv = img.invert()
                img_inv.scale(100,100)
                img_bin = img_inv.binarize()


            if img.height<50:
                #print "ok"
                img = img.resize(img.width*4,img.height*4)
                img_inv = img.invert()
                img_inv.scale(100,100)
                img_bin = img_inv.binarize()
                img_bin = img_bin.dilate(2)
                img_bin = img_bin.erode(1)


            else:
                img_inv = img.invert()
                img_inv.scale(100,100)
                img_bin = img_inv.binarize()                




            """
            if flag==1:
                img_dilate = img_inv.dilate(2)
                img_erode = img_dilate.erode(2)
                img_erode.save("rot_1.jpg")
                """
            #elif flag!=1:
            img_bin.save("images/temp.jpg")

            img = cv2.imread("images/temp.jpg") 
            dst = cv2.fastNlMeansDenoisingColored(img,None,10,10,7,21) 
            

            marking = image_to_string(IMAGE.fromarray(dst),lang='eng')
            marking = marking.replace("\n"," ")
            marking = marking.split(" ")
            print marking
            for j in marking:
                if j=='':
                    marking.remove(j)            
            
            for j in range(len(marking)):
                print len(marking)
                marking[j] = marking[j].replace("O","0")
                #if marking[i][1]=="O":
                    #marking[i][1]="0"
            for j in marking:        
                if re.match("^\d+?\.?\d+?$", j) is None:    
                    marking.remove(j)
            print len(marking)        
            for j in range(len(marking)):
                marking[j]=float(marking[j])

            marking=sorted(marking)
            print marking

            for j in range(len(marking)):
                if marking[1]/marking[0] == marking[2]*1.0/marking[1]:
                    self.isLog = True
                
                else:
                    self.isLog = False 
            
            """    
            if num_marking>len(marking) and self.isLog==False:
                if num_marking-len(marking)==2:
                    #print "diff is 2"
                    marking.append(marking[1]-2*marking[0])
                    marking.sort()
                    marking.append(marking[len(marking)-1]+(marking[1]-marking[0]))                
                    marking.sort()
                if num_marking-len(marking)==1:
                    marking.append(marking[len(marking)-1]+(marking[1]-marking[0]))
                    marking.sort()              
                #else:
                    #i=int(i)
                    
            if num_marking>len(marking) and self.isLog==True:
                if num_marking-len(marking)==2:
                    #print "diff is 2"
                    marking.append(marking[0]**2/marking[1])
                    marking.sort()
                    marking.append(marking[len(marking)-1]*(marking[1]/marking[0]))                
                    marking.sort()
                if num_marking-len(marking)==1:
                    marking.append(marking[len(marking)-1]*(marking[1]/marking[0]))
                    marking.sort()                      
                    """

            if self.isLog==True:
                marking.append(marking[0]**2/marking[1])
                marking.sort()
                marking.append(marking[len(marking)-1]*(marking[1]/marking[0]))                
                marking.sort()    


            if self.isLog==False:
                marking.append(2*marking[0]-marking[1])
                marking.sort()
                marking.append(marking[len(marking)-1]+(marking[1]-marking[0]))                
                marking.sort()        

            print marking
            mark_len = len(marking)        
            if i==0:
                self.minx=marking[0]
                self.maxx=marking[mark_len-1]            
            else:
                self.miny=marking[0]
                self.maxy=marking[mark_len-1]
         
     
     
  
    #returns number of pixels between two markings on an axis. Call this method once for each axis.
    def findGradient(self):
        for i in range(0,2):
            if i==0:
                img = Image("images/temp_x1.jpg",0)
            else:
                img = Image("images/temp_y2.jpg",0)    
            img_inv = img.invert()
            img_inv.scale(100,100)
            img_bin = img_inv.binarize()

            resize=1
            if img_bin.width<70:
                resize = 1
                img_bin = img_bin.resize(img.width*4,img.height*resize)
            flag=0
            if img_bin.width<img_bin.height:
                flag = 1 
                img_bin = img_bin.rotate(-90,fixed = False)

            img_bin.save("images/temp.jpg")

            img = cv2.imread("images/temp.jpg")
            #h_img, w_img = img.shape[:2]
            #if w_img<h_img:
                 
            img = cv2.fastNlMeansDenoisingColored(img,None,10,10,7,21) 


            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # grayscale
            _,thresh = cv2.threshold(gray,150,255,cv2.THRESH_BINARY_INV) # threshold
            kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(2,2))
            dilated = cv2.dilate(thresh,kernel,iterations = 13) # dilate
            contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE) # get contours
            height = np.size(img, 0)
            width = np.size(img, 1)

            index =1
            rect_dim=[]
            for contour in contours:
                # get rectangle bounding contour
                [x,y,w,h] = cv2.boundingRect(contour)
                y=y+h
                rect = [x,y,w,h]
                
                # discard areas that are too large
                if h>0.7*height and w>0.7*width:
                   continue
                
                # discard areas that are too small
                if h<height*0.02 or w<width*0.02:
                    continue
                #print rect
                cv2.rectangle(img,(x,y),(x+w,y-h),(255,0,255),2)
                rect_dim.append(x+w/2.0) 
            cv2.imwrite("images/contoured.jpg", img)     

            rect_dim.sort(reverse=True)
            pix_diff=[]
            #print len(rect_dim)
            #print rect_dim
            for i in range(0,len(rect_dim)-1):
                pix_diff.append(rect_dim[i]-rect_dim[i+1])
            print pix_diff                        
            print sum(pix_diff)/len(pix_diff)
            print sum(pix_diff[:-1])/len(pix_diff[:-1])
            if abs(sum(pix_diff)/len(pix_diff)-sum(pix_diff[:-1])/len(pix_diff[:-1]))>3:
                pix_diff.remove(pix_diff[-1])
            pix_avg=sum(pix_diff)/(len(pix_diff)*1.0)

            pix_avg = pix_avg/resize


            if flag==1:
                pix_avgy=pix_avg
                print "pix_avgy="+str(pix_avgy)
                self.dy = pix_avgy
            else:
                pix_avgx=pix_avg    
                print "pix_avgx="+str(pix_avgx)  
                self.dx = pix_avgx 
             
             


    def findCrop(self):
        for i in range(len(self.textBoxImages)):
            cv2.imwrite("images/temp_textbox.png",self.textBoxImages[i])
            img=IMAGE.open("images/temp_textbox.png")
            # img = cv2.imread("temp_textbox.png")
            # w=np.size(img, 0)
            # h=np.size(img, 1)
            w,h=img.size
            print'img size w=%d h=%d i=%d' %(w,h,i)
            im = img.load()
            y_temp=0
            while(y_temp<h):
                x_temp=0
                while(x_temp<w-1):
                    print y_temp,x_temp,h,w
                    print im[x_temp,y_temp]
                    if((im[x_temp,y_temp]<(200,200,200) or im[x_temp+1,y_temp]<(200,200,200))):
                        img=cv2.imread("images/temp_textbox.png")
                        cropped = img[y_temp-1:h,0:w]
                        s =  'images/onlylabel_'+str(i+1)+'.png' 
                        cv2.imwrite(s , cropped)
                        return y_temp
                    x_temp+=1 
                y_temp+=1   
                print "als x_temp=%d y_temp=%d"%(x_temp,y_temp)





     
     
        
    #Returns all the labels and the corresponding colors in HSV of plots in graph in a curve datastructure.
    def findColorNnumOfPlots(self):
        for i in range(len(self.textBoxImages)):
            #flag=0
            s='images/onlylabel_'+str(i+1)+'.png'
            img = Image(s,0)
            #print str(img.width) +"  " + str(img.height)
               
            #print str(img.width) +"  " + str(img.height)
            #if img.width<400 :
                #img = img.resize(img.width*5,img.height*5)    
            img_inv = img.invert()
            img_inv.scale(100,100)
            img_bin = img_inv.binarize()
            
            """
            if flag==1:
                img_dilate = img_inv.dilate(2)
                img_erode = img_dilate.erode(2)
                img_erode.save("rot_1.jpg")
                """

            #elif flag!=1:
            img_bin.save("images/rot_1.jpg")

            img = cv2.imread("images/rot_1.jpg") 
            dst = cv2.fastNlMeansDenoisingColored(img,None,10,10,7,21) 
            
            graphs = image_to_string(IMAGE.fromarray(dst),lang='eng')
            graphs = graphs.replace("\n",">%$ ")                               #formatting the string to get the list 
            graphs = graphs.split(">%$ ")                                      #of plots plotted in given graphs                               
            print graphs
            graphNamesList=graphs
            n=len(graphs)                                                      #number of plots in given graph
            img = Image(s,0)
            img = img.resize(img.width*3,img.height*3)                         #resizing the image to make it big enough for cropping
            #print height
            #img = img.crop(15,15,img.width,img.height)                   #removing the edges of the given graph description image
            height = (img.height)*1.0/n
            width = img.width 
            graphList=[]
            start = 0
            for i in range(0,n):                                               #cropping the image so as to get a single plot description 
                cropImg = img.crop(0, start, width, height)                   #in one image
                graphList.append(cropImg)
                start+=height
            
            graphList1 = graphList    
            #time.sleep(3)
            """
            graphName = []      
            for i in graphList1:                                               #getting the names of all the plots from the images cropped above
                #i = i.resize(i.width*4,i.height*4)
                i = i.invert()
                i.scale(100,100)
                i = i.binarize()
                #i = i.erode()
                i.save("temp.jpg")
                i = cv2.imread("temp.jpg")
                i = cv2.fastNlMeansDenoisingColored(i,None,10,10,7,21) 
                g = image_to_string(IMAGE.fromarray(i),lang='eng')
                print g
                print "\n"
                graphName.append(g)
                """
            
            
            graphColor = []
            for i in graphList:                                                #finding colors of plots of all the images cropped above
                i.save("images/temp.jpg")    
                #raw_input()
                imge = cv2.imread("images/temp.jpg",1)
                
                imge = cv2.fastNlMeansDenoisingColored(imge,None,10,10,7,21) 
                imge = cv2.cvtColor(imge, cv2.COLOR_BGR2RGB)
                #imge = cv2.cvtColor(imge, cv2.COLOR_RGB2HSV)
         
                # show our image
                plt.figure()
                #plt.axis("off")
                #plt.imshow(imge)
                imge = imge.reshape((imge.shape[0] * imge.shape[1], 3))
                n_clusters = 3                                                 #number of clusters in kmeans clustering
                clt = KMeans(n_clusters = 3)
                clt.fit(imge)
                hist = centroid_histogram(clt)
                bar,color = plot_colors(hist, n_clusters, clt.cluster_centers_)
                #bar = cv2.cvtColor(bar,cv2.COLOR_GRAY2RGB) 
                # show our color bart
                plt.figure()
                #plt.axis()
                #plt.imshow(bar)
                #plt.show()
                
                if color[0]>240 and color[1]>240 and color[2]>240:             
                    color = [10.00, 10.00, 10.00]
                
                color = list(rgb2hsv(color[0],color[1],color[2]))
                #color[1] = color[1]                                      #increasing the picture saturation and value of the image
                #color[2] = color[2]                                       #which got reduced due to processing
                #color = hsv2rgb(color[0],color[1],color[2])     
                print color
                graphColor.append(color)                                    
                
                
            for i in range(0,len(graphColor)):
                c = curve(graphColor[i],graphNamesList[i])
                #c.color(graphColor[i])
                #c.name(graphName[i])
                 
                self.curveList.append(c)
            #return graphColor, graphName
            #pass
            print graphNamesList
            print graphColor
            print self.curveList

#<<<<<<< HEAD
    # the fill data funtion doesn,t take care of textbox inside the graph
#image passing needs clarification

    def findMarkings(self):
        table=np.zeros((len(self.curveList),self.x2-self.x1,2))
        for i in range(self.x1,self.x2):
            for j in range(self.y1,self.y2):
                for k in range(0,len(self.curveList)):
                    if img_object[j,i].all()<(self.curveList[k]+20).all() and img_object[i,j].all()>(self.curveList[k]-20).all():
                         #replace image list with appropriatre  object
                        if self.miny+j*self.dy>table[k,i-1][1]-(self.maxy-self.miny)/10 and self.miny+j*self.dy<table[k,i-1][1]+(self.maxy-self.miny)/10 :
                           self.istable=True
                           if self.isLog==False:
                                table[k,i]=[i*self.dx+self.minx,self.miny+j*self.dy]
                           else:
                               table[k,i]=[i*self.dx,math.exp(self.dy)]
        return table





#End of Funtion to avoid merge conflict -Adapa
  
   
def centroid_histogram(clt):   
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)                   # grab the number of different clusters and create a histogram
    (hist, _) = np.histogram(clt.labels_, bins = numLabels)                     # based on the number of pixels assigned to each cluster
  
    hist = hist.astype("float")                                                 # normalize the histogram, such that it sums to one
    hist /= hist.sum()
 
    return hist                                                                 # return the histogram
#=======
    # is it a log graph
    
#>>>>>>> 1919b2d4fde8870d45695236eb2367418646a5ba


def plot_colors(hist, n_clusters, centroids):
    bar = np.zeros((50, 300, 3), dtype = "uint8")                               # initialize the bar chart representing the relative frequency
    startX = 0                                                                  # of each of the colors
    
 
    i = 0                                                                       # loop over the percentage of each cluster and the color of
    mini = 300                                                                  # each cluster
    colval = 0
    for (percent, color) in zip(hist, centroids):
        endX = startX + (percent * 300)                                         # plot the relative percentage of each cluster
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
            color.astype("uint8").tolist(), -1)
        
        flag=0
        """
        if color[0]>240 and color[1]>240 and color[2]>240:
             i=i+1
             startX = endX
             continue
             """
        temp=endX-startX     
        if temp<mini and ((color[0]-color[1])>3 or (color[1]-color[0])>3 or (color[2]-color[1])>3 or (color[1]-color[2])>3 or (color[2]-color[0])>3 or (color[0]-color[2])>3):
            mini = temp
            flag=1
            colval = i    
        i=i+1
        startX = endX 
        """
        if flag==1 and color[0]>240 and color[1]>240 and color[2]>240:
             i=i+1
             startX = endX
             continue
             """      
            #color_req = color
        #startX = endX
    # return the bar chart
    print colval
    color_req = centroids[colval]
    return bar,color_req
    

def rgb2hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df/mx
    v = mx
    return h, s, v
    
    
    
def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = math.floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0: r, g, b = v, t, p
    elif hi == 1: r, g, b = q, v, p
    elif hi == 2: r, g, b = p, v, t
    elif hi == 3: r, g, b = p, q, v
    elif hi == 4: r, g, b = t, p, v
    elif hi == 5: r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b    
    









'''g1=graph('doc',1,292,57,232,39,'images/d.jpg')
g1=graph('doc',1,1309,409,850,290,'images/a.jpg')
g1.findLabel()
g1.findLabelText()
g1.findMarkings()
g1.findGradient()
print g1.xlabel
print g1.ylabel
print g1.dx
print g1.dy
print g1.minx, g1.maxx
print g1.miny, g1.maxy
print g1.isLog'''


#289,407,855,1



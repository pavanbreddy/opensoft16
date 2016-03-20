import wx
import os
from top import top
#import wx.Image
import wx.lib.wxcairo as wxcairo
import sys
import cv2
import poppler
from graph import graph
from curve import curve
from document import document
from page import page
picturewidth=300
pictureheight=300
pagewidth=600
pageheight=600
import wx
import wx.lib.wxcairo as wxcairo
import sys
from crop import *
import poppler
#from crop import *
from Utils import ResultEvent,DeleteEvent,CropEvent

import wx

########################################################################

class TestPopup(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent, style,filename,page,mainframe):
        """Constructor"""
        wx.Frame.__init__(self, parent, style)
        self.mainframe=mainframe
        self.page=page
        panel = wx.Panel(self)
       	self.panel = RectangleSelectImagePanel(self,filename)
       	self.okbutton=wx.Button(self,-1, 'OK', (50, 130))
       	self.okbutton.Bind(wx.EVT_BUTTON, self.OkButton)
       	self.cancelbutton=wx.Button(self,-1, 'Cancel', (50, 130))
       	self.cancelbutton.Bind(wx.EVT_BUTTON, self.CancelButton)
       	self.sizer1=wx.BoxSizer(wx.HORIZONTAL)
       	self.sizer2=wx.BoxSizer(wx.VERTICAL)
       	self.sizer1.Add(self.okbutton,1,wx.EXPAND)
       	self.sizer1.Add(self.cancelbutton,1,wx.EXPAND)
       	self.sizer2.Add(self.panel,5,wx.EXPAND)
       	self.sizer2.Add(self.sizer1,1,wx.EXPAND)
       	self.SetSizer(self.sizer2)
       	self.sizer2.Fit(self)
    def OkButton(self,e):
    	x0 = int(self.panel.x0)
        y0 = int(self.panel.y0)
        x1 = int(self.panel.x1)
        y1 = int(self.panel.y1)
    	self.mainframe.crop(self.page,(x0,y0,x1,y1))
    	#self.Close()
    def CancelButton(self,e):
    	self.Close()

    #     panel.SetBackgroundColour("CADET BLUE")

    #     st = wx.StaticText(panel, -1,
    #                        "This is a special kind of top level\n"
    #                        "window that can be used for\n"
    #                        "popup menus, combobox popups\n"
    #                        "and such.\n\n"
    #                        "Try positioning the demo near\n"
    #                        "the bottom of the screen and \n"
    #                        "hit the button again.\n\n"
    #                        "In this demo this window can\n"
    #                        "be dragged with the left button\n"
    #                        "and closed with the right."
    #                        ,
    #                        pos=(10,10))
         

    #     panel.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
    #     panel.Bind(wx.EVT_MOTION, self.OnMouseMotion)
    #     panel.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
    #     panel.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

    #     st.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
    #     st.Bind(wx.EVT_MOTION, self.OnMouseMotion)
    #     st.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
    #     st.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

    #     wx.CallAfter(self.Refresh)    

    # def OnMouseLeftDown(self, evt):
    #     self.Refresh()
    #     self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
    #     self.wPos = self.ClientToScreen((0,0))
    #     self.panel.CaptureMouse()

    # def OnMouseMotion(self, evt):
    #     if evt.Dragging() and evt.LeftIsDown():
    #         dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
    #         nPos = (self.wPos.x + (dPos.x - self.ldPos.x),
    #                 self.wPos.y + (dPos.y - self.ldPos.y))
    #         self.Move(nPos)

    # def OnMouseLeftUp(self, evt):
    #     if self.panel.HasCapture():
    #         self.panel.ReleaseMouse()

    # def OnRightUp(self, evt):
    #     self.Show(False)
    #     self.Destroy()
 
class PDFWindow(wx.ScrolledWindow):
    """ This example class implements a PDF Viewer Window, handling Zoom and Scrolling """

    MAX_SCALE = 2
    MIN_SCALE = 1
    SCROLLBAR_UNITS = 20  # pixels per scrollbar unit

    def __init__(self, parent):
        wx.ScrolledWindow.__init__(self, parent, wx.ID_ANY)
        # Wrap a panel inside
        self.panel = wx.Panel(self)
        # Initialize variables
        self.n_page = 0
        self.scale = 1
        self.document = None
        self.n_pages = None
        self.current_page = None
        self.width = None
        self.height = None
        # Connect panel events
        self.panel.Bind(wx.EVT_PAINT, self.OnPaint)
        self.panel.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.panel.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)

    def LoadDocument(self, file):
        self.document = poppler.document_new_from_file("file://" + file, None)
        self.n_pages = self.document.get_n_pages()
        self.current_page = self.document.get_page(self.n_page)
        self.width, self.height = self.current_page.get_size() 
        self._UpdateSize()

    def OnPaint(self, event):
        dc = wx.PaintDC(self.panel)
        cr = wxcairo.ContextFromDC(dc)
        cr.set_source_rgb(1, 1, 1)  # White background
        if self.scale != 1:
            cr.scale(self.scale, self.scale)
        cr.rectangle(0, 0, self.width, self.height)
        cr.fill()
        self.current_page.render(cr)

    def OnLeftDown(self, event):
        self._UpdateScale(self.scale + 0.2)

    def OnRightDown(self, event):
        self._UpdateScale(self.scale - 0.2)

    def _UpdateScale(self, new_scale):
        if new_scale >= PDFWindow.MIN_SCALE and new_scale <= PDFWindow.MAX_SCALE:
            self.scale = new_scale
            # Obtain the current scroll position
            prev_position = self.GetViewStart() 
            # Scroll to the beginning because I'm going to redraw all the panel
            self.Scroll(0, 0) 
            # Redraw (calls OnPaint and such)
            self.Refresh() 
            # Update panel Size and scrollbar config
            self._UpdateSize()
            # Get to the previous scroll position
            self.Scroll(prev_position[0], prev_position[1]) 

    def _UpdateSize(self):
        u = PDFWindow.SCROLLBAR_UNITS
        self.panel.SetSize((self.width*self.scale, self.height*self.scale))
        self.SetScrollbars(u, u, (self.width*self.scale)/u, (self.height*self.scale)/u)

    def OnKeyDown(self, event):
        update = True
        # More keycodes in http://docs.wxwidgets.org/stable/wx_keycodes.html#keycodes
        keycode = event.GetKeyCode() 
        if keycode in (wx.WXK_PAGEDOWN, wx.WXK_SPACE):
            next_page = self.n_page + 1
        elif keycode == wx.WXK_PAGEUP:
            next_page = self.n_page - 1
        else:
            update = False
        if update and (next_page >= 0) and (next_page < self.n_pages):
                self.n_page = next_page
                self.current_page = self.document.get_page(next_page)
                self.Refresh()
                
class curvepanel(wx.Panel):
	def __init__(self,parent,curveobj,mainframe):
    		self.mainframe=mainframe
		wx.Panel.__init__(self,parent)
		self.fulsizer=wx.BoxSizer(wx.VERTICAL)
		self.curve=curveobj
		self.titlesizer=wx.BoxSizer(wx.HORIZONTAL)
		self.titlabel=wx.StaticText(self,-1,"Title:")
		self.inputtitle=wx.TextCtrl(self)
		self.inputtitle.AppendText(self.curve.name)
		self.titlesizer.Add(self.titlabel,1,wx.EXPAND)
		self.titlesizer.Add(self.inputtitle,1,wx.EXPAND)
		self.tabletext=wx.TextCtrl(self,style=wx.TE_MULTILINE)
		for i in range(0,len(self.curve.x)):
			self.tabletext.AppendText(str(self.curve.x[i])+" : "+str(self.curve.y[i])+"\n")
		self.delbutton=wx.Button(self,-1, 'Delete', (50, 130))
		self.Bind(wx.EVT_BUTTON, self.OnClick)
		self.fulsizer.Add(self.titlesizer,1)
		self.fulsizer.Add(self.tabletext,6,wx.EXPAND)
		self.fulsizer.Add(self.delbutton,1)
		self.SetSizer(self.fulsizer)
	def OnClick(self,event):
		self.mainframe.deletefunc(self.curve)
	def save(self):
		self.curve.name=self.inputtitle.GetLineText(0)
		return self.curve

class CurveNoteBook(wx.Notebook):
    """
    Notebook class
    """
 
    #----------------------------------------------------------------------
    def __init__(self, parent,curvelist,mainframe):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )
        self.mainframe=mainframe
        self.pages=[]
        # Create the first tab and add it to the notebook
        for curve in curvelist:
        	curvetab=curvepanel(self,curve,mainframe)
            	self.pages.append(curvetab)
        	#curvetab.SetBackgroundColour("Gray")
                print curve.name
        	self.AddPage(curvetab, curve.name)
    def save(self):
		clist=[]
		for curve in self.pages:
			clist.append(curve.save())
		return clist	

class GraphNoteBook(wx.Notebook):
    """
    Notebook class
    """
 
    #----------------------------------------------------------------------
    def __init__(self, parent,graphlist,mainframe):
        self.mainframe=mainframe
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )
        self.pages=[]
        for graph in graphlist:
        	graphtab=grPanel(self,graph,mainframe)
        	self.pages.append(graphtab)
        	#curvetab.SetBackgroundColour("Gray")
        	self.AddPage(graphtab, "Graph")
 
        # Create the first tab and add it to the notebook
    def save(self):
	glist=[]
	for graph in self.pages:
		glist.append(graph.save())
	return glist	


class grPanel(wx.Panel):
	def __init__(self,parent,graphobj,mainframe):
    		self.mainframe=mainframe
		wx.Panel.__init__(self,parent)
		self.grobj=graphobj
		self.sizer=wx.BoxSizer(wx.VERTICAL)
		#self.sizer2=wx.BoxSizer(wx.HORIZONTAL)
		#self.curvepanels=[]
		self.xlabelsizer=wx.BoxSizer(wx.HORIZONTAL)
		self.xlabellabel=wx.StaticText(self,-1,"Xlabel:")
		self.inputxlabel=wx.TextCtrl(self)
		self.inputxlabel.AppendText(str(graphobj.xlabel))
		self.xlabelsizer.Add(self.xlabellabel,1,wx.EXPAND)
		self.xlabelsizer.Add(self.inputxlabel,1,wx.EXPAND)
		
		self.ylabelsizer=wx.BoxSizer(wx.HORIZONTAL)
		self.ylabellabel=wx.StaticText(self,-1,"Ylabel:")
		self.inputylabel=wx.TextCtrl(self)
		self.inputylabel.AppendText(str(graphobj.ylabel))
		self.ylabelsizer.Add(self.ylabellabel,1,wx.EXPAND)
		self.ylabelsizer.Add(self.inputylabel,1,wx.EXPAND)
		
		self.minxsizer=wx.BoxSizer(wx.HORIZONTAL)
		self.minxlabel=wx.StaticText(self,-1,"Minx:")
		self.inputminx=wx.TextCtrl(self)
		self.inputminx.AppendText(str(graphobj.minx))
		self.minxsizer.Add(self.minxlabel,1,wx.EXPAND)
		self.minxsizer.Add(self.inputminx,1,wx.EXPAND)
		
		self.minysizer=wx.BoxSizer(wx.HORIZONTAL)
		self.minylabel=wx.StaticText(self,-1,"miny:")
		self.inputminy=wx.TextCtrl(self)
		self.inputminy.AppendText(str(graphobj.miny))
		self.minysizer.Add(self.minylabel,1,wx.EXPAND)
		self.minysizer.Add(self.inputminy,1,wx.EXPAND)
		
		self.maxxsizer=wx.BoxSizer(wx.HORIZONTAL)
		self.maxxlabel=wx.StaticText(self,-1,"maxx:")
		self.inputmaxx=wx.TextCtrl(self)
		self.inputmaxx.AppendText(str(graphobj.maxx))
		self.maxxsizer.Add(self.maxxlabel,1,wx.EXPAND)
		self.maxxsizer.Add(self.inputmaxx,1,wx.EXPAND)
		
		self.maxysizer=wx.BoxSizer(wx.HORIZONTAL)
		self.maxylabel=wx.StaticText(self,-1,"maxy:")
		self.inputmaxy=wx.TextCtrl(self)
		self.inputmaxy.AppendText(str(graphobj.maxy))
		self.maxysizer.Add(self.maxylabel,1,wx.EXPAND)
		self.maxysizer.Add(self.inputmaxy,1,wx.EXPAND)
		self.delbutton=wx.Button(self,-1, 'Delete', (50, 130))
		self.delbutton.Bind(wx.EVT_BUTTON, self.OnClick)
		
		self.upbutton=wx.Button(self,-1, 'Update', (50, 130))
		self.upbutton.Bind(wx.EVT_BUTTON, self.updategraph)
		
		image=graphobj.rectangle
		cv2.imwrite('temp.jpg',image)
		image=wx.Image('temp.jpg')
            	h= image.Height
            	w=image.Width
            #wxImage = wx.ImageFromBuffer(w, h, image)
            	H=h
            	W=w
            	if(h>pictureheight):
             	   	H=pictureheight
              	  	W=(pictureheight*w)/h
            	if(W>picturewidth):
              	  H=(picturewidth*H)/W
              	  W=picturewidth
            #newimage=np.zeros((H,W,3), np.uint8)
            #newimage=cv2.resize(image,(H,W))
            #image=newimage
            	#wxImage = wx.BitmapFromBuffer( w,h, image)
            	wxImage=image.Scale(W,H)
            	print W
            	print H
            	bitmap = wx.BitmapFromImage(wxImage)
            	self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY,bitmap)
    		self.sizer.Add(self.xlabelsizer)
    		self.sizer.Add(self.ylabelsizer)
    		self.sizer.Add(self.minxsizer)
    		self.sizer.Add(self.maxxsizer)
    		self.sizer.Add(self.minysizer)
    		self.sizer.Add(self.maxysizer)
    		self.sizer.Add(self.imageCtrl)
		#self.titlabel=wx.StaticText(self,-1,"Title:")
		self.graph=graphobj
		self.curvenote=CurveNoteBook(self,graphobj.curveList,mainframe)
		
		#self.sizer.Add(self.curvenote)
		self.sizer.Add(self.delbutton)
		self.sizer.Add(self.upbutton)
        	self.sizerf=wx.BoxSizer(wx.HORIZONTAL)
        	self.sizerf.Add(self.sizer,1,wx.EXPAND)
        	self.sizerf.Add(self.curvenote,1,wx.EXPAND)
    		self.SetSizer(self.sizerf)
    		print 'yo'
		
	def updategraph(self,e):
		gr=self.save()
        	gr.dx=(gr.maxx-gr.minx)/(gr.x2-gr.x4)
                print gr.maxx.__class__.__name__
        	gr.dy=(gr.maxy-gr.miny)/(gr.y2-gr.y4)
		gr.fillData()
		self.mainframe.RefreshTree()
		# self.mainframe.docnote.SetSelection(gr.document.docid)
  #           	self.mainframe.docnote.pages[gr.document.docid].pagenote.SetSelection(gr.pageno)
  #           	self.mainframe.docnote.pages[gr.document.docid].pagenote.pages[gr.pageno].graphnote.SetSelection(gr.graphID)
        def OnClick(self,event):
        	print "Here"
        	self.mainframe.deletefunc(self.grobj)
		#wx.PostEvent(self.mainframe, DeleteEvent(self.grobj))
	def save(self):
        	print 'saving graph'
		self.grobj.xlabel=self.inputxlabel.GetLineText(0)
		self.grobj.ylabel=self.inputylabel.GetLineText(0)
		self.grobj.minx=float(self.inputminx.GetLineText(0))
		self.grobj.maxx=float(self.inputmaxx.GetLineText(0))
		self.grobj.miny=float(self.inputminy.GetLineText(0))
		self.grobj.maxy=float(self.inputmaxy.GetLineText(0))
		self.grobj.curvelist=self.curvenote.save()
		return self.grobj
class pagePanel(wx.Panel):
	def __init__(self,parent,page,mainframe):
		print '3'
		wx.Panel.__init__(self,parent)
    		self.mainframe=mainframe
		self.page=page
		#self.pageviewnote=wx.Notebook(self)
		self.graphnote=GraphNoteBook(self,page.graphList,mainframe)
		self.panel1=wx.Panel(self.graphnote)
		image=page.pdfImage
		cv2.imwrite('temp.jpg',image)
		image=wx.Image('temp.jpg')
            	h= image.Height
            	w=image.Width
            #wxImage = wx.ImageFromBuffer(w, h, image)
            	H=h
            	W=w
            	if(h>pageheight):
             	   	H=pageheight
              	  	W=(pageheight*w)/h
            	if(W>pagewidth):
              	  H=(pagewidth*H)/W
              	  W=pagewidth
            #newimage=np.zeros((H,W,3), np.uint8)
            #newimage=cv2.resize(image,(H,W))
            #image=newimage
            	#wxImage = wx.BitmapFromBuffer( w,h, image)
            	wxImage=image.Scale(W,H)
            	print W
            	print H
            	bitmap = wx.BitmapFromImage(wxImage)
            	self.imageCtrl = wx.StaticBitmap(self.panel1, wx.ID_ANY,bitmap)
		self.graphnote.AddPage(self.panel1,"PageView")
		self.sizer=wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.graphnote,1,wx.EXPAND)
		self.newbutton=wx.Button(self,-1, 'ADD NEW GRAPH', (50, 130))
		self.newbutton.Bind(wx.EVT_BUTTON, self.newButton)
		self.sizer.Add(self.newbutton)
    		self.SetSizer(self.sizer)
    	def newButton(self,e):
    		fname='filed'+str(self.page.document.docid)+'p'+str(self.page.pageno)+'.jpg'
    		cv2.imwrite(fname,self.page.pdfImage)
    		tp=TestPopup(self,wx.SIMPLE_BORDER,fname,self.page,self.mainframe)
            	tp.Show(True)
    		
    	def save(self):
    		newglist=self.graphnote.save()
    		self.page.graphList=newglist
    		return self.page

class PageNoteBook(wx.Notebook):
    """
    Notebook class
    """
 
    #----------------------------------------------------------------------
    def __init__(self, parent,pagelist,mainframe):
        print '502'
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)
        self.pan=wx.Panel(self)
        self.viewersizer=wx.BoxSizer(wx.VERTICAL)
        self.viewer=PDFWindow(self.pan)
    	self.viewer.LoadDocument(parent.doc.pdf_path)
      	self.mainframe=mainframe
    	self.viewer.SetFocus()
    	self.viewersizer.Add(self.viewer,1,wx.EXPAND)
    	self.pan.SetSizer(self.viewersizer)
    	self.viewersizer.Fit(self.pan)
    	#self.pdfpanel.SetSizer(self.viewersizer)
	#self.sizer=wx.BoxSizer(wx.VERTICAL)
    	#self.pagenote.AddPage(self.viewer,'View PDF')
        
        print '2'
        self.pages=[]
        for page in pagelist:
        	pagetab=pagePanel(self,page,mainframe)
        	self.pages.append(pagetab)
        	#curvetab.SetBackgroundColour("Gray")
        	self.AddPage(pagetab, "Page"+str(page.pageno))
        self.AddPage(self.pan,'View PDF')
    def save(self):
    	newpagelist=[]
    	for pagetab in self.pages:
    		newpagelist.append(pagetab.save())
    	return newpagelist
    		
 
        # Create the first tab and add it to the notebook
class docPanel(wx.Panel):
	def __init__(self,parent,docu,mainframe):
		
		wx.Panel.__init__(self,parent)
    		self.mainframe=mainframe
		self.doc=docu
		print '2'
		self.pagenote=PageNoteBook(self,docu.pageList,mainframe)
		print '3'
		#self.pdfpanel=wx.Panel(self.pagenote)
		# self.buttonpanel = pdfButtonPanel(pdfpanel, wx.NewId(),
  #                               wx.DefaultPosition, wx.DefaultSize, 0)
  #       	self.buttonpanel.SetSizerProps(expand=True)
  #       	self.viewer = pdfViewer(pdfpanel, wx.NewId(), wx.DefaultPosition,
  #                               wx.DefaultSize,
  #                               wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)
  #       	self.viewer.UsePrintDirect = ``False``
  #       	self.viewer.SetSizerProps(expand=True, proportion=1)

  #       # introduce buttonpanel and viewer to each other
  #       	self.buttonpanel.viewer = self.viewer
  #       	self.viewer.buttonpanel = self.buttonpanel
  #       	pdfV.viewer.LoadFile(docu.pdf_path)
  #       	self.viewsizer=wx.BoxSizer(wx.VERTICAL)
  #       	self.viewsizer.Add(self.buttonpanel,1,wx.EXPAND)
  #       	self.viewsizer.Add(self.viewer,1,wx.EXPAND)
  #       	self.pdfpanel.SetSizer(self.viewsizer)
  #       	self.pagenote.AddPage(self.pdfpanel,'View PDF')
		#self.viewersizer=wx.BoxSizer(wx.VERTICAL)
		#self.viewer=PDFWindow(self.pagenote)
    		#self.viewer.LoadDocument(docu.pdf_path)
    		#self.viewer.SetFocus()
    		#self.viewersizer.Add(self.viewer,1,wx.EXPAND)
    		#self.pdfpanel.SetSizer(self.viewersizer)
		self.sizer=wx.BoxSizer(wx.VERTICAL)
    		#self.pagenote.AddPage(self.viewer,'View PDF')
		self.sizer.Add(self.pagenote,1,wx.EXPAND)
    		self.SetSizer(self.sizer)
    		
	def save(self):
		pagelist=self.pagenote.save()
		self.doc.pageList=pagelist
		return self.doc


class DocNoteBook(wx.Notebook):
    """
    Notebook class
    """
    #print 'here'
    #----------------------------------------------------------------------
    def __init__(self, parent,doclist,mainframe):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )
        self.pages=[]
        self.doclist=doclist
        self.mainframe=mainframe
        self.initdocs(doclist)
    def initdocs(self,doclist):
       for i in range(0,len(self.pages)):
         self.DeletePage(i)
       self.pages = []
       for doc in doclist:
        	print '1'
        	doctab=docPanel(self,doc,self.mainframe)
        	#curvetab.SetBackgroundColour("Gray")
        	self.pages.append(doctab)
        	self.AddPage(doctab, doc.filename)
        # Create the first tab and add it to the notebook
    def savefiles(self):
    	newdoclist=[]
    	for doc in self.pages:
    		newdoclist.append(doc.save())
        print "d0p0g0"
        print newdoclist[0].pageList[0].graphList[0].minx
    	return newdoclist
    	
class DemoFrame(wx.Frame):
    """
    Frame that holds all other widgets
    """
 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Notebook Tutorial",
                          size=(600,400)
                          )
        panel = wx.Panel(self)
        self.obj=document()
        self.obj.pageList=[page(1,1)]
        lis=[self.obj, self.obj, self.obj]
        notebook = DocNoteBook(panel,lis)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()
 
        self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = DemoFrame()
    app.MainLoop()

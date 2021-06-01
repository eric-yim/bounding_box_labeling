import matplotlib.pyplot as plt
import matplotlib.patches as patches
class PointCollector:
    """
    For labeling keypoints

    Saves json as such
    [
        {x: data, y: data},
        {x: data, y: data}
    ]

    Output is a list
    """
    def __init__(self,img,output,save='points.json',scaled=True,title=None):
        assert isinstance(output,list), "Output Must be a List"
        self.output=output
        self.save=save
        self.scaled = scaled
        #self.original_img = img.copy()
        self.img = img

        self.h,self.w =img.shape[:2]
        self.f = plt.figure(figsize=(10,6))
        
        self.f.canvas.mpl_connect('button_press_event', self._onclick)
        self.ax = plt.subplot2grid((1, 1), (0, 0), colspan=1,rowspan=1)
        if title:
            self.f.suptitle(title)
        self._init_image()
        self.points = []
    
        #self.names = names
        self.f.canvas.mpl_connect('scroll_event', self._onscroll)
        self.i = 0
        #self._display_name()

    def _init_image(self):
        self.ax.clear()
        self.ax.imshow(self.img)
        
        self.f.canvas.draw()
    def _onclick(self,event):
        if event.inaxes:
            #Left Click
            if event.button==1:
                point = (event.xdata,event.ydata)
                self._add_point(point)
                
                
            #Mid Click
            elif event.button==2:
                
                plt.close()
                
            #Right Click
            elif event.button==3:
                self._remove_point()
            self._redraw()

    def _onscroll(self,event):
        pass
    def _add_point(self,point):
        if self.scaled:
            point = self._scale_points(point,self.h,self.w)
        self.output.append({'x':point[0],'y':point[1]})
    
        self._draw_point(point)
        

    def _write_to_output(self):
        """
        Write self.points to txt file
        """
        pass
    def _redraw(self):
        self._init_image()
        for v in self.output:
            point =(v['x'],v['y'])
            self._draw_point(point)

    def _remove_point(self):
        if len(self.output) > 0:
            self.output.pop(-1)

    def _scale_points(self,points,h,w):
        """
        Expects list of tuples OR single tuple
        [(x,y),(x,y)] OR (x,y)
        """
        h = float(h)
        w = float(w)
        if isinstance(points,list):
            return [self._scale_points(point,h,w) for point in points]
        return (points[0]/w,points[1]/h)
    def _unscale_points(self,points,h,w):
        h = float(h)
        w = float(w)
        if isinstance(points,list):
            return [self._unscale_points(point,h,w) for point in points]
        return (points[0]*w,points[1]*h)
            
    def _draw_point(self,point):
        if self.scaled:
            point = self._unscale_points(point,self.h,self.w)
        circle = patches.Circle(point,5,fill=True,color='lawngreen')
        self.ax.add_patch(circle)
        self.f.canvas.draw()
class PointCollectorWithNames:
    """
    For labeling keypoints,
    Each point has a name

    Scroll Down: next name
    Scroll Up: Prev name

    Saves json instead of txt
    {
        keypoint_name:{x: data, y: data}
    }

    """
    def __init__(self,names,img,output,save='points.txt',scaled=True,title=None):
        assert isinstance(output,dict), "Output Must be a Dict"
        self.output=output
        self.save=save
        self.scaled = scaled
        #self.original_img = img.copy()
        self.img = img

        self.h,self.w =img.shape[:2]
        self.f = plt.figure(figsize=(10,6))
        
        self.f.canvas.mpl_connect('button_press_event', self._onclick)
        self.ax = plt.subplot2grid((1, 1), (0, 0), colspan=1,rowspan=1)
        if title:
            self.f.suptitle(title)
        self._init_image()
        self.points = []
    
        self.names = names
        self.f.canvas.mpl_connect('scroll_event', self._onscroll)
        self.i = 0
        self._display_name()

    def _init_image(self):
        self.ax.clear()
        self.ax.imshow(self.img)
        
        self.f.canvas.draw()
    def _onclick(self,event):
        if event.inaxes:
            #Left Click
            if event.button==1:
                point = (event.xdata,event.ydata)
                self._add_point(point)
                
                
            #Mid Click
            elif event.button==2:
                
                plt.close()
                
            #Right Click
            elif event.button==3:
                self._remove_point()
            self._redraw()
    def _display_name(self):
        if self.i < len(self.names):
            print(f"Label for {self.names[self.i]}")
        else:
            print("Completed")
    def _onscroll(self,event):
        if event.inaxes:
            if event.button=='up':
                self.i-=1
                if self.i<0:
                    self.i=0
                self._display_name()
            elif event.button=='down':
                self.i+=1
                if self.i > len(self.names):
                    self.i = len(self.names)
                self._display_name()
    def _add_point(self,point):
        if self.scaled:
            point = self._scale_points(point,self.h,self.w)
        self.output[self.names[self.i]] = {'x':point[0],'y':point[1]}
        self._draw_point(point)
        
        while (self.i < len(self.names)) and (self.names[self.i] in self.output.keys()):
            self.i +=1
        self._display_name()
    def _write_to_output(self):
        """
        Write self.points to txt file
        """
        pass
    def _redraw(self):
        self._init_image()
        for k,v in self.output.items():
            point = (v['x'],v['y'])
            self._draw_point(point)
    def _remove_point(self):
        if self.i < len(self.names):
            key = self.names[self.i]
            self.output.pop(key,None)
    def _scale_points(self,points,h,w):
        """
        Expects list of tuples OR single tuple
        [(x,y),(x,y)] OR (x,y)
        """
        h = float(h)
        w = float(w)
        if isinstance(points,list):
            return [self._scale_points(point,h,w) for point in points]
        return (points[0]/w,points[1]/h)
    def _unscale_points(self,points,h,w):
        h = float(h)
        w = float(w)
        if isinstance(points,list):
            return [self._unscale_points(point,h,w) for point in points]
        return (points[0]*w,points[1]*h)
            
    def _draw_point(self,point):
        if self.scaled:
            point = self._unscale_points(point,self.h,self.w)
        circle = patches.Circle(point,5,fill=True,color='lawngreen')
        self.ax.add_patch(circle)
        self.f.canvas.draw()
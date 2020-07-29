import numpy as np
#from PIL import Image
import matplotlib.pyplot as plt
import os
import pandas as pd
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", default = '/media/hd0/71220202_external/avanti_media/crowd_count/ytstream_saves/shibuya02/originals/',type=str, help="name of base directory")
ap.add_argument("-s", "--start_image", type=str,default='None',
                    help="e.g. 00099.png (must match exactly)")
    
args = ap.parse_args()
top_left = True
point_tl = None
point_br = None
on_number_pad = False
write_path = 'all_boxes.txt'
#============================
def get_image(name):
	img = cv2.cvtColor(cv2.imread(name),cv2.COLOR_BGR2RGB)
	return np.array(img)

def get_image_names():
	#Get whole list
	base_dir = args.directory
	img_names = os.listdir(base_dir)
	img_names.sort()
	#Start at given name
	i = 0
	if args.start_image != 'None':
		while args.start_image != img_names[i]:
			i+=1
	return img_names[i:]
    

#================================================
#CLICK EVENT FOR LABELING
def integerize(a):
	return np.round(a).astype(np.int32)
def onclick(event):
	if event.button==1:
		on_left_click(event)
	if event.button==3:
		on_right_click(event)
def reset_tl_br():
	global top_left,point_tl,point_br,have_box,on_number_pad
	top_left = True
	point_tl,point_br = None,None
	have_box = False
	on_number_pad = False
def on_right_click(event):
	global my_image
	global last_image
	my_image = last_image.copy()
	reset_tl_br()
	redraw_image()
    

def on_left_click(event):
	"""
	Label by clicking top_left, bottom_right corners
	"""
	global top_left
	global point_tl
	global point_br
	global on_number_pad
	recent_point = (event.xdata, event.ydata)
	if recent_point[0] is not None and recent_point[1] is not None:
		recent_point = (integerize(recent_point[0]),integerize(recent_point[1]))
	else:
		redraw_image()
		return
	if on_number_pad:
		#If number pad, select number of ppl in 
		num=numberize(recent_point)
		if num is None:
			redraw_image()
			return
		else:
			write_label(num)
			load_temp_img()
			return 
	else:
		#If on image, select bounding box
		accepted=False
		if have_box:
			accepted=accept_box(recent_point)
		if accepted:
			save_temp_img()
			show_numberpad()
			return
		else:
			if top_left:
				print("Top Left: {}".format(recent_point))
				point_tl = recent_point
			else:
				print("Bottom Right: {}".format(recent_point))
				point_br = recent_point
			top_left = not top_left    
			draw_box()
			return


def accept_box(recent_point):
	"""
	Accept Box by Clicking in Middle of Box
	"""
	accepted=False
	global point_tl,point_br
	if recent_point[0]> point_tl[0] and recent_point[0]<point_br[0]:
		if recent_point[1] > point_tl[1] and recent_point[1] < point_br[1]:
			accepted = True
	return accepted



def gather_mini_image():
	global my_image,point_tl,point_br
	return my_image[point_tl[1]:point_br[1],point_tl[0]:point_br[0]]
#================================================
# NUMBER PAD LABEL	
def show_numberpad():
	mini_image = gather_mini_image()
	global my_image,on_number_pad
	on_number_pad = True
	num_image = get_image('number_pad.png')
	while mini_image.shape[0]> num_image.shape[0]:
		h,w = mini_image.shape[:2]
		mini_image = cv2.resize(mini_image,(w//2,h//2))
	padded_mini= np.zeros((num_image.shape[0],mini_image.shape[1],3),dtype=np.uint8)
	padded_mini[:mini_image.shape[0],:,:]=mini_image

	my_image = np.concatenate([num_image,padded_mini],axis=1)
	redraw_image()
def numberize(recent_point):
	divs_x = [82,164,245]
	divs_y = [54,108,162]
	
	if recent_point[0] < divs_x[0]:
		if recent_point[1]< divs_y[0]:
			return 1
		elif recent_point[1] < divs_y[1]:
			return 4
		elif recent_point[1] < divs_y[2]:
			return 7
	elif recent_point[0] < divs_x[1]:
		if recent_point[1]< divs_y[0]:
			return 2
		elif recent_point[1] < divs_y[1]:
			return 5
		elif recent_point[1] < divs_y[2]:
			return 8
		else:
			return 10
	elif recent_point[0] < divs_x[2]:
		if recent_point[1]< divs_y[0]:
			return 3
		elif recent_point[1] < divs_y[1]:
			return 6
		elif recent_point[1] < divs_y[2]:
			return 9
	return None
def save_temp_img():
	global my_image
	img = cv2.cvtColor(my_image,cv2.COLOR_BGR2RGB)
	cv2.imwrite('temp.png',img)
def load_temp_img():
	global my_image
	my_image = get_image('temp.png')
	reset_tl_br()
	remember_original()
	redraw_image()
#================================================
# DRAWING
def draw_box():
	global point_tl
	global point_br
	global my_image
	global have_box
	if point_tl is not None and point_br is not None:
		if point_tl[0] < point_br[0] and point_tl[1] < point_br[1]:
			my_image = cv2.rectangle(my_image,point_tl,point_br,(0,255,0),2)
			have_box = True

	redraw_image()
def redraw_image():
	global ax1
	global my_image
	global pause
	global current_name
	ax1.imshow(my_image)
	ax1.set_title(current_name)
	plt.draw()
	plt.waitforbuttonpress()
def remember_original():
	global my_image
	global last_image
	last_image = my_image.copy()  
    
def create_figure():
	global ax1
	f = plt.figure(figsize=(10,6))
	cid = f.canvas.mpl_connect('button_press_event', onclick)
	ax1 = plt.subplot2grid((1, 1), (0, 0), colspan=1,rowspan=1)
  
def write_label(num):
	 global write_path
	 global current_name
	 global point_tl,point_br
	 string = "{},{},{},{}".format(current_name,point_tl,point_br,num)
	 print("Added Row: {}".format(string))
	 with open(write_path,'a') as f:
		 f.write(string+'\n')
#================================================
def label_image(name):
	global my_image
	global current_name
	base_dir = args.directory
	current_name = name
	name = os.path.join(base_dir,name)
	my_image = get_image(name)
	reset_tl_br()
	remember_original()
	redraw_image()
  
def label_images(img_names):	
	create_figure()
	for name in img_names:
		label_image(name)
        

    
    

def main():
	image_names = get_image_names()
	label_images(image_names)
if __name__=="__main__":
	main()

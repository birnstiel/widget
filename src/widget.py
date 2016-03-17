#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.widgets import Slider, Button
import sys,os,subprocess,shutil
from string import ascii_letters
from random import choice
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

def main():
	x     = np.linspace(1.0, 10.0, 200)
	y     = np.linspace(1.0, 10.0, 200)
	times = np.linspace(1.0,11.0,100)
	X,Y   = np.meshgrid(x,y)
	
	data1D = np.array([t*np.sin(x*np.pi*3)+6 for t in times])
	data2D = np.zeros([len(y)*len(times),len(x)])
	
	for it in np.arange(len(times)):
		data2D[it*len(y)+np.arange(len(y)),:] = (X+Y)*np.exp(-6.0*((X-times[it])**2+(Y-times[it])**2)) 
	
	p = plotter(x,data1D,times=times,data2=[0.5*data1D,0.25*data1D+5])
	
	plotter(x,data2D,y=y,times=times,data3=[times,5.0],lstyle=[0.5*np.ones(4),'--'],ext_link=p,\
		colbar=True,show_legend=True,data_label='contours',data3_label=['line one','line two'])
	
	plt.show()

class plotter:
	def __init__(self,x,data,y=None,data2=[],data3=[],times=None,i_start=0,\
				xlog=False,ylog=False,zlog=False,xlim=None,ylim=None,zlim=None,xlabel='',ylabel='',\
				lstyle='-',ncont=None,cmap=None,ext_link=None,fill=True,bg_color='none',colbar=False,
				show_legend=False,data_label=None,data2_label=None,data3_label=None,lw=2,dpi=None,**kwargs):
		"""
		creates a GUI to display timedependent 1D or 2D data.
		
		Arguments:
		x    = the x axis array of length nx
		data = - array of the form (nt,nx) for nt 1D snapshots
			   - array of the form (nt*ny,nx) for nt 2D snapshots
		
		Keywords:
		y
		:	y axis array for data of a form (ntny,nx) where the first ny rows are the fist snapshot
		
		data2
		:	for plotting additional 1-dimensional y(x) data on the 1D or 2D plot
			join in a list if several data-sets should be included like
			[y1 , y2] where y1,y2 are arrays of shape (nt,nx)
			
		data3
		:	for plotting additional vertical lines on the 1D or 2D plot
			can be either nt points for x(t)-data or one single float if time dependent
			join to lists if more data is plotted
			 
		times
		:	times of the snapshots, to be shown in the title of the axes, if given
		
		i_start
		:	index of initial snapshot
		[x,y,z]log
		:	true: use logarithmic scale in [x,y,z]
		
		[x,y,z]lim
		:	give limits [x0,x1], ... for the specified axes    
		
		[x,y]label
		:	label for the [x,y] axes
		
		lstyle
		:	style (string or color specification) or list of styles to be used for the lines
			will be repeatet if too short
		ncont
		:	number of contours for the contour plot
		
		fill : bool
		:	if true, emulate the extend='both' behavior for contourf in logspace
		
		cmap
		:	color map for the contours
		
		ext_link
		:	link an onther plotter object to the slider of the current one
		
		bg_color : color spec
		:	background color of plot
		
		label : array of strings
		: array of strings belonging to the data, data2, data3 entries
		
		colbar : bool
		:   whether or not to add a colorbar
		
		show_legend : bool
		:	whether or not to show a legend
		
		data_label : string
		:	label for the data

		data2_label : array of strings
		:	labels for lines in data2

		data3_label : array of strings
		:	labels for lines in data3
		
		lw : int or float
		:   line width
		
		dpi : int
		:   dpi for plotting images, defaults to rcParams['figure.dpi']
		
		**kwargs : other keywords are passed to the plotting routine
		
		"""
		dpi = dpi or plt.rcParams['figure.dpi']
		#
		# general setup
		#
		if y is not None:
			if np.ndim(x)!=np.ndim(y):
				print('ERROR: x and y need to be both 1D or both 2D')
				sys.exit(1)		
			
			if (np.ndim(x)==2) and (x.shape[1]!=y.shape[1]):
				print('ERROR: x and y need to have same number of columns')
				sys.exit(1)
			
		if np.ndim(x)==1:
			nx = len(x)
		else:
			nx = x.shape[1]
			
		if y is None:
			nt = data.shape[0]
		else:
			if np.ndim(y)==1:
				ny = len(y)
			else:
				ny = x.shape[0]
			nt = data.shape[0]/ny
		#
		# check if we have a y-axis that is time dependent
		#
		y_of_t = False
		x_1D   = x
		if np.ndim(y)==2 and y.shape[0]/ny==nt:
			y_of_t=True
			x_1D = x[0,:]
			
		#
		# some size checks
		#	
		if nx!=data.shape[1]:
			print('ERROR: number of x points does not match the number of columns of the data array')
			sys.exit(1)
		if times is not None:
			if nt != len(times):
				print('ERROR: len(times) does not match (number of rows)/ny of the data array')
				sys.exit(1)
		if y is None:
			i_max  = data.shape[0]-1
		else:
			i_max  = nt-1
		#
		# color scheme 
		#
		if cmap is None: cmap=plt.get_cmap('hot')
		#
		# convert data2 if necessary
		#
		if type(data2).__name__=='ndarray':
			data2 = [data2]
		#
		# convert data3 if necessary
		#
		if type(data3).__name__=='ndarray':
			data3 = [data3]
		#
		# convert to arrays
		#
		for i in np.arange(len(data3)):
			data3[i]=np.array(data3[i],ndmin=1)
		#
		# set limits
		#
		if xlim is None: xlim=[x.min(),x.max()]
		if ylim is None:
			if y is None:
				ylim=[data.min(),data.max()]
			else:
				ylim=[y.min(),y.max()]
		if zlim is None: zlim=[data.min(),data.max()]
		#
		# set logarithmic color axis
		#
		if zlog:
			#data=np.log10(data)
			#zlim=np.log10(zlim)
			norm = LogNorm()
			if ncont is None:
				zax = 10.**np.arange(np.ceil(np.log10(zlim[0])),np.floor(np.log10(zlim[-1]))+1)
			else:
				zax = np.logspace(np.log10(zlim[0]),np.log10(zlim[-1]),ncont)
			if zax[0]>zlim[0]:
				zax = np.append(zlim[0],zax)
			if zax[-1]<zlim[-1]:
				zax = np.append(zax,zlim[-1])
			ncont = len(zax)
		else:
			norm = None    
			if ncont is None: ncont = 10
			zax = np.linspace(zlim[0],zlim[1],ncont)
		#
		# add floor value
		#
		if fill:
			data = np.maximum(data,zlim[0])
		#
		# set line styles
		#
		if type(lstyle).__name__!='list': lstyle=[lstyle]
		len_ls0 = len(lstyle)
		len_ls1 = len(data2)+len(data3)+1
		dummy = []
		for j in np.arange(len_ls1):
			dummy += [lstyle[np.mod(j,len_ls0)]]
		lstyle = dummy
		#
		# set up figure
		#
		plt.figure(facecolor=bg_color)
		#
		# ===============
		# INITIAL DRAWING
		# ===============
		#
		ax    = plt.subplot(111,axisbg=bg_color)
		plt.subplots_adjust(left=0.25, bottom=0.25)
		plt.axis([xlim[0], xlim[1], ylim[0], ylim[1]])
		#
		# draw labels
		#
		if xlabel!='': plt.xlabel(xlabel)
		if ylabel!='': plt.ylabel(ylabel)
		if times is not None: ti=plt.title('%g'%times[i_start])
		#
		# set scales
		#
		if xlog: ax.set_xscale('log')
		if ylog: ax.set_yscale('log')
		#
		# make empty labels if none are passed
		#
		if data_label  is None: data_label = ''
		if data2_label is None: data2_label=['']*len(data2)
		if data3_label is None: data3_label=['']*len(data3)
		#
		# plot the normal data
		#
		if y is None:
			#
			# line data
			#
			if type(lstyle[0]).__name__=='str':
				l, = ax.plot(x,data[i_start],lstyle[0],lw=lw,label=data_label)
			else:
				l, = ax.plot(x,data[i_start],color=lstyle[0],lw=lw,label=data_label)
		else:
			#
			# 2D data
			#
			if y_of_t:
				l  = ax.contourf(x,y[i_start*ny+np.arange(ny),:],data[i_start*ny+np.arange(ny),:],zax,cmap=cmap,norm=norm,label=data_label,**kwargs)
				clist = l.collections[:]
			else:
				l  = ax.contourf(x,y,data[i_start*ny+np.arange(ny),:],zax,cmap=cmap,norm=norm,label=data_label,**kwargs)
				clist = l.collections[:]
		#
		# plot additional line data
		#
		add_lines = []
		for j,d in enumerate(data2):
			if type(lstyle[j+1]).__name__=='str':
				l2, = ax.plot(x_1D,d[i_start,:],lstyle[j+1],lw=lw,label=data2_label[j])
			else:
				l2, = ax.plot(x_1D,d[i_start,:],color=lstyle[j+1],lw=lw,label=data2_label[j])
			add_lines+=[l2]
		#
		# plot additional vertical lines
		#
		add_lines2 = []
		for j,d in enumerate(data3):
			if type(lstyle[j+1]).__name__=='str':
				l3, = ax.plot(d[min(i_start,len(d)-1)]*np.ones(2),ax.get_ylim(),lstyle[j+1+len(data2)],lw=lw,label=data3_label[j])
			else:
				l3, = ax.plot(d[min(i_start,len(d)-1)]*np.ones(2),ax.get_ylim(),color=lstyle[j+1+len(data2)],lw=lw,label=data3_label[j])
			add_lines2+=[l3]
		if show_legend:
			leg=ax.legend()
			leg.get_frame().set_facecolor(bg_color)
			leg.get_frame().set_edgecolor('none')
		#
		# add colorbar
		#
		if colbar:
			divider = make_axes_locatable(ax)  
			cax     = divider.append_axes("right", size="5%", pad=0.05)  
			plt.colorbar(l, cax=cax);
		#
		# ========
		# Make GUI
		# ========
		#
		#
		# make time slider
		#
		axcolor     = 'lightgoldenrodyellow'
		ax_time     = plt.axes([0.25, 0.1, 0.65, 0.03], axisbg=axcolor)
		slider_time = Slider(ax_time, 'time', 0.0, i_max, valinit=i_start,valfmt='%i')
		self.slider = slider_time
		ax._widgets = [slider_time] # avoids garbage collection
		#
		# define slider update funcion
		#
		def update(val):
			i = int(np.floor(slider_time.val))
			if y is None:
				#
				# update line data
				#
				l.set_ydata(data[i])
			else:
				#
				# update 2D data
				#			
				while len(clist)!=0:
					for col in clist:
						ax.collections.remove(col)
						clist.remove(col)
				if y_of_t:
					dummy  = ax.contourf(x,y[i*ny+np.arange(ny),:],data[i*ny+np.arange(ny),:],zax,norm=norm,cmap=cmap,**kwargs)
				else:
					dummy  = ax.contourf(x,y,data[i*ny+np.arange(ny),:],zax,norm=norm,cmap=cmap,**kwargs)
				if colbar: plt.colorbar(dummy, cax=cax);
				for d in dummy.collections: clist.append(d)
			#
			# update additional lines
			#
			for d,l2 in zip(data2,add_lines):
				l2.set_ydata(d[i])
			#
			# update additional vertical lines
			#
			for d,l3 in zip(data3,add_lines2):
				l3.set_xdata(d[min(i,len(d)-1)])
				l3.set_ydata(ax.get_ylim())
			#
			# update title
			#
			if times is not None: ti.set_text('%g'%times[i])
			#
			# update plot
			#
			plt.draw()
			#
			# update external plotter as well
			#
			if ext_link is not None: ext_link.slider.set_val(slider_time.val)
		slider_time.on_changed(update)
		#
		# set xlog button
		#
		ax_xlog = plt.axes([0.5, 0.025, 0.1, 0.04])
		button_xlog = Button(ax_xlog, 'xscale', color=axcolor, hovercolor='0.975')
		ax._widgets += [button_xlog] # avoids garbage collection
		def xlog_callback(event):
			if ax.get_xscale() == 'log':
				ax.set_xscale('linear')
			else:
				ax.set_xscale('log')
			plt.draw()
		button_xlog.on_clicked(xlog_callback)
		#
		# set ylog button
		#
		ax_ylog = plt.axes([0.6, 0.025, 0.1, 0.04])
		button_ylog = Button(ax_ylog, 'yscale', color=axcolor, hovercolor='0.975')
		ax._widgets += [button_ylog] # avoids garbage collection
		def ylog_callback(event):
			if ax.get_yscale() == 'log':
				ax.set_yscale('linear')
			else:
				ax.set_yscale('log')
			plt.draw()
		button_ylog.on_clicked(ylog_callback)
		#
		# plot button
		#
		ax_plotbutton = plt.axes([0.8, 0.025, 0.1, 0.04])
		button_plot = Button(ax_plotbutton, 'plot', color=axcolor, hovercolor='0.975')
		def plotbutton_callback(event,img_name=None,img_format='.pdf'):
			# ===================================================
			# this part is copied from above, replacing ax=>newax
			# and getting the snapshot index from the slider
			# ===================================================
			#
			newfig=plt.figure(facecolor=bg_color);
			newax    = plt.subplot(111,axisbg=bg_color);
			i        = int(np.floor(slider_time.val));
			plt.axis([xlim[0], xlim[1], ylim[0], ylim[1]]);
			#
			# draw labels
			#
			if xlabel!='': plt.xlabel(xlabel)
			if ylabel!='': plt.ylabel(ylabel)
			if times is not None: ti=plt.title('%g'%times[i])
			#
			# set scales
			#
			if xlog: newax.set_xscale('log')
			if ylog: newax.set_yscale('log')
			#
			# plot the normal data
			#
			if y is None:
				#
				# line data
				#
				if type(lstyle[0]).__name__=='str':
					l, = newax.plot(x_1D,data[i],lstyle[0],lw=lw,label=data_label)
				else:
					l, = newax.plot(x_1D,data[i],color=lstyle[0],lw=lw,label=data_label)
			else:
				#
				# 2D data
				#
				if y_of_t:
					l  = newax.contourf(x,y[i*ny+np.arange(ny),:],data[i*ny+np.arange(ny),:],zax,norm=norm,cmap=cmap,label=data_label,**kwargs)
					clist = l.collections[:]
				else:
					l  = newax.contourf(x,y,data[i*ny+np.arange(ny),:],zax,norm=norm,cmap=cmap,label=data_label,**kwargs)
					clist = l.collections[:]
				if colbar:
					divider = make_axes_locatable(newax)  
					newcax  = divider.append_axes("right", size="5%", pad=0.05)  
					plt.colorbar(l, cax=newcax);
			#
			# plot additional line data
			#
			add_lines = []
			for j,d in enumerate(data2):
				if type(lstyle[j+1]).__name__=='str':
					l2, = newax.plot(x_1D,d[i,:],lstyle[j+1],lw=lw,label=data2_label[j])
				else:
					l2, = newax.plot(x_1D,d[i,:],color=lstyle[j+1],lw=lw,label=data2_label[j])
				add_lines+=[l2]
			#
			# plot additional vertical lines
			#
			add_lines2 = []
			for j,d in enumerate(data3):
				if type(lstyle[j+1]).__name__=='str':
					l3, = newax.plot(d[min(i,len(d)-1)]*np.ones(2),newax.get_ylim(),lstyle[j+1+len(data2)],lw=lw,label=data3_label[j])
				else:
					l3, = newax.plot(d[min(i,len(d)-1)]*np.ones(2),newax.get_ylim(),color=lstyle[j+1+len(data2)],lw=lw,label=data3_label[j])
				add_lines2+=[l3]
			if show_legend:
				leg=newax.legend()
				leg.get_frame().set_facecolor(bg_color)
				leg.get_frame().set_edgecolor('none')
			#
			# =========================================
			# now set the limits as in the other figure
			# =========================================
			#
			newax.set_xlim(ax.get_xlim())
			newax.set_ylim(ax.get_ylim())
			newax.set_xscale(ax.get_xscale())
			newax.set_yscale(ax.get_yscale())
			#
			# =========================================
			# now set the limits as in the other figure
			# =========================================
			#
			if '.' not in img_format: img_format = '.'+img_format
			if img_name is None:
				j=0
				while os.path.isfile('figure_%03i%s'%(j,img_format)): j+=1
				img_name = 'figure_%03i%s'%(j,img_format)
			else:
				img_name = img_name.replace(img_format,'')+img_format
			plt.savefig(img_name,facecolor=bg_color,dpi=dpi)
			print('saved %s'%img_name)
			plt.close(newfig)
		button_plot.on_clicked(plotbutton_callback)
		ax._widgets += [button_plot] # avoids garbage collection
		#
		# plot button
		#
		ax_moviebutton = plt.axes([0.7, 0.025, 0.1, 0.04])
		button_movie = Button(ax_moviebutton, 'movie', color=axcolor, hovercolor='0.975')
		def moviebutton_callback(event):
			dirname    = 'movie_images_'+''.join(choice(ascii_letters) for x in range(5))
			img_format = '.png'
			#
			# create folder
			#
			if os.path.isdir(dirname):
				print('WARNING: %s folder already exists, please delete it first'%dirname)
				return
			else:
				os.mkdir(dirname)
			#
			# save all the images
			#
			i0 = int(np.floor(slider_time.val))
			for j,i in enumerate(np.arange(i0,nt)):
				slider_time.set_val(i)
				plotbutton_callback(None,img_name=dirname+os.sep+'img_%03i'%j, img_format=img_format);
			#
			# create the movie
			#
			moviename = 'movie.mp4'
			i_suffix  = 0
			dummy     = moviename
			while os.path.isfile(dummy):
				i_suffix += 1
				dummy     = moviename.replace('.', '_%03i.'%i_suffix)
			moviename = dummy
			
			ret=subprocess.call(['ffmpeg','-i',dirname+os.sep+'img_%03d'+img_format,'-c:v','libx264','-crf','20','-maxrate','400k','-pix_fmt','yuv420p','-bufsize','1835k',moviename]);
			if ret==0:
				#
				# delete the images & the folder
				#
				for j,i in enumerate(np.arange(i0,nt)):
					os.remove(dirname+os.sep+'img_%03i%s'%(j,img_format))
				shutil.rmtree(dirname)
				print('*** Movie successfully created ***')
			else:
				print('WARNING: movie could not be produced, keeping images')
			#
			# reset slider
			#
			slider_time.set_val(i0)
		button_movie.on_clicked(moviebutton_callback)
		ax._widgets += [button_movie] # avoids garbage collection
		#
		# make ax current axes, so that it is easier to interact with
		#
		plt.axes(ax)
		#
		# GO
		#
		plt.draw()
	
if __name__ == "__main__":
	main()


#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import sys
import os

def main():
	x     = np.linspace(1.0, 10.0, 200)
	y     = np.linspace(1.0, 10.0, 200)
	times = np.linspace(1.0,11.0,100)
	X,Y   = np.meshgrid(x,y)
	
	data1D = np.array([t*np.sin(x*np.pi*3)+6 for t in times])
	data2D = np.zeros([len(y)*len(times),len(x)])
	
	for it in np.arange(len(times)):
		data2D[it*len(y)+np.arange(len(y)),:] = (X+Y)*np.exp(-6.0*((X-times[it])**2+(Y-times[it])**2)) 
	
	plotter(x,data1D,times=times,data2=[0.5*data1D,0.25*data1D+5])
	
	plotter(x,data2D,y=y,times=times,data2=data1D)
	
	plt.show()

def plotter(x,data,y=None,data2=[],times=None,i_start=0,xlog=False,ylog=False,zlog=False,xlim=None,ylim=None,zlim=None,xlabel='',ylabel='',lstyle='-',ncont=None,cmap=None,fill=True):
	"""
	creates a GUI to display timedependent 1D or 2D data.
	
	Arguments:
	x    = the x axis array of length nx
	data = array of the form (nt,nx) for nt snapshots
	
	Keywords:
	*y*     		y axis array for data of a form (nt*ny,nx) where the first ny rows are the fist snapshot
	*data2*			for plotting additional data (only 1D data) on the 1D or 2D plot
	*times*			times of the snapshots, to be shown in the title of the axes
	*i_start*		index of initial snapshot
	*[x,y,z]log* 	true: use logarithmic scale in [x,y,z]
	*[x,y,z]lim*	give limits [x0,x1], ... for the specified axes    
	*[x,y]label*	label for the [x,y] axes
	lstyle			style to be used for the lines
	*ncont*			number of contours for the contour plot
	*cmap*			color map for the contours
	*fill*			if true, data lower than zlim[0] will be rendered at lowest color level
					if false, will be rendered white 
	"""
	#
	# general setup
	#
	if y==None:
		nt,nx = data.shape
	else:
		nx = data.shape[1]
		ny = len(y)
		nt = data.shape[0]/ny
	#
	# some size checks
	#	
	if nx!=len(x):
		print('ERROR: len(x) does not match the number of columns of the data array')
		sys.exit(1)
	if times!=None:
		if nt != len(times):
			print('ERROR: len(times) does not match (number of rows)/ny of the data array')
			sys.exit(1)
	if y==None:
		i_max  = data.shape[0]-1
	else:
		i_max  = nt-1
	#
	# color scheme 
	#
	if cmap==None: cmap='hot'
	#
	# convert data2 if necessary
	#
	if type(data2).__name__=='ndarray':
		data2 = [data2]
	#
	# set limits
	#
	if xlim==None: xlim=[x[0],x[-1]]
	if ylim==None:
		if y==None:
			ylim=[data.min(),data.max()]
		else:
			ylim=[y[0],y[-1]]
	if zlim==None: zlim=[data.min(),data.max()]
	#
	# zlog cannot just be set, we need to convert the data
	#
	if zlog:
		data=np.log10(data)
		zlim=np.log10(zlim)
	#
	# add floor value
	#
	if fill:
		data = np.maximum(data,zlim[0])
	#
	# set number of contours
	#
	if ncont==None:
		ncont=zlim[-1]-zlim[0]+1
	#
	# set up figure
	#
	plt.figure()
	#
	# ===============
	# INITIAL DRAWING
	# ===============
	#
	ax    = plt.subplot(111)
	plt.subplots_adjust(left=0.25, bottom=0.25)
	plt.axis([xlim[0], xlim[1], ylim[0], ylim[1]])
	#
	# draw labels
	#
	if xlabel!='': plt.xlabel(xlabel)
	if ylabel!='': plt.ylabel(ylabel)
	if times!=None: ti=plt.title('%g'%times[i_start])
	#
	# set scales
	#
	if xlog: ax.set_xscale('log')
	if ylog: ax.set_yscale('log')
	#
	# plot the normal data
	#
	if y==None:
		#
		# line data
		#
		l, = ax.plot(x,data[i_start], lw=2,ls=lstyle)
	else:
		#
		# 2D data
		#
		l  = ax.contourf(x,y,data[i_start*ny+np.arange(ny),:],np.linspace(zlim[0],zlim[-1],ncont),cmap=cmap)
		clist = l.collections[:]
	#
	# plot additional line data
	#
	add_lines = []
	for d in data2:
		l2, = ax.plot(x,d[i_start], lw=2,ls=lstyle)
		add_lines+=[l2]
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
	#
	# define slider update funcion
	#
	def update(val):
		i = int(round(slider_time.val))
		if y==None:
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
			dummy  = ax.contourf(x,y,data[i*ny+np.arange(ny),:],np.linspace(zlim[0],zlim[-1],ncont),cmap=cmap)
			for d in dummy.collections:
				clist.append(d)
		#
		# update additional lines
		#
		for d,l2 in zip(data2,add_lines):
			l2.set_ydata(d[i])
		#
		# update title
		#
		if times!=None: ti.set_text('%g'%times[i])
		#
		# update plot
		#
		plt.draw()
	slider_time.on_changed(update)
	#
	# set xlog button
	#
	ax_xlog = plt.axes([0.5, 0.025, 0.1, 0.04])
	button_xlog = Button(ax_xlog, 'xscale', color=axcolor, hovercolor='0.975')
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
	def plotbutton_callback(event):
		# ===================================================
		# this part is copied from above, replacing ax=>newax
		# and getting the snapshot index from the slider
		# ===================================================
		#
		newfig=plt.figure()
		newax    = plt.subplot(111)
		i        = int(round(slider_time.val))
		plt.axis([xlim[0], xlim[1], ylim[0], ylim[1]])
		#
		# draw labels
		#
		if xlabel!='': plt.xlabel(xlabel)
		if ylabel!='': plt.ylabel(ylabel)
		if times!=None: ti=plt.title('%g'%times[i])
		#
		# set scales
		#
		if xlog: newax.set_xscale('log')
		if ylog: newax.set_yscale('log')
		#
		# plot the normal data
		#
		if y==None:
			#
			# line data
			#
			l, = newax.plot(x,data[i], lw=2,ls=lstyle)
		else:
			#
			# 2D data
			#
			l  = newax.contourf(x,y,data[i*ny+np.arange(ny),:],np.linspace(zlim[0],zlim[-1],ncont),cmap=cmap)
			clist = l.collections[:]
		#
		# plot additional line data
		#
		add_lines = []
		for d in data2:
			l2, = newax.plot(x,d[i], lw=2,ls=lstyle)
			add_lines+=[l2]
		#
		# =========================================
		# now set the limits as in the other figure
		# =========================================
		newax.set_xlim(ax.get_xlim())
		newax.set_ylim(ax.get_ylim())
		newax.set_xscale(ax.get_xscale())
		newax.set_yscale(ax.get_yscale())
		#
		# set the original figure active again
		#
		j=0
		while os.path.isfile('figure_%03i.pdf'%j): j+=1
		fname = 'figure_%03i.pdf'%j
		plt.savefig(fname)
		print('saved %s'%fname)
		plt.close(newfig)
	button_plot.on_clicked(plotbutton_callback)
	#
	# GO
	#
	plt.show()
	
if __name__ == "__main__":
	main()
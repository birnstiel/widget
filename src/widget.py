import numpy as np
import glob
import matplotlib.pyplot as plt
#from matplotlib import colorbar
from matplotlib.widgets import Button

class plotter:
    #
    # the initialization
    #
    def __init__(self,x=[],y=[],data=[],times=[],i_start=0,xlog=0,ylog=0,zlog=0,xlim=[],ylim=[],zlim=[],
        xlabel='',ylabel='',lstyle='-',
        data2=[],transparent=True):
        self.transparent=transparent
        self.fig=plt.figure()
        #
        # some fiducial data if no data is given 
        #
        if (x==[])&(data==[]):
            self.times = np.arange(2, 20, 1)
            self.freq  = np.arange(2, 20, 1)
            self.x     = np.arange(0.0, 1.0, 0.001)
            self.data  = np.zeros([len(self.times),len(self.x)])
            for j in np.arange(0,len(self.times),1):
                self.data[j] = np.sin(2*np.pi*self.freq[j]*self.x)
            self.data2 = []
            self.oneD  = 1
        else:
            self.x     = x
            self.data  = data
            self.data2 = data2
            self.xlim  = xlim
            self.ylim  = ylim
            self.zlim  = zlim
            #
            # distinguish between 1D and 2D version
            #
            self.y = y
            if not(y==[]):
                self.oneD = 0
                self.n_t  = self.data.shape[0]/len(y)
            else:
                self.oneD = 1
                self.n_t  = self.data.shape[0]
        #
        # if no time is given, make an index
        #
        if (times==[]):
            self.times = np.arange(0, self.data.shape[0], 1)
        else:
            self.times = times
        #
        # save the number of grid points
        #   
        self.n_x   = len(self.x)
        self.n_y   = len(self.y)
        #
        # wether or not x or y are logarithmic
        #
        self.lstyle    = lstyle
        self.xlog      = xlog
        self.ylog      = ylog
        self.zlog      = zlog
        self.show_time = 1
        self.xlabel    = xlabel
        self.ylabel    = ylabel
        self.ind       = i_start
        #
        # the setup
        #
        self.ax = plt.subplot(111)
        plt.subplots_adjust(bottom=0.2)
        #
        # buttons to go +1 or -1
        #
        self.ax_f = plt.axes([0.50, 0.05, 0.05, 0.05])
        self.ax_r = plt.axes([0.45, 0.05, 0.05, 0.05])
        self.b_f = Button(self.ax_f, '>')
        self.b_f.on_clicked(self.f)
        self.b_r = Button(self.ax_r, '<')
        self.b_r.on_clicked(self.r)
        #
        # buttons to go +10 or -10
        #
        self.ax_ff = plt.axes([0.55, 0.05, 0.05, 0.05])
        self.ax_rr = plt.axes([0.40, 0.05, 0.05, 0.05])
        self.b_ff = Button(self.ax_ff, '>>')
        self.b_ff.on_clicked(self.ff)
        self.b_rr = Button(self.ax_rr, '<<')
        self.b_rr.on_clicked(self.rr)
        #
        # buttons to go to start or end
        #
        self.ax_fff = plt.axes([0.60, 0.05, 0.05, 0.05])
        self.ax_rrr = plt.axes([0.35, 0.05, 0.05, 0.05])
        self.b_fff = Button(self.ax_fff, '|>')
        self.b_fff.on_clicked(self.fff)
        self.b_rrr = Button(self.ax_rrr, '<|')
        self.b_rrr.on_clicked(self.rrr)
        #
        # the log buttons
        #
        self.ax_xlog = plt.axes([0.70, 0.05, 0.05, 0.05])
        self.ax_ylog = plt.axes([0.75, 0.05, 0.05, 0.05])
        self.b_xlog = Button(self.ax_xlog, 'xlog')
        self.b_xlog.on_clicked(self.setxlog)
        self.b_ylog = Button(self.ax_ylog, 'ylog')
        self.b_ylog.on_clicked(self.setylog)
        #
        # the print button
        #
        self.ax_print = plt.axes([0.85, 0.05, 0.075, 0.05])
        self.b_print  = Button(self.ax_print, 'print')
        self.b_print.on_clicked(self.printfig)
        #
        # call the plotcommand to
        # print the initial frame
        #
        self.plotcommand(0)
        plt.show()
    #
    # the forward and backward commands
    #
    def f(self, event):
        self.ind += 1
        if (self.ind > self.n_t-1):
            self.ind = self.n_t-1            
        self.plotcommand(self.ind)
        
    def ff(self, event):
        self.ind += 10
        if (self.ind > self.n_t-1):
            self.ind = self.n_t-1            
        self.plotcommand(self.ind)
        
    def fff(self, event):
        self.ind = self.n_t-1
        self.plotcommand(self.ind)

    def r(self, event):
        self.ind -= 1
        if (self.ind < 0):
            self.ind = 0
        self.plotcommand(self.ind)
        
    def rr(self, event):
        self.ind -= 10
        if (self.ind < 0):
            self.ind = 0
        self.plotcommand(self.ind)
        
    def rrr(self, event):
        self.ind = 0
        self.plotcommand(self.ind)
        
    def setxlog(self,event):
        if self.xlog==1:
            self.xlog = 0
            self.ax.set_xscale('linear')
            self.b_xlog.label.set_text('xlog')
        else:
            self.xlog = 1
            self.ax.set_xscale('log')
            self.b_xlog.label.set_text('xlin')
        plt.draw()
    
    def setylog(self,event):
        if self.ylog==1:
            self.ylog = 0
            self.ax.set_yscale('linear')
            self.b_ylog.label.set_text('xlog')
        else:
            self.ylog = 1
            self.ax.set_yscale('log')
            self.b_ylog.label.set_text('xlin')
        plt.draw()

    def printfig(self,event):
        #
        # create figure & axes
        #
        F=plt.figure()
        A=plt.axes()
        if self.transparent==True:
            A.set_axis_bgcolor('none')
        #
        # plot it
        #
        self.plotcommand(self.ind,AX=A)
        #
        # determine file name
        #
        i=len(glob.glob('figure_???.pdf'))+1
        fname = 'figure_'+str(i).zfill(3)+'.pdf'
        if self.transparent==True:
            plt.savefig(fname, facecolor='none', edgecolor='none')
        else:
            plt.savefig(fname)        
        print 'saved as '+fname
        plt.close(F)
    #
    # this function does the actual drawing
    #
    def plotcommand(self,i,AX=None):
        if AX==None:
            AX=self.fig.get_axes()[0]
        #
        # if l does not exist yet (i.e. first call)
        # then create it
        #
        AX.clear()
        #
        # if 1D plot
        #
        if (self.oneD==1):
            AX.plot(self.x, self.data[i],self.lstyle,lw=2,markerfacecolor='none')
            if not(self.data2==[]):
                AX.plot(self.x, self.data2[i],self.lstyle,lw=2,markerfacecolor='none')
        #
        # if 2D plot
        #
        else:
            if (self.zlog==1):
                if (self.zlim==[]):
                    Z    = np.log10(self.data[i*self.n_y+np.arange(0,self.n_y),:])
                    AX.contourf(self.x,self.y,Z)
                else:
                    Z    = np.log10(self.zlim[0]+
                        self.data[i*self.n_y+np.arange(0,self.n_y),:])
                    AX.contourf(self.x,self.y,Z,
                        np.arange(np.log10(self.zlim[0]),np.log10(self.zlim[1])))
                    plt.hot()
            else:
                if (self.zlim==[]):
                    Z    = self.data[i*self.n_y+np.arange(0,self.n_y),:]
                    AX.contourf(self.x,self.y,Z)
                else:
                    Z    = self.data[i*self.n_y+np.arange(0,self.n_y),:]+self.zlim[0]
                    AX.contourf(self.x,self.y,Z,np.arange(self.zlim[0],self.zlim[1]))
        #
        # log or lin axes
        #
        if (self.xlog==1):
            AX.set_xscale('log')
        if (self.ylog==1):
            AX.set_yscale('log')
        #
        # limits
        #
        if not(self.xlim==[]):
            AX.set_xlim(self.xlim)
        if not(self.ylim==[]):
            AX.set_ylim(self.ylim)
        #
        # title
        #
        if (self.show_time == 1):
            AX.set_title(self.times[i])
        #
        # labels
        #
        AX.set_xlabel(self.xlabel)
        AX.set_ylabel(self.ylabel)
        #
        # draw the plot
        #
        plt.draw()


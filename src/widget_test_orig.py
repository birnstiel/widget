import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
#
# this function does the actual drawing
#
def plotcommand(i):
    #
    # if l does not exist yet (i.e. first call)
    # then create it
    #
    ax.clear()
    ydata = np.sin(2*np.pi*times[i]*x)
    ax.plot(x, ydata, lw=2)
    #
    # title
    #
    if (show_time == 1):
        ax.set_title(i)
    #
    # labels
    #
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    #
    # draw the plot
    #
    plt.draw()
    
class Index:
    ind = 0
    #
    # the forward and backward commands
    #
    def f(self, event):
        self.ind += 1
        if (self.ind > n_t-1):
            self.ind = n_t-1            
        plotcommand(self.ind)
        
    def ff(self, event):
        self.ind += 10
        if (self.ind > n_t-1):
            self.ind = n_t-1            
        plotcommand(self.ind)
        
    def fff(self, event):
        self.ind = len(times)-1
        plotcommand(self.ind)

    def r(self, event):
        self.ind -= 1
        if (self.ind < 0):
            self.ind = 0
        plotcommand(self.ind)
        
    def rr(self, event):
        self.ind -= 10
        if (self.ind < 0):
            self.ind = 0
        plotcommand(self.ind)
        
    def rrr(self, event):
        self.ind = 0
        plotcommand(self.ind)
        
    def setxlog(self,event):
        global xlog
        if xlog==1:
            xlog = 0
            ax.set_xscale('linear')
        else:
            xlog = 1
            ax.set_xscale('log')
        plt.draw()
    
    def setylog(self,event):
        global ylog
        if ylog==1:
            ylog = 0
            ax.set_yscale('linear')
        else:
            ylog = 1
            ax.set_yscale('log')
        plt.draw()
#
# end of the definitions
# now comes the setup
#
################
# the time array
################
times = np.arange(2, 20, 1)
n_t   = len(times)
#
# wether or not x or y are logarithmic
#
xlog      = 0
ylog      = 0
show_time = 1
xlabel    = ''
ylabel    = ''
#
# the setup
#
ax = plt.subplot(111)
plt.subplots_adjust(bottom=0.2)
x = np.arange(0.0, 1.0, 0.001)
s = np.sin(2*np.pi*times[0]*x)
callback = Index()
#
# buttons to go +1 or -1
#
ax_f = plt.axes([0.50, 0.05, 0.05, 0.05])
ax_r = plt.axes([0.45, 0.05, 0.05, 0.05])
b_f = Button(ax_f, '>')
b_f.on_clicked(callback.f)
b_r = Button(ax_r, '<')
b_r.on_clicked(callback.r)
#
# buttons to go +10 or -10
#
ax_ff = plt.axes([0.55, 0.05, 0.05, 0.05])
ax_rr = plt.axes([0.40, 0.05, 0.05, 0.05])
b_ff = Button(ax_ff, '>>')
b_ff.on_clicked(callback.ff)
b_rr = Button(ax_rr, '<<')
b_rr.on_clicked(callback.rr)
#
# buttons to go to start or end
#
ax_fff = plt.axes([0.60, 0.05, 0.05, 0.05])
ax_rrr = plt.axes([0.35, 0.05, 0.05, 0.05])
b_fff = Button(ax_fff, '|>')
b_fff.on_clicked(callback.fff)
b_rrr = Button(ax_rrr, '<|')
b_rrr.on_clicked(callback.rrr)
#
# the log buttons
#
ax_xlog = plt.axes([0.70, 0.05, 0.05, 0.05])
ax_ylog = plt.axes([0.75, 0.05, 0.05, 0.05])
b_xlog = Button(ax_xlog, 'xlog')
b_xlog.on_clicked(callback.setxlog)
b_ylog = Button(ax_ylog, 'ylog')
b_ylog.on_clicked(callback.setylog)
#
# call the plotcommand to
# print the initial frame
#
plotcommand(0)
plt.show()

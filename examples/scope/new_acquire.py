'''Test the BitScope Library by connecting with the first available device's channel A(index=0)
and performing continuous trace and acquire. Requires BitLib 2.0 and Python Bindings

Only performs capture and realtime plot for ONE device, over channel A, which receives the trigger

B.Sudarsan
sudarsan.sboa@gmail.com
'''
#Import required libraries
from bitscope import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

TRUE = 1
FALSE =0

#Create one set of figure, axis objects to draw graph
fig, ax = plt.subplots()

#Setup general parameters for the capture
MY_RATE = 1000000 # default sample rate in Hz we'll use for capture.
MY_SIZE = 12288 # number of samples we'll capture - 12288 is the maximum size

#Variable to store y-axis data
DATA = np.random.rand(MY_SIZE)

#Vector storing time-data for x-axis
x = np.arange(MY_SIZE)/float(MY_RATE)

line, = ax.plot(x,np.array(DATA))	
#'line' is now the data-curve in the figure, which can be updated for animation.

#Label the axes in the plot
ax.set_xlabel("Time in sec")
ax.set_ylabel("Signal in Volts")

scope = ""

#Define the function to animate the plot by updating the data-curve in the figure.
def animate(i):
    #Makes sure the updated variables are the ones declared in the global scope
    global DATA,fig,ax,scope

    #Capture analog data synchronously to the Bitscope device's buffer.
    #If a trigger event is not received in 0.1sec, auto trigger happens.
    #BL_Trace(), when without any arguments, captures immediately, no trigger needed.
    print "trace {}".format(scope.tracer.trace(0.01, BL_SYNCHRONOUS))
    
    #Transfer the captured data to our PC's memory using the USB link
    # DATA = BL_Acquire()
    DATA = scope.devices[0].channels[0].acquire()

    #Update the plot's data-curve with the new data
    line.set_ydata(np.array(DATA))

    #Rescale the axes of the plot, just in case
    ax.relim()
    ax.autoscale_view()

    #We're required to return anything that is updated in the plot
    #for Funcanimate to work correctly.
    return line,

#Function to initialize the figure, plots random data to 'line'
def init():
    line.set_ydata(np.random.rand(12288))
    return line,

def main(argv=None):
    print "Starting: Attempting to open one devices..."

    global scope

    #Attempt to open 1 device at /dev/ttyUSBx
    #Make sure you run 'cd /dev/' followed by 'ls ' on terminal to see if the device is present. 
    scope = Scope('USB:/dev/ttyUSB1',1)
    #See return value to see the number of successfully opened devices.
    if (len(scope.devices)==0):
         print "  FAILED: all devices not found (check your probe file)."    
    else:
        #Successfully opened one device
        #Report the number of devices opened, and the library version used
        print '\nNumber of devices opened: %s' %len(scope.devices)
        print " Library: %s (%s)\n\n" % (scope.version(BL_VERSION_LIBRARY),scope.version(BL_VERSION_BINDING))

        #Setup acquisition in FAST mode, where the whole of the 12288 samples in
        #the buffer are used by one channel alone.
        scope.devices[0].mode(BL_MODE_FAST)
        
        #Report the capture details
        # print " Capture: %d @ %.0fHz = %fs" % (BL_Size(),BL_Rate(MY_RATE),BL_Time())
        print " Capture: %d @ %.0fHz = %fs" % (scope.tracer.size(),scope.tracer.rate(MY_RATE),scope.tracer.time())

        #Setup channel-nonspecific parameters for capture.
        # BL_Intro(BL_ZERO); #How many seconds to capture before the trigger event- 0 by default
        # BL_Delay(BL_ZERO); #How many seconds to capture after the trigger event- 0 by default
        # BL_Rate(MY_RATE); # optional, default BL_MAX_RATE
        # BL_Size(MY_SIZE); # optional default BL_MAX_SIZE
        scope.tracer.configure(MY_RATE,MY_SIZE,BL_ZERO,BL_ZERO)

        #Set up channel A properties - A has channel index 0, B has 1.
        #All the subsequent properties belong to channel A until another is selected.
        # scope.devices[0].channels[0].select()

        #Setup a falling-edge trigger at 0.999V.
        #Other options are BL_TRIG_RISE, BL_TRIG_HIGH, BL_TRIG_LOW.
        # BL_Trigger(0.999,BL_TRIG_FALL); # This is optional when untriggered BL_Trace() is used
        scope.tracer.trigger(0.999,BL_TRIG_FALL)

        # BL_Select(BL_SELECT_SOURCE,BL_SOURCE_POD); # use the POD input - the only one available
        # BL_Range(BL_Count(BL_COUNT_RANGE)); # maximum range for y-axis - use this whenever possible
        # BL_Offset(BL_ZERO); # Y-axis offset is set to zero as BL_ZERO
        scope.devices[0].channels[0].configure(BL_SOURCE_POD,BL_ZERO,BL_Count(BL_COUNT_RANGE),BL_COUPLING_DC)
        #Enable the currently selected channel, i.e. channel A
        #This ensures the recorded data goes into the memory-buffer in Bitscope device
        scope.devices[0].channels[0].enable()
        
        print " Bitscope Enabled"
        
        #The following call animates the figure 'fig'('fig' is initialized using 'init') using the function 'animate'
        #There are 200 frames preserved in memory, and refresh rate is 5ms.
        ani = animation.FuncAnimation(fig, animate, np.arange(1,200), init_func=init, interval=5)#, blit=True)

        #Display the animated plot.
        plt.show()

        print "Finished: Library closed, resources released."

#A fancy, yet common way of running a python script
#Makes it resemble a C program code
if __name__ == "__main__":
    import sys
    sys.exit(main())
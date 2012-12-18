#!/usr/bin/python
#Needs the following libs
#sudo apt-get install python-numpy python-scipy python-matplotlib

import scipy.io.wavfile as wavfile
from scipy.io import loadmat
import numpy as np
import argparse
import sys
import matplotlib.pyplot as plot
import scipy.signal as sg

class EndpointsAction(argparse.Action):
    def __call__(self, parser, args, values, option = None):
        setattr(args, self.dest, map(int,values))
        if len(args.endpoints) < 3:
            defaults = [0,None, 1]
            print "Wrong number of arguments, require 3 values, --endpoints start stop step"
            print "Using default endpoints of " + `args.endpoints`
            setattr(args, self.dest, defaults)

parser = argparse.ArgumentParser(description="Apply filter tutorial to input data")
parser.add_argument(dest="filename", help="WAV file to be processed")
parser.add_argument("-e", "--endpoints", dest="endpoints", default=[0,None, 1], action=EndpointsAction, nargs="*", help='Start and stop endpoints for data, default will try to process the whole file')

DECIMATE_BY = 4
FILT_CONST = 30
def show_filter_response(filt, title=None):
    w,h = sg.freqz(filt)
    plot.plot(w/max(w), np.abs(h))
    if title != None:
        plot.title(title)
    plot.show()

def show_specgram(input_data, fft_size=512, one_sided=True, title=None):
    split = "onesided" if one_sided else "twosided"
    plot.specgram(input_data, fft_size, sides=split)
    if title != None:
        plot.title(title)
    plot.show()

def prototype_filter(num_taps=DECIMATE_BY*FILT_CONST, normalized_cutoff=1./(2*DECIMATE_BY)):
    return sg.firwin(num_taps, normalized_cutoff)

def basic_single_filter(input_data, show_filter=True):
    filt = prototype_filter()
    show_filter_response(filt, title="Basic lowpass filter response")
    filtered_data = sg.fftconvolve(filt, input_data)
    return filtered_data

def polyphase_single_filter(input_data, decimate_by):
    if len(input_data) % decimate_by != 0:
        input_data = input_data[:len(input_data)-len(input_data)%decimate_by]
    #Adding these zeros is CRUCIAL!!!!!! Otherwise interference in the passband is not destructive?
    head_data_stream = np.append(input_data[::decimate_by],0)
    tail_data_streams = np.asarray([np.insert(input_data[0+i::decimate_by],0,0) for i in range(1,decimate_by)])
    #Once again, sorting the datastreams is CRUCIAL! Rows go in the following order
    #1
    #...
    #3
    #2
    data_streams = np.vstack((head_data_stream, tail_data_streams[::-1,:]))
    filt = prototype_filter()
    filter_streams = np.asarray([np.asarray(filt[0+i::decimate_by]) for i in range(decimate_by)])
    filtered_data_streams = np.asarray([sg.lfilter(filter_streams[n,:], 1, data_streams[n,:]) for n in range(decimate_by)])
    filtered_data = np.sum(filtered_data_streams, axis=0)
    return filtered_data

try:
    args = parser.parse_args()
except SystemExit:
    parser.print_help()
    sys.exit()

if args.filename[-4:] == ".wav":
    sr, data = wavfile.read(args.filename)
    data = np.asarray(data, dtype=np.complex64)[::args.endpoints[2]]
    if args.endpoints[1] == None:
        pass
    else:
        data = data[args.endpoints[0]:args.endpoints[1]]
    data /= 32768

show_specgram(data, title="Frequency plot of initial data")
basic = basic_single_filter(data)
show_specgram(basic, title="Frequency plot of filtered data using standard filtering")
decimated = basic[::DECIMATE_BY]
show_specgram(decimated, title="Frequency plot of filtered, then decimated data")
decimated_filtered = polyphase_single_filter(data, DECIMATE_BY)
show_specgram(decimated_filtered, title="Frequency plot of polyphase filtered data")
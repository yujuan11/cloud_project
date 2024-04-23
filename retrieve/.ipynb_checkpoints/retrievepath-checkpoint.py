#import uproot # for reading .root files
#import awkward as ak # to represent nested data in columnar format
#import vector # for 4-momentum calculations
#import time # to measure time to analyse
#import math # for mathematical functions such as square root
#import numpy as np # for numerical calculations such as histogramming
#import matplotlib.pyplot as plt # for plotting
#from matplotlib.ticker import AutoMinorLocator # for minor ticks
import pika
import infofile # local file containing cross-sections, sums of weights, dataset IDs

# lumi = 0.5 # fb-1 # data_A only
# lumi = 1.9 # fb-1 # data_B only
# lumi = 2.9 # fb-1 # data_C only
# lumi = 4.7 # fb-1 # data_D only
lumi = 10  # fb-1 # data_A,data_B,data_C,data_D

fraction = 1.0  # reduce this is if you want the code to run quicker

# tuple_path = "Input/4lep/" # local
tuple_path = "https://atlas-opendata.web.cern.ch/atlas-opendata/samples/2020/4lep/"  # web address

samples = {

    'data': {
        'list' : ['data_A','data_B','data_C','data_D'],
    },

    r'Background $Z,t\bar{t}$' : { # Z + ttbar
        'list' : ['Zee','Zmumu','ttbar_lep'],
        'color' : "#6b59d3" # purple
    },

    r'Background $ZZ^*$' : { # ZZ
        'list' : ['llll'],
        'color' : "#ff0000" # red
    },

    r'Signal ($m_H$ = 125 GeV)' : { # H -> ZZ -> llll
        'list' : ['ggH125_ZZ4lep','VBFH125_ZZ4lep','WH125_ZZ4lep','ZH125_ZZ4lep'],
        'color' : "#00cdff" # light blue
    },

}

MeV = 0.001
GeV = 1.0



def get_string():
    path=[]
    value=[]
    s_value=[]
    # Connect to RabbitMQ server
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()
    # Declare a 'messages' queue
    channel.queue_declare(queue='messages')
    for s in samples:  # loop over samples
        #print('Processing ' + s + ' samples')  # print which sample
        #frames = []  # define empty list to hold data
        for val in samples[s]['list']:  # loop over each file
            if s == 'data':
                prefix = "Data/"  # Data prefix
            else:  # MC prefix
                prefix = "MC/mc_" + str(infofile.infos[val]["DSID"]) + "."
            fileString = tuple_path + prefix + val + ".4lep.root"  # file name to open
            path.append(fileString)
            value.append(val)
            s_value.append(s)
            message=str(fileString)+';'+str(val)+';'+str(s)
            channel.basic_publish(exchange='', routing_key='messages', body=message)
            print("Message sent:", message)
    # Close the connection
    connection.close()
    return path, value,s_value

def send_messages(path,value,s):
   
    # Iterate over the lists and concatenate elements at the same position
    path_value_s = [str(path[i]) + "," + str(value[i]) + "," + str(s[i]) for i in range(len(path))]
    
    for message in path_value_s:
        # Publish each message to the queue
        channel.basic_publish(exchange='', routing_key='messages', body=message)
        print("Message sent:", message)



path,value,s=get_string()









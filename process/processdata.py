import uproot # for reading .root files
import awkward as ak # to represent nested data in columnar format
import vector # for 4-momentum calculations
import time # to measure time to analyse
#import math # for mathematical functions such as square root
#import numpy as np # for numerical calculations such as histogramming
#import matplotlib.pyplot as plt # for plotting
#from matplotlib.ticker import AutoMinorLocator # for minor ticks
import pika
import pickle
import infofile # local file containing cross-sections, sums of weights, dataset IDs

lumi = 10  # fb-1 # data_A,data_B,data_C,data_D

fraction = 1.0  # reduce this is if you want the code to run quicker

MeV = 0.001
GeV = 1.0
all_data={}

connection_params = pika.ConnectionParameters('rabbitmq',heartbeat=600,blocked_connection_timeout=300)
# Connect to RabbitMQ server
connection1 = pika.BlockingConnection(connection_params)
channel_1 = connection1.channel()

# Declare the same queue
channel_1.queue_declare(queue='messages')

def receive_messages():
    
    def callback(ch, method, properties, body):
        # Split each line by colon to extract the three elements
        ele= body.decode()
        elements=ele.split(';')
        if len(elements) == 3:
            data={}
            path, val, s = elements
            print("Received elements:", path, val, s)
            data=get_data_from_files(path,val,s) # process each file
            
            #all_data.update(data)

    # Start consuming messages
    channel_1.basic_consume(queue='messages', on_message_callback=callback, auto_ack=True)

    print('Waiting for messages. To exit, press CTRL+C')
    try:
        channel_1.start_consuming()
    except KeyboardInterrupt:
        channel_1.stop_consuming()
    

# Connect to RabbitMQ server
connection2 = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel_2 = connection2.channel()
# Declare a 'messages' queue
channel_2.queue_declare(queue='senddata')

# send processed data
def send_processed_data(data,sample,s):
    
    data_list = data.tolist()
    # Serialize the data to pickle
    serialized_data = pickle.dumps({'data':data_list,'sample':sample,'s':s})
    channel_2.basic_publish(exchange='', routing_key='senddata', body=serialized_data)

def get_data_from_files(fileString,val,s):
    data = {}  # define empty dictionary to hold awkward arrays
    frame=[]
    temp = read_file(fileString, val,s)  # call the function read_file defined below
    send_processed_data(temp,val,s)
    frame.append(temp)
    data[s] = ak.concatenate(frame)  # dictionary entry is concatenated awkward arrays
    return data  # return dictionary of awkward arrays



def calc_weight(xsec_weight, events):
    return (
        xsec_weight
        * events.mcWeight
        * events.scaleFactor_PILEUP
        * events.scaleFactor_ELE
        * events.scaleFactor_MUON
        * events.scaleFactor_LepTRIGGER
    )

def get_xsec_weight(sample):
    info = infofile.infos[sample] # open infofile
    xsec_weight = (lumi*1000*info["xsec"])/(info["sumw"]*info["red_eff"]) #*1000 to go from fb-1 to pb-1
    return xsec_weight # return cross-section weight

def calc_mllll(lep_pt, lep_eta, lep_phi, lep_E):
    # construct awkward 4-vector array
    p4 = vector.zip({"pt": lep_pt, "eta": lep_eta, "phi": lep_phi, "E": lep_E})
    # calculate invariant mass of first 4 leptons
    # [:, i] selects the i-th lepton in each event
    # .M calculates the invariant mass
    return (p4[:, 0] + p4[:, 1] + p4[:, 2] + p4[:, 3]).M * MeV

# cut on lepton charge
# paper: "selecting two pairs of isolated leptons, each of which is comprised of two leptons with the same flavour and opposite charge"
def cut_lep_charge(lep_charge):
# throw away when sum of lepton charges is not equal to 0
# first lepton in each event is [:, 0], 2nd lepton is [:, 1] etc
    return lep_charge[:, 0] + lep_charge[:, 1] + lep_charge[:, 2] + lep_charge[:, 3] != 0

# cut on lepton type
# paper: "selecting two pairs of isolated leptons, each of which is comprised of two leptons with the same flavour and opposite charge"
def cut_lep_type(lep_type):
# for an electron lep_type is 11
# for a muon lep_type is 13
# throw away when none of eeee, mumumumu, eemumu
    sum_lep_type = lep_type[:, 0] + lep_type[:, 1] + lep_type[:, 2] + lep_type[:, 3]
    return (sum_lep_type != 44) & (sum_lep_type != 48) & (sum_lep_type != 52)


def read_file(path, sample,s):
    start = time.time()  # start the clock
    print("\tProcessing: " + sample)  # print which sample is being processed
    data_all = []  # define empty list to hold all data for this sample

    # open the tree called mini using a context manager (will automatically close files/resources)
    with uproot.open(path + ":mini") as tree:
        numevents = tree.num_entries  # number of events
        if 'data' not in sample: xsec_weight = get_xsec_weight(sample)  # get cross-section weight
        for data in tree.iterate(['lep_pt', 'lep_eta', 'lep_phi',
                                  'lep_E', 'lep_charge', 'lep_type',
                                  # add more variables here if you make cuts on them
                                  'mcWeight', 'scaleFactor_PILEUP',
                                  'scaleFactor_ELE', 'scaleFactor_MUON',
                                  'scaleFactor_LepTRIGGER'],  # variables to calculate Monte Carlo weight
                                 library="ak",  # choose output type as awkward array
                                 entry_stop=numevents * fraction):  # process up to numevents*fraction

            nIn = len(data)  # number of events in this batch

            if 'data' not in sample:  # only do this for Monte Carlo simulation files
                # multiply all Monte Carlo weights and scale factors together to give total weight
                data['totalWeight'] = calc_weight(xsec_weight, data)

            # cut on lepton charge using the function cut_lep_charge defined above
            data = data[~cut_lep_charge(data.lep_charge)]

            # cut on lepton type using the function cut_lep_type defined above
            data = data[~cut_lep_type(data.lep_type)]

            # calculation of 4-lepton invariant mass using the function calc_mllll defined above
            data['mllll'] = calc_mllll(data.lep_pt, data.lep_eta, data.lep_phi, data.lep_E)

            # array contents can be printed at any stage like this
            # print(data)

            # array column can be printed at any stage like this
            # print(data['lep_pt'])

            # multiple array columns can be printed at any stage like this
            # print(data[['lep_pt','lep_eta']])

            nOut = len(data)  # number of events passing cuts in this batch
            data_all.append(data)  # append array from this batch
            
            elapsed = time.time() - start  # time taken to process
            print("\t\t nIn: " + str(nIn) + ",\t nOut: \t" + str(nOut) + "\t in " + str(
                round(elapsed, 1)) + "s")  # events before and after

    return ak.concatenate(data_all)  # return array containing events passing all cuts






receive_messages()

# Close the connection
connection2.close()









import os
import time
import pickle
from datetime import datetime as dt
from datetime import timedelta as td
from readgssi.dzt import readdzt
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# returns a list of DZT files created on the current date, sorted by creation time
# in: absolute path of the desired folder
# out: list containing absolute paths of DZT files
def todays_stack(search_dir):
    os.chdir(search_dir)
    delimiter = os.sep #this might not work
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files]
    filtered = []
    for f in files:
        if (f.split(".")[1] == "DZT") and (dt.fromtimestamp(os.path.getmtime(f))+td(days=1) > dt.today()):
            filtered.append(f.split(delimiter)[-1])
    filtered.sort(key=lambda x: os.path.getmtime(x))
    return filtered

# returns a list of DZT files in a directory, sorted by creation time
# in: absolute path of the desired folder
# out: list containing absolute paths of DZT files
def full_stack(search_dir):
    os.chdir(search_dir)
    delimiter = os.sep #this might not  work
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files]
    filtered = []
    for f in files:
        if (f.split(".")[1] == "DZT"):
            filtered.append(f.split(delimiter)[-1])
    filtered.sort(key=lambda x: os.path.getmtime(x))
    return filtered

def recv_obj(conn):
    Total_dat = []
    print("started reciving")
    while True:
        data = conn.recv(4096)
        if data:
            Total_dat.append(data)
        if not data:
            break
    recv_bin = b''.join(Total_dat)
    recv_obj = pickle.loads(recv_bin)
    return recv_obj

def gen_recv(conn):
    Total_dat = []
    recv_bin = None
    recv_obj = None
    data = None
    while True:
        data = conn.recv(4096)
        if data.endswith(b'EOP'):
            data = data[:-3]
            Total_dat.append(data)
            break
        else:
            Total_dat.append(data)
    recv_bin = b''.join(Total_dat)
    recv_obj = pickle.loads(recv_bin)
    return recv_obj

def gen_send(conn,obj):
    pickled = pickle.dumps(obj)+('EOP').encode()
    conn.send(pickled)
    return
    

# DZT Class
# Atributes:
#     origin_path (str): absolute path of the file on the source system
#     file_name (str): name of the file on the source system
#     realsensefile (str): name of the associated csv containing the survey path
#     dzt_contents (bin): binary string containing the actual file data
#     realsense_contents (bin): binary string contraining the survey path
class DZT_DAT:
    def __init__(self,path):

        self.file_name = path
        with open(self.file_name,'rb') as f:
            self.dzt_contents = f.read()
        self.realsense_file = self.file_name.split('.')[0]+('.csv')
        self.realsense_contents = []
        
        # Try to find real sense data 3 times before proceeding
        attempt = 0
        while attempt <= 3:
            try:
                with open(self.realsense_file,'rb') as f:
                    self.realsense_contents = f.read()
            except:
                print("Looking for realsense data...")
                attempt += 1
                time.sleep(5)
                    
  
    def b_scan(self):
        header,array,_ = readdzt(self.file_name)
        traces = array[0]
        numTraces = header['shape'][1]
        samples = header['shape'][0]
        fig = plt.imshow(traces)
        plt.savefig(self.file_name.split('.')[0]+".png",format='png')
        return
        
def reportReader():
    return

def configReader():
    return 

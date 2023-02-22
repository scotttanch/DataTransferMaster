import os
import time
import pickle

from datetime import datetime as dt
from datetime import timedelta as td

from readgssi.dzt import readdzt

import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import text_to_be_present_in_element


# returns a list of DZT files created on the current date, sorted by creation time
# in: absolute path of the desired folder
# out: list containing absolute paths of DZT files
def todays_stack(search_dir:str , ext:str):
    os.chdir(search_dir)
    delimiter = os.sep #this might not work
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files]
    filtered = []
    for f in files:
        if (f.split(".")[1] == ext) and (dt.fromtimestamp(os.path.getmtime(f))+td(days=1) > dt.today()):
            filtered.append(f.split(delimiter)[-1])
    filtered.sort(key=lambda x: os.path.getmtime(x))
    return filtered

# returns a list of DZT files in a directory, sorted by creation time
# in: absolute path of the desired folder
# out: list containing absolute paths of DZT files
def full_stack(search_dir:str, ext:str):
    os.chdir(search_dir)
    delimiter = os.sep #this might not  work
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files]
    filtered = []
    for f in files:
        if (f.split(".")[1] == ext):
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

def gen_send(conn,obj:object):
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
    def __init__(self,path:str):

        self.file_name = path
        with open(self.file_name,'rb') as f:
            self.dzt_contents = f.read()
        self.realsense_file = self.file_name.split('.')[0]+('.csv')
        self.realsense_contents = []
        
        # Try to find real sense data 3 times before proceeding
        attempt = 0
        while not self.realsense_contents and attempt < 3:
            try:
                with open(self.realsense_file,'rb') as f:
                    self.realsense_contents = f.read()
            except:
                print("Looking for realsense data...")
                attempt += 1
                time.sleep(2)
                
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

def configReader(con_file:  str):
    try:
        with open (con_file, 'r') as f:
            lines = f.readlines()
    except:
        raise Exception("Config File not found",con_file)

    host = lines[0]
    port = int(lines[1])
    delay = int(lines[2])
    path = lines[3]
    
    return host, port, delay, path

def hotspot_config(con_file: str):
    try:
        with open (con_file, 'r') as f:
            lines = f.readlines()
    except:
        raise Exception("Config File not found",con_file)

    main_page = lines[0]
    network_page = lines[1]
    adm_psw = lines[2]
    return main_page, network_page, adm_psw

def write_config(main_page: str, network_page: str, adm_psw: str, file_name: str):
    with open(file_name, 'w+') as f:
        f.write(main_page + "\n")
        f.write(network_page + "\n")
        f.write(adm_psw + "\n")
    return

# Returns the current technology as a string
# Args: con_file: str, name of the config file, if not in local folder must be an absolute path
# Return: tech: str. current network mode. expected 4G, 5G, or no signal
def check_mode(con_file: str) -> str:

    main_page, _, adm_psw = hotspot_config(con_file)
    FFops = Options()
    FFops.add_argument("-headless")
    driver = webdriver.Firefox(options=FFops)

    # Open the main page
    driver.get(main_page)
    
    # Enter the password
    pass_input = driver.find_element(By.NAME,"password")
    pass_input.clear()
    pass_input.send_keys(adm_psw)
    pass_input.send_keys(Keys.RETURN)

    # find the technology field on the main page
    #current_val = driver.find_element(By.ID,"technology")
    WebDriverWait(driver, timeout=30).until(text_to_be_present_in_element((By.ID,'technology'),'G'))
    current_val = driver.find_element(By.ID,"technology")
    tech = current_val.text
    
    if tech == "":
        print("Could not identify current network mode")
        tech = "unknown"

    driver.close()
    return tech 

def set_mode(con_file: str, new_mode: str):

    if new_mode == '3G':
        new_val = '2'
    elif new_mode == '4G':
        new_val = '1'
    elif new_mode == '5G':
        new_val = '0'
    else:
        raise Exception("Unknown network preference", new_mode)

    main_page, network_page, adm_psw = hotspot_config(con_file)
    FFops = Options()
    FFops.add_argument("-headless")
    driver = webdriver.Firefox(options=FFops)

    # Open the main page
    driver.get(main_page)

    # Enter the password
    pass_input = driver.find_element(By.NAME,"password")
    pass_input.clear()
    pass_input.send_keys(adm_psw)
    pass_input.send_keys(Keys.RETURN)

    # Switch to the config page
    driver.get(network_page)

    # Find the ok button and click it
    ok_but = driver.find_element(By.ID,'ok-btn')
    ok_but.click()

    # Find the value of the networkmode element, 0 is 5G, 1 is 4G, 2 is 3G (3G doesnt seem to be supported here)
    # The order of modes in the drop down is actuall 0,2,1 though so 5G to 4G is two downs
    change_tech = driver.find_element(By.ID,"networkmode")
    current_val = change_tech.get_attribute('value')
    
    # do a little confirmation printing
    if current_val == '0':
        current_mode = '5G'
    elif current_val == '1':
        current_mode = '4G'
    elif current_val == '2':
        current_mode = '3G'
    else:
        raise Exception("Current network technology unknown",current_mode)

    if current_val == new_val:
        print("Network mode already set")
        return

    # Currently 5G
    if current_val == '0':
        # Change to 4G
        if new_val == '1':
            change_tech.send_keys(Keys.ARROW_DOWN)
            change_tech.send_keys(Keys.ARROW_DOWN)
        # Change to 3G
        if new_val == '2':
            change_tech.send_keys(Keys.ARROW_DOWN)

    # Currently 4G
    if current_val == '1':
        # Change to 5G
        if new_val == '0':
            change_tech.send_keys(Keys.ARROW_UP)
            change_tech.send_keys(Keys.ARROW_UP)
        # Change to 3G
        if new_val == '2':
            change_tech.send_keys(Keys.ARROW_UP)
        
    # Currently 3G
    if current_val == '2':
        # Change to 5G
        if new_val == '0':
            change_tech.send_keys(Keys.ARROW_UP)
        # Change to 4G
        if new_val == '1':
            change_tech.send_keys(Keys.ARROW_DOWN)

    change_tech.send_keys(Keys.RETURN)
    submit_button = driver.find_element(By.ID,"manualSave")
    submit_button.click()
    
    print("Network mode changed from",current_mode,"to",new_mode)

    driver.close()
    return
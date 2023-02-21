import transfer_tools as tls
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from datetime import timedelta as td
import pandas as pd
import os

# Location of the report files and the stack containing them
report_folder = "C:\\Users\\Scott\\Documents\\GitHub\\DataTransferMaster\\reports\\"
#report_folder = "C:\\Users\\Scott\\Documents\\GitHub\\DataTransferMaster\\reports\\Test 2 1-26 2-7\\"
file_paths = tls.full_stack(report_folder,"txt")
delimiter = os.sep

# New file format
# name, mode, size, processing time, sending time, total time, sending rate
# str,  str,  kb,   ns,              ns,           ns,         Mb/s
# 0     1     2     3                4             5           6

# Session report class definition
class Session_Report:
    def __init__(self,file_path):
        self.name = file_path.split(delimiter)[-1].split(".")[0]
        self.creation_date = self.name.split('_')[1]
        self.creation_time = self.name.split('_')[2]
        self.time_string = self.creation_date+"-2022::"+self.creation_time
        self.creation_date = datetime.strptime(self.time_string,"%m-%d-%Y::%H-%M")
        with open(self.name+'.txt', 'r') as f:
            self.data = f.readlines()[1:]

        # Extract the network mode
        self.mode = self.data[0].split(',')[1]

        # Extract Processing Time
        tmp = []
        for line in self.data:
            val = float(line.split(',')[3])
            tmp.append(val)
        self.avg_P = np.mean(tmp)*(10**-9)
        self.std_P = np.std(tmp)*(10**-9)
        
        # Extract Sending Time
        tmp = []
        for line in self.data:
            val = float(line.split(',')[4])
            tmp.append(val)
        self.avg_S = np.mean(tmp)*(10**-9)
        self.std_S = np.std(tmp)*(10**-9)

        # Extract Total Time
        tmp = []
        for line in self.data:
            val = float(line.split(',')[5])
            tmp.append(val)
        self.avg_R = np.mean(tmp)*(10**-9)
        self.std_R = np.std(tmp)*(10**-9) 

        # Extract processing Bit rate                                       
        tmp = []
        for line in self.data:
            val = float(line.split(',')[6])
            tmp.append(val)
        self.avg_Bit = np.mean(tmp)                    
        self.std_Bit = np.std(tmp)  
    
    def print(self):
        print("Report: ", self.name)
        print("Created on: ",self.creation_date," at ",self.creation_time)
        print("Technology: ",self.mode)
        print("Average Acknowledgement time: ",self.avg_S," (s)")
        print("Average Processing time: ",self.avg_P," (s)")
        print("Average Round Trip ",self.avg_R,"+\-",self.std_R," (s)")
        print("Average Bit Rate: ",self.avg_Bit,"+\-",self.std_Bit," (Mb/s)")

# Create an empty list that will have session reports as its elements, sorted by the date atribute
reports = []
for file in file_paths:
    reports.append(Session_Report(file))
reports.sort(key=lambda x: x.creation_date)

# Empty lists for the things that will be ploted
Bit_rates_4 = []
Bit_stds_4 = []
S_Times_4 = []
P_Times_4 = []
R_Times_4 = []
Dates_4 = []

Bit_rates_5 = []
Bit_stds_5 = []
S_Times_5 = []
P_Times_5 = []
R_Times_5 = []
Dates_5 = []

# Populate the empty lists
for report in reports:
    if report.mode == '4G':
        Dates_4.append(report.creation_date)
        Bit_rates_4.append(report.avg_Bit)
        Bit_stds_4.append(report.std_Bit)
        S_Times_4.append(report.avg_S)
        P_Times_4.append(report.avg_P)
        R_Times_4.append(report.avg_R)
    else:
        Dates_5.append(report.creation_date)
        Bit_rates_5.append(report.avg_Bit)
        Bit_stds_5.append(report.std_Bit)
        S_Times_5.append(report.avg_S)
        P_Times_5.append(report.avg_P)
        R_Times_5.append(report.avg_R)

# Create a set of tick marks and their labels
ticks = pd.date_range(min(Dates_4),max(Dates_4),6)
labels = []
for date in ticks:
    string = str(date.month) + "/" + str(date.day) + " " + str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2)
    labels.append(string)

# Print some values
avg_sending = np.mean(S_Times_4)
avg_processing = np.mean(P_Times_4)
avg_bit = np.mean(Bit_rates_4)
avg_round = np.mean(R_Times_4)
print("Average Time to send: " + str(round(avg_sending,3)) + " (s)")
print("Average Processing time: " + str(round(avg_processing,3)) +" (s)" )
print("Average Round Trip: " + str(round(avg_round,3)) + " (s)")
print("Average Speed: " + str(round(avg_bit,3)) + " (Mb/s)")

# Response Time subplot
plt.subplot(2,1,2)
plt.plot(Dates_4,S_Times_4)
plt.plot(Dates_4,R_Times_4)
plt.plot(Dates_5,S_Times_5)
plt.plot(Dates_5,R_Times_5)
plt.legend(["4G ACK"," 4G Round Trip","5G ACK"," 5G Round Trip"])
plt.title("Response and Round Trip Time")
plt.ylabel("Time (s)")
plt.xticks(ticks,labels,rotation=15)

# Bit Rate Subplot
plt.subplot(2,1,1)
plt.plot(Dates_4,Bit_rates_4)
plt.plot(Dates_5,Bit_rates_5)
plt.title("Bit Rate Sampled Every Half Hour")
plt.ylabel("Bit Rate (Mb/s)")
plt.legend(["4G Rate"," 5G Rate"])
plt.xticks([])

# Show the plot
plt.show()

            
        

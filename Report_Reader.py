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
        
        if self.data[-1].split(',')[0] == 'File':       # I accidently made the reports write the column labels on the top and bottom
            self.data = self.data[1:-1]                 # I'm calling it a feature not a bug, this deals with that feature
                                                   
        tmp = []
        for line in self.data:
            val = float(line.split(',')[4])
            tmp.append(val)
        self.avg_Bit = np.mean(tmp)                      # the *1000 stays until i push the new code out that deals with the 
        self.std_Bit = np.std(tmp)                    # fact that i divided by 1000 one too many times, Applys to reports created before 2/7/23

        tmp = []
        for line in self.data:
            val = float(line.split(',')[2])
            tmp.append(val)
        self.avg_P = np.mean(tmp)*(10**-9)
        self.std_P = np.std(tmp)*(10**-9)
        
        tmp = []
        for line in self.data:
            val = float(line.split(',')[3])
            tmp.append(val)
        self.avg_S = np.mean(tmp)*(10**-9)
        self.std_S = np.std(tmp)*(10**-9)
    
    def print(self):
        print("Report: ", self.name)
        print("Created on: ",self.creation_date," at ",self.creation_time)
        print("Average Acknowledgement time: ",self.avg_S," (s)")
        print("Average Processing time: ",self.avg_P," (s)")
        print("Average Bit Rate: ",self.avg_Bit,"+\-",self.std_Bit,"(Mb/s)")

# Create an empty list that will have session reports as its elements, sorted by the date atribute
reports = []
for file in file_paths:
    reports.append(Session_Report(file))
reports.sort(key=lambda x: x.creation_date)

# Empty lists for the things that will be ploted
Bit_rates = []
Bit_stds = []
S_Times = []
P_Times = []
Dates = []

# Populate the empty lists
for report in reports:
    Dates.append(report.creation_date)
    Bit_rates.append(report.avg_Bit)
    Bit_stds.append(report.std_Bit)
    S_Times.append(report.avg_S)
    P_Times.append(report.avg_P)

# Create a set of tick marks and their labels
ticks = pd.date_range(min(Dates),max(Dates),6)
labels = []
for date in ticks:
    string = str(date.month) + "/" + str(date.day) + " " + str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2)
    labels.append(string)

# Print some values
avg_sending = np.mean(S_Times)
avg_processing = np.mean(P_Times)
avg_bit = np.mean(Bit_rates)
print("Average Time to send: " + str(round(avg_sending,3)) + " (s)")
print("Average Processing time: " + str(round(avg_processing,3)) +" (s)" )
print("Average Speed: " + str(round(avg_bit,3)) + " (Mb/s)")

# Response Time subplot
plt.subplot(2,1,2)
plt.plot(Dates,S_Times)
plt.plot(Dates,P_Times)
plt.legend(["ACK","Processed"])
plt.title("Response and Processing Times")
plt.ylabel("Time (s)")
plt.xticks(ticks,labels,rotation=15)

# Bit Rate Subplot
plt.subplot(2,1,1)
plt.plot(Dates,Bit_rates)
plt.title("Bit Rate Sampled Every Half Hour")
plt.ylabel("Bit Rate (Mb/s)")
plt.xticks([])

# Show the plot
plt.show()

            
        

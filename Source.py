import socket
import pickle
import transfer_tools as tls
import time
import cv2

# Constants
search_path = "/home/stanch/public/DZTs"
#Host = '65.183.134.63'
Host = '192.168.1.206'
Port = 55
delay = 30


print("Waiting for Connection to Host")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((Host, Port))
    print("Connected to ", Host)
    
    # Are we doing F scans or B scans?
    choice = False
    while choice == False:
        scan_mode = input("Select Scan Mode: [F/B] ")
        if scan_mode == 'F' or 'f':
            f_mode = True
            choice = True
        elif scan_mode == 'B' or 'b':
            f_mode = False
            choice = True
        else:
            print("Selection not understood")
    
    # Prompt the user for the name of the survery and send it off
    print("Sending Directory...")
    directory =  "DIR " + input("Enter Survey Directory: ")
    tls.gen_send(s,directory)
    ACK_response = tls.gen_recv(s)

    while True:
        # Send the list of files on the source machine, need to recive the list of files on the server
        print("Sending Source Stack...")
        source_stack = tls.full_stack(search_path)
        tls.gen_send(s,source_stack)
        request_stack = tls.gen_recv(s)
        if request_stack != []:
            print("Sending Files...")
            while request_stack != []:
                next_file = request_stack.pop()
                print("Sending ",next_file)
                next_dzt = tls.DZT_DAT(next_file,f_mode)
                tls.gen_send(s,next_dzt)
                b_scan = tls.gen_recv(s)
                print("/home/stanch/public/b_scans/"+next_file.split('.')[0]+".png")
                cv2.imwrite("/home/stanch/public/b_scans/"+next_file.split('.')[0]+".png",b_scan)
                #ACK_response = tls.gen_recv(s)
            print("Stack Empty")
        else:
            print("No requests, waiting for more files....")
            time.sleep(delay)
    
    # Close the socket
    print("Closing Connection...")
    tls.gen_send(s,"COM exit")
    response = tls.gen_recv(s)
    #print("response: ",response)

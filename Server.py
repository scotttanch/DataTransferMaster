#import pickle
import gc
import socket
import transfer_tools as tls
#import time
import os
import cv2

print("Waiting for Connection to Client")
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Begin listening at the desired port
    Host = "192.168.0.197"
    #Host = '127.0.0.1'
    Port = 55
    s.bind((Host, Port))
    s.listen()
    project_directory = 'C:\\Users\STanch\\Desktop\\Surveys\\'
    Continuous_Run = True
    # Accept connection to the source
    while Continuous_Run:
        conn, addr = s.accept()
        print("Establishing New Connection...")
        print('Connected to', addr)
        with conn:
            directory = None
            while True:
                # Receive the etirety of an objects bin and unpickle i
                print("Waiting for data")
                recv_obj = tls.gen_recv(conn)

                # This should be what to do with a provided directory or command
                if type(recv_obj) == str:
                    # Is the string a command or a directory?
                    if recv_obj.startswith('COM'):
                        # Commands go here
                        command = recv_obj.split(' ')[-1]
                        if command == "exit":
                            print("Closing socket")
                            tls.gen_send(conn, "ACK")
                            break
                        if command == "testing":
                            print("Enabling Testing mode...")
                            testing_mode = True
                    if recv_obj.startswith('DIR'):
                        directory = recv_obj.split(' ')[-1]
                        if not os.path.exists(project_directory + directory):
                            os.mkdir(project_directory+directory)
                        tls.gen_send(conn, "ACK")

                # This should be what to do with the source_stack
                if type(recv_obj) == list:
                    source_list = recv_obj
                    server_list = tls.full_stack(project_directory+directory)
                    requests = list(set(source_list)-set(server_list))
                    tls.gen_send(conn, requests)

                # This should be what to do with a DZT obj
                if type(recv_obj) == tls.DZT_DAT:
                    tls.gen_send(conn, "ACK")
                    print("Recvied: ", recv_obj.file_name)
                    with open(recv_obj.file_name, 'wb+') as f:
                        f.write(recv_obj.dzt_contents)
                    if recv_obj.realsense_contents:
                        with open(recv_obj.realsense_file, 'wb+') as f:
                            f.write(recv_obj.realsense_contents)
                    print("Generating B Scan")
                    recv_obj.b_scan()
                    b_scan = cv2.imread(recv_obj.file_name.split('.')[0]+".png")
                    tls.gen_send(conn, b_scan)
        gc.collect()

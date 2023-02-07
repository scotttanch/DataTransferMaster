import socket
import transfer_tools as tls
import time
from datetime import datetime
import cv2

# TODO: Implement a config file so i can remove system paths and IPs
# Constants to be configed
search_path = "/home/stanch/public/DZTs"
Host = '65.183.134.63'
#Host = '192.168.1.206'
Port = 56
delay = 30


def clientHandler():

    print("Waiting for Connection to Host")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        s.connect((Host, Port))
        print("Connected to ", Host)

        # Prompt the user for the name of the survery and send it off
        #print("Sending Directory...")
        #directory =  "DIR " + input("Enter Survey Directory: ")
        #tls.gen_send(s,directory)
        #ACK_response = tls.gen_recv(s)

        # Or If were in testing mode use this for directory
        date_and_time = datetime.now().strftime("%m-%d_%H-%M")
        directory =  "Perks_" +  date_and_time
        print(directory)
        tls.gen_send(s,"DIR "+directory)
        ACK_response = tls.gen_recv(s)

        # Currently the client is always running looking for new files
        # to be added to the survey, When a real survey is complete the
        # client must be manually stopped. 

        while True:
            
            try:
                # Send the list of files on the source machine, need to recive the list of files on the server
                # In practice this should be todays_stack but since the 
                # data set were working with is not "live" so to speak
                # We want the full stack

                print("Sending Source Stack...")
                source_stack = tls.full_stack(search_path,"DZT")
                tls.gen_send(s,source_stack)
                request_stack = tls.gen_recv(s)

                # Create the associated report file
                with open("/home/stanch/public/reports/"+directory+"_Report.txt", 'a+') as f:
                    line = "File,Size (Kb),T_p (nS),T_s (nS),Rate (Mbit/s) \n"
                    f.write(line)

                if request_stack != []:
                    print("Sending Files...")

                    while request_stack != []:
                        next_file = request_stack.pop()
                        print("Sending ",next_file)
                        next_dzt = tls.DZT_DAT(next_file)
                        start_send_timer = time.monotonic_ns()
                        tls.gen_send(s,next_dzt)
                        ACK_response = tls.gen_recv(s)
                        end_send_timer = time.monotonic_ns()
                        b_scan = tls.gen_recv(s)
                        tls.gen_send(s, "ACK")
                        
                        # Get/Calucalte Metrics and write them to the report file
                        size = (len(next_dzt.dzt_contents)+len(next_dzt.realsense_contents))/1000   # File sizes in Kilobytes
                        processing_time = tls.gen_recv(s)                                           # Time to process in Ns
                        sending_time = end_send_timer - start_send_timer                            # Time to send in Ns
                        sending_rate = (size*8)/(sending_time*(10**-9)*(10**3))                     # Rate in Megabits/s
                        with open("/home/stanch/public/reports/"+directory+"_Report.txt", 'a+') as f:
                            line = next_file.split('.')[0] + "," + str(size) + "," + str(processing_time) + "," + str(sending_time) + "," + str(sending_rate) + "\n"
                            f.write(line)


                        print("/home/stanch/public/b_scans/"+next_file.split('.')[0]+".png")
                        cv2.imwrite("/home/stanch/public/b_scans/"+next_file.split('.')[0]+".png",b_scan)

                    print("Stack Empty")
                
                # switch the commented lines in this block during real
                # opperation vs experimental setups
                else:
                #    print("No requests, waiting for more files....")
                #    time.sleep(delay)
                    break
            
            except KeyboardInterrupt:
                break
        
        # Close the socket
        print("Closing Connection...")
        tls.gen_send(s,"COM exit")
        ACK_response = tls.gen_recv(s)

    return

def main():
    # This whole timing thing is only relevant to the testing form
    clientHandler()
    while True:
        try:
            # create a time object
            now = datetime.now()
            # find the number of seconds to the next half hour
            sec_to_wait = (30 - (now.minute % 30))*60
            print("Waiting for next event....(" + str(sec_to_wait/60)+ " minutes)")
            time.sleep(sec_to_wait)
            clientHandler()
        except KeyboardInterrupt:
            break
    return


if __name__ == "__main__":
    main()
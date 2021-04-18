import time 
from watchdog.observers import Observer 
from watchdog.events import FileSystemEventHandler
import queue
from Shell import Shell
import os
import socket
import pexpect

class OnTrafficWatch: 
    # Set the directory on watch
    watchDirectory = "./"
  
    def __init__(self): 
        self.observer = Observer()
        self.queue = queue.Queue() 
  
    def run(self): 
        event_handler = Handler(self.queue) 
        self.observer.schedule(event_handler, self.watchDirectory, recursive = True) 
        self.observer.start() 
        try: 
            while True: 
                time.sleep(5)

        except: 
            self.observer.stop() 
            print("Observer Stopped") 
  
        self.observer.join()

class Handler(FileSystemEventHandler):

    def __init__(self, queue):
        self.queue = queue
        self.shell = Shell() 
   
    def on_any_event(self, event):
        if event.is_directory: 
            return None
  
        elif event.event_type == 'created': 
            # Event is created, you can process it now 
            print("Watchdog received created event - % s." % event.src_path)

            if('data' in str(event.src_path)):
                self.queue.put(str(event.src_path)[2:])
                print(self.queue.qsize())
            if(self.queue.qsize() > 1):
                file = self.queue.get()
                csv_file_name = socket.gethostname()+'traffic'+file[5:-5]+'.csv'

                self.shell.execute("echo \"abcd\" |  sudo -S tshark -r " + file + " -T fields -E separator=, -E quote=d -e _ws.col.No. -e _ws.col.Time -e _ws.col.Source -e tcp.srcport -e _ws.col.Destination -e tcp.dstport -e _ws.col.Protocol -e _ws.col.Length -e _ws.col.Info > " + csv_file_name)

                try:
                    var_password  = "abcd"
                    var_command = "scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no " + csv_file_name + " root@10.3.0.24:/root/GateWay/Profiles"
        
                    var_child = pexpect.spawn(var_command)
                    i = var_child.expect(["password:", pexpect.EOF])
                    print(i)

                    if i==0: # send password                
                        var_child.sendline(var_password)
                        var_child.expect(pexpect.EOF)

                        os.remove(file)
                        os.remove(csv_file_name)
                    elif i==1: 
                        print("Got the key or connection timeout")
                        pass

                    

                except Exception as e:
                    print("Oops Something went wrong buddy")
                    print(e)             

import socket
import threading
import os
import shlex
import sys
import platform



rfc_list=[]
rfc_title=[]
a=[]
SERVER_PORT = 7734
EXIT_FLAG = False
OS = platform.system()


def rfc_request(message,rfc_number,peer_name,peer_port,file_name):
    s=socket.socket()
    peer_ip= socket.gethostbyname(peer_name)
    s.connect((peer_ip,peer_port))
    print "\nclient connected: \n"
    s.send(message)
    reply=s.recv(1024)
    reply_list=shlex.split(reply)
    os.chdir(os.getcwd())
    file_name=file_name+".txt"
    if str(reply_list[1])=='200':
        file1=open(file_name,'wb')
        while True:
            q=s.recv(1024)
            if q:
                file1.write(q)
                break
            else:
                file1.close()
                print "File %s downloaded successfully\n" % (file_name)
                break
        s.close()
    else:
        print "File Not Found"
        s.close()
        return False
    return True


def rfc_retrieve(name, sock):
    request=sock.recv(1024)
    print request
    rfc_number=shlex.split(request)
    file_found = 0
    for x in a:
        t = x.split("-")
        if int(t[0])==int(rfc_number[2]):
            print t[0]
            file_found=1
            file_name=str(x)+".txt"

    if file_found==0:
        print "File not found"
        file_data="P2P-CI/1.0 404 FILE NOT FOUND"+"\n"
        sock.send(file_data)
    else:
        file_data="P2P-CI/1.0 200 OK"+"\n"
        sock.send(file_data)
        with open(file_name,'r') as f:
            bytesToSend = f.read(1024)
            sock.send(bytesToSend)
            while bytesToSend != "":
                bytesToSend = f.read(1024)
                sock.send(bytesToSend)
    sock.close()


def rfc_create_list():
    global a
    file_list = os.listdir(os.getcwd())
    temp_rfc = list()
    temp_title = list()
    for file_name in file_list:
        files = file_name.split(".")
        if files[1] == "txt":
            w = str(files[0])
            a.append(w)
            files1 = w.split("-")
            temp_rfc.append(int(files1[0]))
            temp_title.append(files1[1])
    return temp_rfc,temp_title



def listen_on_client():

    cs_socket = socket.socket()
    cs_host = socket.gethostname()
    cs_port = PORT
    cs_socket.bind((cs_host,cs_port))
    cs_socket.listen(2)

    cs_thread = threading.current_thread()
    while(EXIT_FLAG != True):

        (peer_socket,peer_addr)=cs_socket.accept()
        print "Connected to", peer_addr
        thread_third=threading.Thread(target=rfc_retrieve,args=("retrThread",peer_socket))
        thread_third.start()
        thread_third.join()
    cs_socket.close()
    return

def print_menu():
    print "Select from the List"
    print "1. List all RFC"
    print "2. Lookup RFC"
    print "3. Add RFC"
    print "4. Get RFC file"
    print "5. Exit"
    print "6. Remove a RFC"

def handle_list_all(serverIP, serverPort):
    message="LISTALL P2P-CI/1.0"+"\n"+"Host: "+HOST+"\n"+" Port: "+str(PORT)
    serv_resp_handler(message,serverIP,serverPort)

def handle_lookup(serverIP, serverPort):
    print "Enter RFC number"
    rfc_number = int(raw_input())
    print "Enter RFC title"
    rfc_title=raw_input()
    message="LOOKUP"+" "+str(rfc_number)+" P2P-CI/1.0"+"\n"+"Host: "+HOST+"\n"+"Port: "+str(PORT)+"\n"+"Title:"+rfc_title
    serv_resp_handler(message,serverIP,serverPort)
def handle_add_RFC(serverIP, serverPort):
    print "Enter RFC number"
    rfc_number=raw_input()
    print "Enter the title for the RFC"
    rfc_title=raw_input()
    a.insert(0,str(rfc_number))
    message="ADD"+" "+rfc_number+" P2P-CI/1.0"+"\n"+" Host: "+HOST+"\n"+" Port: "+str(PORT)+"\n"+" Title: "+rfc_title
    serv_resp_handler(message,serverIP,serverPort)

def handle_get_RFC(serverIP, serverPort):
    print "Enter RFC #: "
    rfc_number = int(raw_input())
    print "Enter RFC title: "
    rfc_title = raw_input()
    print "Enter peer hostname(which contains the file): "
    name_peer = raw_input()
    print "Enter Peer port # : "
    port_peer = int(raw_input()) 
    message = "GET RFC " +str(rfc_number)+ " " +"P2P-CI/1.0\n"+"Host: "+name_peer+"\n"+"OS: "+str(OS)
    file_name = str(rfc_number)+"-"+rfc_title
    status = rfc_request(message,rfc_number,name_peer,port_peer,file_name)
    if status == True:
        #add rfc
        a.insert(0,str(rfc_number))
        message="ADD"+" "+ str(rfc_number) +" P2P-CI/1.0"+"\n"+" Host: "+HOST+"\n"+" Port: "+str(PORT)+"\n"+" Title: "+rfc_title
        serv_resp_handler(message,serverIP,serverPort)


def handle_exit(serverIP, serverPort):
    message = "EXIT P2P-CI/1.0 Host: "+HOST+" Port: "+str(PORT)
    serv_resp_handler(message, serverIP, serverPort)
    global EXIT_FLAG
    EXIT_FLAG = True
   # thread.exit()

def handle_rem_RFC(serverIP, serverPort):
    print "Enter RFC number"
    rfc_number = int(raw_input())
    print "Enter RFC title"
    rfc_title = raw_input()
    str_file_name = str(rfc_number)+"-"+rfc_title+".txt"
    os.remove(str_file_name)
    message = "REMOVE"+" "+str(rfc_number)+" P2P-CI/1.0"+"\n"+" Host: "+HOST+"\n"+" Port: "+str(PORT)+"\n"+" Title: "+rfc_title
    serv_resp_handler(message, serverIP, serverPort)

def user_input_handler():
    temp_rfc = list()
    temp_title = list()
    print "Enter Host name of the Centralised Server"
    serverIP=raw_input()
    serverPort = SERVER_PORT
    message = "REGISTER P2P-CI/1.0 Host: "+HOST+" Port: "+str(PORT)+"\n"
    serv_resp_handler(message,serverIP,serverPort)
    temp_rfc, temp_title=rfc_create_list()
    print temp_rfc
    for x in range(len(temp_rfc)):
        message = "ADD"+" "+str(temp_rfc[x])+" P2P-CI/1.0"+"\n"+" Host: "+HOST+"\n"+" Port: "+str(PORT)+"\n"+" Title: "+temp_title[x]
        serv_resp_handler(message,serverIP,serverPort)
    
    while(True):
        
        print_menu()

        choice = int(raw_input())

        if choice == 1:
            handle_list_all(serverIP, serverPort)
            
        if choice == 2:
            handle_lookup(serverIP, serverPort)

        if choice == 3:
            handle_add_RFC(serverIP, serverPort)
                
        if choice == 4:
            handle_get_RFC(serverIP, serverPort)

        if choice == 5:
            handle_exit(serverIP, serverPort)

        if choice == 6:
            handle_rem_RFC(serverIP, serverPort)
    return            


def serv_resp_handler(message, serverIP, serverPort):
    sock = socket.socket()
    sock.connect((serverIP,serverPort))
    sock.send(message)
    reply = sock.recv(16384)
    print "*"*40
    print "Response received from Server:"
    print reply
    print "*"*40
    sock.close()



if __name__== "__main__":

    global HOST
    global PORT
    global IP

    HOST = ''
    PORT = 0
    IP = ''
    HOST = socket.gethostname()
    print "Enter your upload port# : "
    PORT = int(raw_input())
    try:
        therad_listen = threading.Thread(target=listen_on_client)
     #   therad_user_opt = threading.Thread(target=user_input_handler)
        therad_listen.daemon = True
     #   therad_user_opt.daemon = True
        therad_listen.start()
     #   therad_user_opt.start()
        user_input_handler()
        
        while(EXIT_FLAG == False):
            pass  
        sys.exit(0)

    except KeyboardInterrupt:
        sys.exit(0)
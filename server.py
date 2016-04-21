import socket
import threading
import os
import shlex

count=0
peer_list=list()
index_list=list()
rfcList=list()
SERVER_PORT = 7734
    
    
class RFCRecord:
    def __init__(self, rfc_number = -1, rfc_title = 'None', peerHostname ='None', peerid =-1):
        self.rfc_number = rfc_number
        self.rfc_title = rfc_title
        self.peerHostname = peerHostname
        self.peerid=peerid

    def __str__(self):
        return str(self.rfc_number)+' '+str(self.rfc_title)+' '+str(self.peerHostname)+' '+str(self.peerid)



class PeerRecord:
    def __init__(self,peerHostname='None',peerPortNo=10000,peerid=-1):
        self.peerHostname=peerHostname
        self.peerPortNo=peerPortNo
        self.peerid=peerid

    def __str__(self):
        return str(self.peerHostname)+' '+str(self.peerPortNo)+' '+str(self.peerid)


def get_port(peerid):
    for peer_record in peer_list:
        if peer_record.peerid == peerid:
            return peer_record.peerPortNo 

def handle_register(data, clientsocket):
    count=add_peer(data)
    reply="Thank you for registering"
    clientsocket.send(reply)

def handle_list(clientsocket):
    reply,code,phrase=list_RFC()
    response="P2P-CI/1.0 "+str(code)+" "+str(phrase)+"\n"
    for i in reply:
        reply_list=shlex.split(str(i))
        response=response+str(reply_list[0])+" "+reply_list[1]+" "+reply_list[2]+" "+str(reply_list[3])+"\n"    
    clientsocket.send(response)

def handle_lookup(clientsocket, rlist):
    reply,code,phrase=find_RFC(rlist[1])
    response="P2P-CI/1.0 "+str(code)+" "+str(phrase)+"\n"
    for i in reply:
        reply_list=shlex.split(str(i))
        response=response+str(reply_list[0])+" "+reply_list[1]+" "+reply_list[2]+" "+str(reply_list[3])+"\n"
    clientsocket.send(response)

def handle_add(clientsocket, rlist, count, data):
    reply,code,phrase=add_RFC(rlist[1],rlist,count)
    a=data.splitlines()
    title=a[3].split(":")
    response="P2P-CI/1.0 "+str(code)+" "+str(phrase)+"\n"
    response=response+"RFC "+rlist[1]+" "+title[1]+" "+rlist[4]+" "+rlist[6]
    clientsocket.send(response)

def handle_exit(rlist, count):
    remove_client(rlist,count)
    clientsocket.send("Bye")

def handle_remove(rlist, count):
    remove_RFC(rlist[1],rlist,count)
    clientsocket.send("Done")




def peer_handler(data,clientsocket,clientaddr):
    global count
    print "*"*37
    print "Request received from Client :"
    print data
    print "*"*37
    rlist=shlex.split(data)
    if rlist[0] == 'REGISTER':
        handle_register(data, clientsocket)

    elif rlist[0] == 'LISTALL':
        handle_list(clientsocket)
    
    elif rlist[0] == 'LOOKUP':
        handle_lookup(clientsocket)
        
    elif rlist[0] == 'ADD':
        handle_add(clientsocket, rlist, count, data)
        
    elif rlist[0] == 'EXIT':
        handle_exit(rlist, count)
        
    elif rlist[0] == 'REMOVE':
        handle_remove(rlist, count)
        


def remove_RFC(rfc_number,rlist,count):
     rfc_pos = 0
     phostname=rlist[4]
     peerport=rlist[6]
     rfc_title=rlist[8]
     for q in index_list:
        if q.rfc_number==rfc_number and q.peerHostname==phostname and q.peerid == count:
            del index_list[rfc_pos]
        rfc_pos = rfc_pos + 1
            

def remove_client(rlist, count):
    global peerhost
    templ=list()
    temil=list()
    phostname=rlist[3]
    peerport=rlist[5]
    for q in peer_list:
        if q.peerPortNo==peerport:
            peerhost=q.peerHostname
            idx2=[x for x,y in enumerate(index_list) if y.peerHostname==str(peerhost)]
            for i in sorted(idx2, reverse=True):
                del index_list[i]
    
    
    idx=[x for x,y in enumerate(peer_list) if y.peerPortNo==peerport]
    for i in idx:
        del peer_list[i]

def add_peer(data):
    global count
    count = count+1
    rlist=shlex.split(data)
    temp=list()
    a=list()
    b=list()
    rfc_list=str(data).rsplit(':',1)
    c=shlex.split(rfc_list[1])
    peer_list.insert(0,PeerRecord(rlist[3],rlist[5],count))
    for i,j in zip(c[::2],c[1::2]):
        index_list.insert(0,RFCRecord(i,j,rlist[3],count))
    return count

def list_RFC():
    global status
    status=0
    global phrase
    phrase=''

    temp=list()
    if not index_list:
        status=404
        phrase='BAD REQUEST'
    else:
        for x in index_list:
            peer_port = get_port(x.peerid)
            temp.append(RFCRecord(x.rfc_number,x.rfc_title,x.peerHostname,peer_port))
            status=200
            phrase='OK'
    return temp,status,phrase


def find_RFC(rfc_number):
    temp=list()
    flag=0
    for x in index_list:
        if int(x.rfc_number)==int(rfc_number):
            temp.append(RFCRecord(x.rfc_number,x.rfc_title,x.peerHostname,x.peerid))
            code=200
            phrase='OK'
            flag = 1
    
    if(flag==0):
        code=404
        phrase='FILE NOT FOUND'
    return temp,code,phrase


def add_RFC(rfc_number,rlist,count):
    index_list.insert(0,RFCRecord(rfc_number,rlist[8],rlist[4],count))
    code=200
    phrase='OK'
    return index_list,code,phrase

def main_handler(clientsocket, clientaddr):
    data = clientsocket.recv(1024)
    peer_handler(data,clientsocket,clientaddr)


    
if __name__=="__main__":
    
    HOST=socket.gethostname()
    PORT=SERVER_PORT
    print HOST
    serversocket = socket.socket()
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind((HOST,PORT))

    serversocket.listen(5)

    print "Server is listening for connection \n"
    
    while(1):
        
        clientsocket, clientaddr = serversocket.accept()
        serverThread = threading.Thread(target=main_handler, args=(clientsocket,clientaddr))
        serverThread.start()
    serversocket.close()

    

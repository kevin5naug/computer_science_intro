import time
import socket
import select
import sys
import string
import indexer
import pickle as pkl
from chat_utils import *
import chat_group as grp

class Server:
    def __init__(self):
        self.new_clients = [] #list of new sockets of which the user id is not known
        self.logged_name2sock = {} #dictionary mapping username to socket
        self.logged_sock2name = {} # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        self.sentnums={}
        #start server
        self.server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        #initialize past chat indices
        self.indices={}
        # sonnet
        self.sonnet_f = open('AllSonnets.txt.idx', 'rb')
        self.sonnet = pkl.load(self.sonnet_f)
        self.sonnet_f.close()
        # new connecting dictionary
        self.enconnect_dict = {}
        
    def new_client(self, sock):
        #add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        #read the msg that should have login code plus username
        msg = myrecv(sock)
        if len(msg) > 0:
            code = msg[0]

            if code == M_LOGIN:
                name = msg[1:]
                if self.group.is_member(name) != True:
                    self.enconnect_dict[name] = False
                    #move socket from new clients list to logged clients
                    self.new_clients.remove(sock)
                    #add into the name to sock mapping
                    self.logged_name2sock[name] = sock
                    self.logged_sock2name[sock] = name
                    #load chat history of that user
                    print(name + ' logged in')
                    self.group.join(name)
                    mysend(sock, M_LOGIN + 'ok')
                else: #a client under this name has already logged in
                    mysend(sock, M_LOGIN + 'duplicate')
                    print(name + ' duplicate login attempt')
            else:
                print ('wrong code received')
        else: #client died unexpectedly
            self.logout(sock)

    def logout(self, sock):
        #remove sock from all lists
        name = self.logged_sock2name[sock]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        if name in self.sentnums:
            del self.sentnums[name]
        self.all_sockets.remove(sock)
        del self.enconnect_dict[name]
        self.group.leave(name)
        sock.close()

#==============================================================================
# main command switchboard
#==============================================================================
    def handle_msg(self, from_sock):
        #read msg code 
        msg = myrecv(from_sock)
        if len(msg) > 0:
            code = msg[0]           
#==============================================================================
# handle connect request
#==============================================================================
            
            if code == M_ENCRYPTRUE:
                from_name = self.logged_sock2name[from_sock]
                self.enconnect_dict[from_name] = True

            if code == M_ENCRYPTFALSE:
                from_name=self.logged_sock2name[from_sock]
                self.enconnect_dict[from_name]=False

            if code == M_CONNECT:
                to_name = msg[1:]
                from_name = self.logged_sock2name[from_sock]
                if self.enconnect_dict[to_name] == False:
                    if to_name == from_name:
                        msg = M_CONNECT + 'hey you'
                    # connect to the peer
                    elif self.group.is_member(to_name):
                        to_sock = self.logged_name2sock[to_name]
                        self.group.connect(from_name, to_name)
                        the_guys = self.group.list_me(from_name)
                        msg = M_CONNECT + 'ok'
                        for g in the_guys[1:]:
                            to_sock = self.logged_name2sock[g]
                            mysend(to_sock, M_CONNECT + from_name)
                    else:
                        msg = M_CONNECT + 'no_user'
                    mysend(from_sock, msg)

                else:
                    msg = M_CONNECT + "Cannot join encypted channel"
                    mysend(from_sock, msg)

            elif code== M_ENCONNECT:
                to_name = msg[1:]
                from_name = self.logged_sock2name[from_sock]
                if self.enconnect_dict[to_name] == False:
                    if to_name == from_name:
                        msg = M_ENCONNECT + 'hey you'
                    # connect to the peer
                    elif self.group.is_member(to_name):
                        to_sock = self.logged_name2sock[to_name]
                        if self.group.enconnect(from_name, to_name)==True:
                            msg = M_ENCONNECT + 'ok'
                            mysend(to_sock, M_ENCONNECT + from_name)
                        else:
                            msg=M_ENCONNECT+'busy'
                    else:
                        msg = M_ENCONNECT + 'no_user'
                    mysend(from_sock, msg)
                else:
                    msg = M_ENCONNECT + "Cannot join encypted channel"
                    mysend(from_sock, msg)

            elif code == M_GETSENTNUM:
                sentnum=int(msg[1:].strip())
                from_name= self.logged_sock2name[from_sock]
                self.sentnums[from_name]=sentnum
                msg = M_GETSENTNUM+'ok'
                mysend(from_sock,msg)

            elif code == M_ENSETTING:
                target_name = msg[1:]
                if target_name in self.sentnums:
                    msg=M_ENSETTING+str(self.sentnums[target_name])
                else:
                    msg=M_ENSETTING+'Fail'
                mysend(from_sock, msg)
                
                
#==============================================================================
# handle message exchange   
#==============================================================================
            elif code == M_EXCHANGE:
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                said = msg[1:]
                print(said)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]               
                    mysend(to_sock, msg)
#==============================================================================
#listing available peers
#==============================================================================
            elif code == M_LIST:
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all(from_name)
                mysend(from_sock, msg)
#==============================================================================
#retrieve a sonnet
#==============================================================================
            elif code == M_POEM:
                poem_indx = int(msg[1:])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_sect(poem_indx)
                print('here:\n', poem)
                mysend(from_sock, M_POEM + poem)
#==============================================================================
#time
#==============================================================================
            elif code == M_TIME:
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, ctime)
#==============================================================================
#search
#==============================================================================




#==============================================================================
# the "from" guy has had enough (talking to "to")!
#==============================================================================
            elif code == M_DISCONNECT:
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                self.enconnect_dict[from_name] = False
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    self.enconnect_dict[g] = False
                    mysend(to_sock, M_DISCONNECT)
#==============================================================================
#the "from" guy really, really has had enough
#==============================================================================
            elif code == M_LOGOUT:
                self.logout(from_sock)
        else:
            #client died unexpectedly
            self.logout(from_sock)   

#==============================================================================
# main loop, loops *forever*
#==============================================================================
    def run(self):
        print ('starting server...')
        while(1):
           read,write,error=select.select(self.all_sockets,[],[])
           print('checking logged clients..')
           for logc in list(self.logged_name2sock.values()):
               if logc in read:
                   self.handle_msg(logc)
           print('checking new clients..')
           for newc in self.new_clients[:]:
               if newc in read:
                   self.login(newc)
           print('checking for new connections..')
           if self.server in read :
               #new client request
               sock, address=self.server.accept()
               self.new_client(sock)
           
def main():
    server=Server()
    server.run()

main()

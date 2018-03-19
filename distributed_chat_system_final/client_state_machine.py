# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 00:00:32 2015

@author: zhengzhang
"""
from chat_utils import *
from numpy.random import RandomState
import pickle as pkl
import indexer

def isprime(n):
    if type(n)!=int:
        return False
    else:
        if n==2 or n==3:
            return True
        if n<2 or n%2==0:
            return False
        if n<9:
            return True
        if n%3==0:
            return False
        test=5
        r=int(n**(0.5))
        while test<=r:
            if n%test==0:
                return False
            test+=1
        return True

def gcd(a,b):
    while b!=0:
        a,b=b,a%b
    return a

def primeroots(n):
    roots=[]
    required_elements=set(num for num in range(1,n) if gcd(num,n)==1)
    for r in range(1,n):
        real_elements=set(pow(r,power)%n for power in range(1,n))
        if required_elements==real_elements:
            roots.append(r)
    return roots

def isbase(clock,base):
    baselst=primeroots(clock)
    if base in baselst:
        return True
    else:
        return False

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.clock=191
        self.base=19
        self.key=None
        self.settingstate=False
        self.sharedkey=None
        self.encryptkey=None
        self.decryptkey=None
        self.encryptionstate=False
        self.indices={}

    def set_state(self, state):
        self.state = state
        
    def get_state(self):
        return self.state
    
    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def get_sentnum(self):
        return ((self.base)**(self.key))%(self.clock)
        
    def connect_to(self, peer):
        msg = M_CONNECT + peer
        mysend(self.s, msg)
        response = myrecv(self.s)
        if response == (M_CONNECT+'ok'):
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response == (M_CONNECT + 'busy'):
            self.out_msg += 'User is busy. Please try again later\n'
        elif response == (M_CONNECT + 'hey you'):
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        elif response == (M_CONNECT + "Cannot join encypted channel"):
            self.out_msg += 'You are unable to join a secure channel \n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return (False)

    def enconnect(self,peer):
        msg=M_ENCONNECT+ peer
        mysend(self.s, msg)
        response=myrecv(self.s)
        if response==(M_ENCONNECT+'ok'):
            self.peer=peer
            self.out_msg +='You are connected with '+ self.peer + '\n'
            self.out_msg+= 'Your massages are all encrypted from now on.'+'\n'
            return (True)
        elif response == (M_ENCONNECT + 'busy'):
            self.out_msg += 'User is busy. Please try again later\n'
        elif response == (M_ENCONNECT + 'hey you'):
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        elif response == (M_ENCONNECT + "Cannot join encypted channel"):
            self.out_msg += 'You are unable to join a secure channel \n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return (False)

    def translate(self, text, size=4):
        new_text=''
        for item in text:
            index=str(ord(item))
            new_item='0'*(size-len(index))+index
            new_text+=new_item
        return new_text

    def keysequence(self, key, length):
        prng=RandomState(key)
        seq=prng.randint(0,127, size=length)
        return seq

    def encrypt(self, text, key, size=4):
        ciphertext=''
        length=int(len(text)/size)
        keyseq=self.keysequence(key,length)
        for index in range(length):
            plainnum1=text[(size*index):(size*index+size)]
            if plainnum1=='0000':
                plainnum=0
            else:
                plainnum=int(plainnum1.lstrip('0'))
            shortkey=int(keyseq[index])
            ciphernum=int((plainnum+shortkey)%128)
            ciphernum='0'*(size-len(str(ciphernum)))+str(ciphernum)
            ciphertext+=ciphernum
        return ciphertext

    def decrypt(self, text, key, size=4):
        plaintext=''
        length=int(len(text)/size)
        keyseq=self.keysequence(key,length)
        for index in range(length):
            cyphernum1=text[(size*index):(size*index+size)]
            if cyphernum1=='0000':
                cyphernum=0
            else:
                cyphernum=int(cyphernum1.lstrip('0'))
            shortkey=int(keyseq[index])
            plainnum=int((cyphernum-shortkey)%128)
            plainnum='0'*(size-len(str(plainnum)))+str(plainnum)
            plaintext+=plainnum
        return plaintext

    def translateback(self, text, size=4):
        original_text=''
        length=int(len(text)/size)
        for index in range(length):
            fraction_raw=text[(size*index):(size*index+size)]
            fraction=fraction_raw.lstrip('0')
            fraction=int(fraction)
            item=chr(fraction)
            original_text+=item
        return original_text
            

    def disconnect(self):
        msg = M_DISCONNECT
        mysend(self.s, msg)
        self.sharedkey=None
        self.encryptkey=None
        self.decryptkey=None
        self.encryptionstate=False
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''

    def encryptsetting(self):
        return self.clock, self.base, self.key

    def proc(self, my_msg, peer_code, peer_msg):
        self.out_msg = ''
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:
                
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    pkl.dump(self.indices[self.me], open(self.me + '.idx','wb'))
                    del self.indices[self.me]
                    self.state = S_OFFLINE
                    
                elif my_msg == 'time':
                    mysend(self.s, M_TIME)
                    time_in = myrecv(self.s)
                    self.out_msg += "Time is: " + time_in
                            
                elif my_msg == 'who':
                    mysend(self.s, M_LIST)
                    logged_in = myrecv(self.s)
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg =='ENCRYPTSETTING':
                    clock, base, key= self.encryptsetting()
                    self.out_msg += "The clock size: "+str(clock)
                    self.out_msg += "The base: "+str(base)
                    self.out_msg +='The key: '+str(key)

                elif my_msg =='RESET_ENCRYPT':
                    self.out_msg += "To reset the key, type in 'RESET_KEY'+'The new key number' without space. (eg. RESET_KEY9) \n"

                elif my_msg[:9]=='RESET_KEY':
                    new_key=int(my_msg[9:].strip())
                    self.key=new_key
                    self.out_msg+='RESET_KEY Action: Pass \n'
                    passbasetest=isbase(self.clock, self.base)
                    if passbasetest:
                        self.out_msg+='New Encryption System Compatibility Check: Pass \n'
                        self.settingstate=True
                        mysend(self.s, M_GETSENTNUM+str(self.get_sentnum()))
                        response=myrecv(self.s)
                        if response==M_GETSENTNUM+'ok':
                            self.out_msg += 'System update completed.\n'
                    else:
                        self.out_msg+='New Encryption system Compatibility Check: Fail \n'
                        self.out_msg+='WARNING: The base must be a primitive root of the new clock size.'
                        self.settingstate=False
                    

                elif my_msg[:9]=='ENCRYPT_C':
                    if self.settingstate==True:
                        peer= my_msg[9:]
                        peer=peer.strip()
                        mysend(self.s, M_ENSETTING+peer)
                        response=myrecv(self.s)
                        if response != (M_ENSETTING+'Fail'):
                            response=response[1:]
                            response_num=int(response.strip())
                            self.sharedkey=((response_num)**(self.key))%(self.clock)
                            self.encryptkey=self.sharedkey
                            self.decryptkey=self.sharedkey
                            self.encryptionstate=True
                            mysend(self.s, M_ENCRYPTRUE)
                            if self.enconnect(peer)==True:
                                self.state= S_CHATTING
                                self.out_msg += '[Encryption] Connect to ' + peer + '. [Encryption] Chat away!\n\n'
                                self.out_msg +='Encryption System Initiated.'
                                self.out_msg += '-----------------------------------\n'
                            else:
                                self.encryptionstate=False
                                self.sharedkey=None
                                self.encryptkey=None
                                self.decryptkey=None
                                mysend(self.s, M_ENCRYPTFALSE)
                                self.out_msg += 'Connection unsuccessful\n'
                        else:
                            self.out_msg += 'Target Encryption System is not enabled. \n'
                    else:
                        self.out_msg+= 'Encryption system setting error. Please reset your encryption system key. \n'
                    
                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'
                        
                elif my_msg[0] == 'p':
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, M_POEM + poem_idx)
                    poem = myrecv(self.s)[1:].strip()
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    search_rslt = (self.indices[self.me].search(term)).strip()
                    if (len(search_rslt)) > 0:
                        self.out_msg += search_rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'
                else:
                    self.out_msg += menu
                    
            if len(peer_msg) > 0:
                if peer_code == M_CONNECT:
                    self.peer = peer_msg
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer 
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                if peer_code == M_ENCONNECT:
                    self.peer = peer_msg
                    mysend(self.s, M_ENSETTING+ self.peer)
                    response=myrecv(self.s)
                    if response!=M_ENSETTING+'Fail':
                            response_num=int(response[1:].strip())
                            self.sharedkey=(response_num)**(self.key)%(self.clock)
                            self.encryptionstate=True
                            mysend(self.s, M_ENCRYPTRUE)
                            self.encryptkey=self.sharedkey
                            self.decryptkey=self.sharedkey
                    else:
                        print('Target Encryption System is not enabled.')
                    self.out_msg += '[ENCRYPTION] Request from ' + self.peer + '\n'
                    self.out_msg += '[ENCRYPTION] You are connected with ' + self.peer 
                    self.out_msg += '. [ENCRYPTION] Chat away!\n\n'
                    self.out_msg +='Encryption System Initiated'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                    
                    
#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if len(my_msg) > 0:     # my stuff going out
                my_msg_extended='['+self.me+']: '+my_msg
                history_msg=text_proc(my_msg_extended)
                self.indices[self.me].add_msg_and_index(history_msg)
                if self.encryptionstate==True:
                    new_msg=self.translate(my_msg_extended)
                    sent_msg=self.encrypt(new_msg, self.encryptkey)
                    self.encryptkey+=1
                else:
                    sent_msg=my_msg_extended
                mysend(self.s, M_EXCHANGE + sent_msg)
                if my_msg == 'bye':
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
            if len(peer_msg) > 0:    # peer's stuff, coming in
                if peer_code == M_CONNECT:
                    self.out_msg += "(" + peer_msg + " joined)\n"
                else:
                    if self.encryptionstate==True:
                        plain_msg=self.decrypt(peer_msg, self.decryptkey)
                        self.decryptkey+=1
                        real_msg=self.translateback(plain_msg)
                    else:
                        real_msg=peer_msg
                    self.indices[self.me].add_msg_and_index(text_proc(real_msg))
                    self.out_msg += real_msg

            # I got bumped out
            if peer_code == M_DISCONNECT:
                self.sharedkey=None
                self.encryptkey=None
                self.decryptkey=None
                self.encryptionstate=False
                
                self.state = S_LOGGEDIN

            # Display the menu again
            if self.state == S_LOGGEDIN:
                self.out_msg += menu
#==============================================================================
# invalid state                       
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)
            
        return self.out_msg

# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 18:22:44 2014

@author: zzhang
"""

# -*- coding: utf-8 -*-
"""
Created on Sat Jul  5 11:38:58 2014

@author: zzhang
"""
import pickle
from indexer import *

def main():
#%% input/output files
    in_file_name = 'AllSonnets.txt'
#    in_file_name = 'hamlet.txt'
    out_file_name = in_file_name + '.idx'
    read_file = open(in_file_name, 'r')
    out_file = open(out_file_name, 'wb')

#%% initialization
    my_index = Index(in_file_name)
#    my_index.add_msg(in_file_name)
    num_lines = 0

#%% roman index stuff
    roman_int_f = open('roman.txt.pk', 'rb')
    int2roman = pickle.load(roman_int_f)
    roman2int = pickle.load(roman_int_f)
    roman_int_f.close()
    
#%% process the inputs
    print('Reading files:')
    li = read_file.readline()
    sec_marks = []
    num_secs = 0
    while li != '':
        li = li.rstrip()
        num_lines += 1
        if num_lines % 1000 == 0:
            print(num_lines, '...')
        if li != '':
            my_index.add_msg_and_index(li)
        else:
            my_index.add_msg(li)
        if li.rstrip('.') in roman2int.keys():
            num_secs += 1
            sec_marks.append(my_index.get_msg_size() - 1)
        li = read_file.readline()
    sec_marks.append(my_index.get_msg_size() - 1)
    
#%% build the frequency list/
    print('Build frequency map\n')
    my_index.build_wf_list()          
#%% print top words, with or without the messages   
    to_print = 40
    my_index.print_top_freq_word(to_print, True)   
#%%
    my_index.print_stats()
#%%
    print('\ntotal sections', num_secs)
    for i in range(len(sec_marks) - 1):
        my_index.set_sect_begin_end(i + 1, sec_marks[i], sec_marks[i + 1])
#%%
    pickle.dump(my_index, out_file)        
#%%      
    p = my_index.get_sect(154)
    print(p)
    
    return my_index    
    
main()




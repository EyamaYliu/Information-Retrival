#!/usr/bin/env python
import sys
import re
import os
import subprocess
import math
from collections import defaultdict

"""
This program is almost directly conversion from vector1.prl.
The purpose is to help people save some time if they are more
comfortable of using python. However, don't trust this script,
and use it with caution. If you find any bug or possible mistake,
please email zzhang84@jhu.edu

Hint: search "To be implemented"

##########################################################
##  VECTOR1
##
##  Usage:   vector1     (no command line arguments)
##
##  The function &main_loop below gives the menu for the system.
##
##  This is an example program that shows how the core
##  of a vector-based IR engine may be implemented in Perl.
##
##  Some of the functions below are unimplemented, and some
##  are only partially implemented. Suggestions for additions
##  are given below and in the assignment handout.
##
##  You should feel free to modify this program directly,
##  and probably use this as a base for your implemented
##  extensions.  As with all assignments, the range of
##  possible enhancements is open ended and creativity
##  is strongly encouraged.
##########################################################


############################################################
## Program Defaults and Global Variables
############################################################
"""

DIR, file_name = os.path.split(os.path.realpath(__file__))
HOME = "."

token_docs_tank = DIR + "/tank"                 # tokenized tank docs
corps_freq_tank = DIR + "/tank"                 # frequency of each token in the doc.
titles_tank = DIR + "/tank.titles"             # titles of each article in cacm

token_docs_plant = DIR + "/plant"               # tokenized plant docs
corps_freq_plant = DIR + "/plant"               # frequency of each token in the plant.
titles_plant = DIR + "/plant.titles"             # titles of each article in cacm

token_docs_perplace = DIR + "/perplace"         # tokenized perplace docs
corps_freq_perplace = DIR + "/perplace"         # frequency of each token in the docs.
titles_perplace = DIR + "/perplace.titles"             # titles of each article in cacm

stoplist = DIR + "/common_words"           # common uninteresting words



# these files are created in your "HOME" directory
token_intr = HOME + "/interactive"         # file created for interactive queries
inter_freq = HOME + "/interactive"         # frequency of each token in above

# doc_vector:
# An array of hashes, each array index indicating a particular
# query's weight "vector". (See more detailed below)

doc_vector_tank = []
doc_vector_plant = []
doc_vector_perplace = []

# qry_vector:
# An array of hashes, each array index indicating a particular query's
# weight "vector".

qry_vector = []

# docs_freq_hash
#
# dictionary which holds <token, frequency> pairs where
# docs_freq_hash[token] -> frequency
#   token     = a particular word or tag found in the cacm corpus
#   frequency = the total number of times the token appears in
#               the corpus.

docs_freq_hash_tank = defaultdict(int)
docs_freq_hash_plant = defaultdict(int)
docs_freq_hash_perplace = defaultdict(int)

# corp_freq_hash
#
# dictionary which holds <token, frequency> pairs where
# corp_freq_hash[token] -> frequency
#   token     = a particular word or tag found in the corpus
#   frequency = the total number of times the token appears per
#               document-- that is a token is counted only once
#               per document if it is present (even if it appears
#               several times within that document).

corp_freq_hash_tank = defaultdict(int)
corp_freq_hash_plant = defaultdict(int)
corp_freq_hash_perplace = defaultdict(int)

# stoplist_hash
#
# common list of uninteresting words which are likely irrelvant
# to any query.
# for given "word" you can do:   `if word in stoplist_hash` to check
# if word is in stop list
#
#   Note: this is an associative array to provide fast lookups
#         of these boring words

stoplist_hash = set()

# titles_vector
#
# vector of the cacm journal titles. Indexed in order of apperance
# within the corpus.

titles_vector_tank  = []
titles_vector_plant  = []
titles_vector_perplace  = []

# relevance_hash
#
# a hash of hashes where each <key, value> pair consists of
#
#   key   = a query number
#   value = a hash consisting of document number keys with associated
#           numeric values indicating the degree of relevance the
#           document has to the particular query.
#   relevance_hash[query_num][doc_num] = 1, if given query and doc is relavent

relevance_hash = defaultdict(lambda: defaultdict(int))

#Training and test constants

training_num = 3600
test_num = 400

#Vprofiles for first 3600 training examples in each doc

vprofile1_tank = []
vprofile2_tank = []

vprofile1_plant = []
vprofile2_plant = []

vprofile1_perplace = []
vprofile2_perplace = []



sys.stderr.write("INITIALIZING VECTORS ... \n")

##########################################################
##  INIT_FILES
##
##  This function specifies the names and locations of
##  input files used by the program.
##
##  Parameter:  $type   ("stemmed" or "unstemmed")
##
##  If $type == "stemmed", the filenames are initialized
##  to the versions stemmed with the Porter stemmer, while
##  in the default ("unstemmed") case initializes to files
##  containing raw, unstemmed tokens.
##########################################################

# Switch:
#    You may change this to "stemmed" or "unstemmed"
filename = "unstemmed"


if filename == "stemmed":
    token_docs_tank += ".stemmed"
    corps_freq_tank += ".stemmed.hist"
    token_docs_plant += ".stemmed"
    corps_freq_plant += ".stemmed.hist"
    token_docs_perplace += ".stemmed"
    corps_freq_perplace += ".stemmed.hist"
    stoplist   += ".stemmed"

else:
    token_docs_tank += ".tokenized"
    corps_freq_tank += ".tokenized.hist"
    token_docs_plant += ".tokenized"
    corps_freq_plant += ".tokenized.hist"
    token_docs_perplace += ".tokenized"
    corps_freq_perplace += ".tokenized.hist"

##########################################################
##  INIT_CORP_FREQ
##
##  This function reads in corpus and document frequencies from
##  the provided histogram file for both the tank,plant
##  and the perplace set. This information will be used in
##  term weighting.
##
##  It also initializes the arrays representing the stoplist,
##  title list and relevance of document given query.
##########################################################

for line in open(corps_freq_tank, 'r'):
    per_data = line.strip().split()
    if len(per_data) == 3:
        corp_freq, doc_freq, term = line.strip().split()
        docs_freq_hash_tank[term] = int(doc_freq)
        corp_freq_hash_tank[term] = int(corp_freq)

for line in open(corps_freq_plant, 'r'):
    per_data = line.strip().split()
    if len(per_data) == 3:
        corp_freq, doc_freq, term = line.strip().split()
        docs_freq_hash_plant[term] = int(doc_freq)
        corp_freq_hash_plant[term] = int(corp_freq)

for line in open(corps_freq_perplace, 'r'):
    per_data = line.strip().split()
    if len(per_data) == 3:
        corp_freq, doc_freq, term = line.strip().split()
        docs_freq_hash_perplace[term] = int(doc_freq)
        corp_freq_hash_perplace[term] = int(corp_freq)

for line in open(stoplist, 'r'):
    if line:
        stoplist_hash.add(line.strip())

# push one empty value onto titles_vector
# so that indices correspond with title numbers.
# title looks like:
# titles_vector[3195] = "   1  1  MILITARY  The commander of the TANK unit reportedly told a Russia"

titles_vector_tank.append("")
sensenum_tank = ['0']
for line in open('tank.titles', 'r'):
    if line:
        titles_vector_tank.append(line.strip())
        sensenum_tank.append(line.strip().split()[1])
	


titles_vector_plant.append("")
sensenum_plant = ['0']
for line in open('plant.titles', 'r'):
    if line:
        titles_vector_plant.append(line.strip())
        sensenum_plant.append(line.strip().split()[1])


titles_vector_perplace.append("")
sensenum_perplace = ['0']
for line in open('perplace.titles', 'r'):
    if line:
        titles_vector_perplace.append(line.strip())
        sensenum_perplace.append(line.strip().split()[1])




##########################################################
##  INIT_DOC_VECTORS
##
##  This function reads in tokens from the document file.
##  When a .I token is encountered, indicating a document
##  break, a new vector is begun. When individual terms
##  are encountered, they are added to a running sum of
##  term frequencies. To save time and space, it is possible
##  to normalize these term frequencies by inverse document
##  frequency (or whatever other weighting strategy is
##  being used) while the terms are being summed or in
##  a posthoc pass.  The 2D vector array
##
##    doc_vector[ doc_num ][ term ]
##
##  stores these normalized term weights.
##
##  It is possible to weight different regions of the document
##  differently depending on likely importance to the classification.
##  The relative base weighting factors can be set when
##  different segment boundaries are encountered.
##
##  This function is currently set up for simple TF weighting.
##########################################################


#######################################
#   Determine which weighting method to use
#   method: 0 = uniform
#           1 = expndecay
#           2 = stepped
#           3 = customized
#######################################

def word_weight_changer(dict,keylist,method = 0):
    length = len(keylist)

    for key in dict:
        if key[:3].lower() == '.x-':
            keyword = key

    if method == 0:
        return dict
    elif method == 1:

        pos = 0
        for i,v in enumerate(keylist):
            if v == keyword:
                pos = i
        for i,v in enumerate(keylist):
            distance = abs(i - pos)
            if distance != 0:
                dict[keylist[i]] /= distance
        return dict

    elif method == 2:
        for i,v in enumerate(keylist):
            if v == keyword:
                dict[keylist[i]] = 6
                if i - 1 >=0:
                    dict[keylist[i-1]] = 6
                if i - 2 >=0:
                    dict[keylist[i-2]] = 3
                if i - 3 >=0:
                    dict[keylist[i-3]] = 3

                if i + 1 < length:
                    dict[keylist[i+1]] = 6
                if i + 2 < length:
                    dict[keylist[i+2]] = 3
                if i + 3 < length:
                    dict[keylist[i+3]] = 3 
        return dict

    # Custom method,step down with respect to distance. 
    elif method == 3:
        pos = 0
        for i,v in enumerate(keylist):
            if v == keyword:
                pos = i
        for i,v in enumerate(keylist):
            distance = abs(i - pos)
            dict[keylist[i]] = 8 - distance
            if dict[keylist[i]] < 0:
                dict[keylist[i]] = 0
                
        return dict
        


def LR_adder(keylist):
    
    for key in keylist:
        if key[:3].lower() == '.x-':
            keyword = key

    for i,v in enumerate(keylist):
        if v == keyword:
            if i-1 >=0:
                keylist[i-1] = 'L-'+ keylist[i-1]
            if i+1 <len(keylist):
                keylist[i+1] = 'R-'+ keylist[i+1]
    return keylist
    

def Lastline_I_detect(token_docs):
    file = open(token_docs, 'r')
    line =file.readlines()
    if line[-1][:2] =='.I':
        pass
    else:
        file.close()
        file = open(token_docs,'a')
        file.write('\n.I')

    file.close()


def doc_vector_creator(token_docs,docs_freq_hash):
    tweight = 1
    doc_vector = []
    # push one empty value onto qry_vectors so that
    # indices correspond with query numbers
    doc_vector.append(defaultdict(int))

    doc_num = 0

    #Switch:
    #    1-bag-of-words/2-adjacent-separate-LR
    #    Decide whether use LR mode instead 1-bag-of-words
    isUsingLR = False    

    Lastline_I_detect(token_docs)

    for word in open(token_docs, 'r'):
        word = word.strip()


        if not word or word == '.I 0':
            continue  # Skip empty line
        
        if word[:2] == '.I':
            if doc_num == 0:
                doc_num += 1
                keylist = []
                new_doc_vec = defaultdict(int)
            else:
                
                if isUsingLR:
                    keylist = LR_adder(keylist)



                for term in keylist:
                    new_doc_vec[term] += tweight

                doc_vector.append(new_doc_vec)

                #Switch: determine which method to use
                doc_vector[doc_num] = word_weight_changer(doc_vector[doc_num],keylist,3)

                keylist = []
                new_doc_vec = defaultdict(int)

                doc_num += 1
        elif word not in stoplist_hash and re.search("[a-zA-Z]", word):
            if docs_freq_hash[word] == 0:
                exit("ERROR: Document frequency of zero: " + word + \
                     " (check if token file matches corpus_freq file\n")
            keylist.append(word)

    return doc_vector

doc_vector_tank = doc_vector_creator(token_docs_tank,docs_freq_hash_tank)
doc_vector_plant = doc_vector_creator(token_docs_plant,docs_freq_hash_plant)
doc_vector_perplace = doc_vector_creator(token_docs_perplace,docs_freq_hash_perplace)



def vP1_vP2_creator(doc_vec,senses):

    vP1 = defaultdict(int)
    vP2 = defaultdict(int)

    vP1cnt = defaultdict(int)
    vP2cnt = defaultdict(int)

    for i in range(1,training_num+1):
        vector = doc_vec[i]
        for each_term in vector:
            if senses[i] == '1':
                vP1[each_term] += vector[each_term]
                vP1cnt[each_term] += 1
            else:
                vP2[each_term] += vector[each_term]
                vP2cnt[each_term] += 1



    for each_term in vP1:
        vP1[each_term] /= vP1cnt[each_term]


    for each_term in vP2:
        vP2[each_term] /= vP2cnt[each_term]


    return vP1,vP2

vprofile1_tank,vprofile2_tank = vP1_vP2_creator(doc_vector_tank,sensenum_tank)
vprofile1_plant,vprofile2_plant = vP1_vP2_creator(doc_vector_plant,sensenum_plant)
vprofile1_perplace,vprofile2_perplace = vP1_vP2_creator(doc_vector_perplace,sensenum_perplace)






###################
## MAIN_LOOP
##
###################


def main():
    menu = \
    "============================================================\n"\
    "==      Welcome to the 600.466 Vector-based IR Engine       \n"\
    "==        We really pretend to give you some option         \n"\
    "==                                                          \n"\
    "============================================================\n"\
    "                                                            \n"\
    "OPTIONS:                                                    \n"\
    "  1 = Do some prediction on tank                            \n"\
    "  2 = Do some prediction on plant                           \n"\
    "  3 = Do some prediction on people/place                    \n"\
    "  4 = Quit                                                  \n"\
    "                                                            \n"\
    "============================================================\n"

    while True:
        sys.stderr.write(menu)
        option = input("Enter Option: ")
        if option == "1":
            predict(vprofile1_tank,vprofile2_tank,doc_vector_tank,sensenum_tank)
        elif option == "2":
            predict(vprofile1_plant,vprofile2_plant,doc_vector_plant,sensenum_plant)
        elif option == "3":
            predict(vprofile1_perplace,vprofile2_perplace,doc_vector_perplace,sensenum_perplace)
        elif option == "4":
            exit(0)
        else:
            sys.stderr.write("Input seems not right, try again\n")


def predict(vP1,vP2,doc_vec,sense):

    correct = 0

    prediction = {}
    for i in range(training_num+1,training_num+test_num+1):
        res1 = cosine_sim_a(vP1,doc_vec[i])
        res2 = cosine_sim_a(vP2,doc_vec[i])
        if res1 > res2:
            prediction[i] = 1
        else:
            prediction[i] = 2

    for i in prediction:
        if int(prediction[i]) == int(sense[i]):
            correct += 1

    correctness = correct/test_num
    print('The percentage of correctness of this prediction is',correctness*100,'%.\n')
        




def cosine_sim_a(vec1, vec2, vec1_norm = 0.0, vec2_norm = 0.0):
    if not vec1_norm:
        vec1_norm = sum(v * v for v in vec1.values())
    if not vec2_norm:
        vec2_norm = sum(v * v for v in vec2.values())

    # save some time of iterating over the shorter vec
    if len(vec1) > len(vec2):
        vec1, vec2 = vec2, vec1

    # calculate the cross product
    cross_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in vec1.keys())
    return cross_product / math.sqrt(vec1_norm * vec2_norm)



def KNN(doc_vec):
    





if __name__ == "__main__": main()








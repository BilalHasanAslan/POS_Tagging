import string
import csv
import copy
import math
import time

# Method that trains on data
def train_emmision_transition(filename):
    # Variables
    tags = {}
    transition = {}
    alltags = []
    allwords = []
    # Opens Training Data
    with open(filename, 'r') as trainingobj:
        traindata = csv.reader(trainingobj)
        # Setting Starting Node
        oldtag = "STARTINGNODE"
        # Going Row by Row , So Word By Word
        for row in traindata:
            word = row[0]
            tag = row[1]
            # Skipping Header
            if not word == "Token":
                #Checking If We Already Observed Data Word If Not Added To List
                if word not in allwords:
                    allwords.append(word)
                #If Word Is not Emptry
                if not word == "":
                    #Skipping Word If It Is Puncuation
                    if word not in string.punctuation:
                        #Cheking If We Have Seen POS Tag Before
                        if tag in tags:
                            #Increamenting Word In The Tags
                            if word in tags[tag]:
                                words = tags[tag]
                                words[word] += 1
                                tags[tag] = words
                            #Adding That Word To The Tags
                            else:
                                words = tags[tag]
                                words[word] = 1
                                tags[tag] = words
                        #Adding The New Tag With The Word
                        else:
                            words = {}
                            words[word] = 1
                            tags[tag] = words
                    #Training For Transitions
                    #Cheking If it is End Of Sentence
                    if word == ".":
                        tag = "ENDINGNODE"
                        #Checking If Previous Tag In The Transition Table
                        if oldtag in transition:
                            #If Tag Connected to Previous Tag Before Just Increment By 1
                            if tag in old:
                                old[tag] += 1
                                transition[oldtag] = old
                            #If Tag Is Not Connected to Previous Tag Before Just Make It 1
                            else:
                                old[tag] = 1
                                transition[oldtag] = old
                        #Add Previous Tag If It Is Not In Transitition Table
                        else:
                            new_transition = {}
                            new_transition[tag] = 1
                            transition[oldtag] = new_transition
                        #Reset The Previous Tag to Starting Node Since It is End Of Sentence
                        oldtag = "STARTINGNODE"

                    else:
                        #Skipping Word If It Is Puncuation
                        if word not in string.punctuation:
                            #Checking If We Observed Tag Before
                            if tag not in alltags:
                                alltags.append(tag)
                            #Checking If Previous Tag In The Transition Table
                            if oldtag in transition:
                                old = transition[oldtag]
                                #If Tag Connected to Previous Tag Before Just Increment By 1
                                if tag in old:
                                    old[tag] += 1
                                #If Tag Is Not Connected to Previous Tag Before Just Make It 1
                                else:
                                    old[tag] = 1
                            #Add Previous Tag If It Is Not In Transitition Table
                            else:
                                new_transition = {}
                                new_transition[tag] = 1
                                transition[oldtag] = new_transition
                            #Making Current Tag To Previous Tag
                            oldtag = tag
    #Creating Dummy Tags Dictonary
    temptags = copy.deepcopy(tags)
    #Calculating Word to POS Tagging Probabilities
    for i in tags:
        k = 0
        tag = tags[i]
        #Calculating Number Of Words In the tag
        for j in tag:
            k += tag[j]
        #Calculating Probabilty
        for j in tag:
            #Using Logarithmic Probability
            tag[j] = math.log10(tag[j]/k)
        #Update Values
        tags[i] = tag

    #Adding End Node Temporarily
    alltags.append("ENDINGNODE")
    #Calculating Transition Table Probabilities
    for i in alltags:
        #Counts All The Times Tag Is Mentioned
        c = 0
        #Checks All The Transitions
        for j in transition:
            f = transition[j]
            #Checks If Connection Exists If No 1 Added for Smoothing
            if i in f:
                c += f[i]
            else:
                f[i] = 1
                c += 1
        #Calculating Probabilties
        for j in transition:
            f = copy.deepcopy(transition[j])
            #Using Logarithmic Probability
            f[i] = math.log10(f[i]/c)
            transition[j] = f
    #Remove The Temporary Tag
    alltags.remove("ENDINGNODE")
    #Return Values
    return tags, transition, alltags, allwords, temptags

#Sentence Checker For Testing
def check(sen, tags, transition, alltags, allwords, temptags):
    #Variables
    dyn = {}
    backpoint = {}
    size = len(sen)
    #Preparing Tables for Dynamic Programing
    for i in range(size):
        k = {}
        for j in alltags:
            k[j] = -9999
        dyn[i] = k
        backpoint[i] = {}
    #Calculating Probabilty With Viterbi algorithm Only For First Column
    for i in alltags:
        #Calculating Probabilty Of Known Word
        if sen[0] in allwords:
            p = -9999
            if sen[0] in tags[i]:
                h = tags[i]
                p = h[sen[0]]
                z = transition["STARTINGNODE"]
                p = p + z[i]
                f = dyn[0]
                f[i] = p
        #Calculating Probability for Unknown Word
        else:
            temp2tags = temptags
            k = 0
            c = 0
            tag = temp2tags[i]
            for j in tag:
                c += 1
                k += tag[j]
            p = math.log10(1/(k+c+1))
            z = transition["STARTINGNODE"]
            p = p + z[i]
            f = dyn[0]
            f[i] = p
        t = backpoint[0]
        t[i] = []
        t[i].append(i)
        backpoint[0] = t
    #Calculating Probabilty With Viterbi algorithm Only For The Rest Of Table
    for i in range(1, size):
        for j in alltags:
            #Calculating Probabilty Of Known Word
            if sen[i] in allwords:
                p = -9999
                if sen[i] in tags[j]:
                    k = tags[j]
                    p = k[sen[i]]
                    p2 = -9999
                    for prev in alltags:
                        k = transition[prev]
                        z = dyn[i-1]
                        if p2 < k[j] + z[prev]:
                            p2 = k[j] + z[prev]
                            r = backpoint[i-1]
                            t = backpoint[i]
                            if prev in r:
                                str1 = ','.join(r[prev])
                                t[j] = str1.split(",")
                                t[j].append(j)
                                backpoint[i] = t
                                f = dyn[i]
                                f[j] = p2+p
                                dyn[i] = f
            #Calculating Probabilty Of Unknown Word
            else:
                temp2tags = temptags
                k = 0
                c = 0
                tag = temp2tags[j]
                for b in tag:
                    c += 1
                    k += tag[b]
                p = math.log10(1/(k+c+1))
                p2 = -9999
                for prev in alltags:
                    k = transition[prev]
                    z = dyn[i-1]
                    if p2 < k[j] + z[prev]:
                        p2 = k[j] + z[prev]

                        r = backpoint[i-1]
                        t = backpoint[i]
                        if prev in r:
                            str1 = ','.join(r[prev])
                            t[j] = str1.split(",")
                            t[j].append(j)
                            backpoint[i] = t
                            f = dyn[i]
                            f[j] = p2+p
                            dyn[i] = f

    #Calculating Probabilites From Last Node To End Node
    last = dyn[size-2]
    resultp = -9999999999
    lastpoint = backpoint[size-2]
    result = []
    for i in last:
        j = transition[i]
        p = j["ENDINGNODE"]
        if resultp < last[i]+p:
            resultp = last[i]+p
            if i in lastpoint:
                result = lastpoint[i]

    return result

#Main Method
if __name__ == "__main__":
    #Variables
    totaltime = 0
    alltrue = 0
    all = 0
    acc = []
    #Training File
    filename = input("Enter Training Filename\n")
    start = time.time()
    tags, transition, alltags, allwords, temptags = train_emmision_transition(
        filename)
    end = time.time()
    print("Time took for training "+str(end - start)+"s")
    #Testing File
    filename = input("Enter Testing Filename\n")
    #Opening File
    file1 = open("Input_And_Ouput.txt", "w") 
     
    with open(filename, 'r') as testobj:
        testdata = csv.reader(testobj)
        sen = []
        POS = []
        for row in testdata:
            word = row[0]
            tag = row[1]
            if not word == "Token":
                if word == ".":
                    if not sen == []:
                        sen.append(word)
                        start = time.time()
                        #POS Tagging
                        result = check(sen, tags, transition, alltags, allwords, temptags)
                        end = time.time()
                        totaltime += (end-start)
                        file1.writelines(str(result)+"\n")
                        file1.writelines(str(POS)+"\n")
                        t = 0
                        #Cheking Accuracy of the Sentence
                        for i in range(len(POS)):
                            if POS[i] == result[i]:
                                t += 1
                                alltrue += 1
                        acc.append(t/len(POS))
                        all += len(POS)
                        sen = []
                        POS = []
                else:
                    #Creating Sentence
                    if word not in string.punctuation:
                        sen.append(word)
                        POS.append(tag)
    #Calculating Accuracy
    y = 0
    total = 0
    for i in acc:
        y += 1
        total += i
    #Closing File
    file1.close()
    
    print("Sentence Accuracy is "+str(total/y))
    print("Average Time Taken For Testing Sentences "+str(totaltime/y) + "s")
    print("Paragraph Accuracy is "+str(alltrue/all))
    print("Total Time taken for Testing Data "+str(totaltime) + "s")

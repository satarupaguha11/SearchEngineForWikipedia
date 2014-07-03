from Stemmer import Stemmer
st=Stemmer('english')
from shutil import copyfileobj
import bz2,math,timeit,re
from collections import *

print "Loading Files..."
fieldPattern=re.compile(r'(b|t|c|i|l)+:(\w+)') #regex to determine the different components of a query
pattern=re.compile('\w+')

stopWordFile=open("stopWords.txt","r")
#creating stop word dictionary
stopWordDict=defaultdict(int)
for line in stopWordFile:
    stopWordDict[line.strip()]=1

N=14000000
offsets=[]
with open("vocabFileOffset.txt","r") as f1: #reading offset of the vocabulary list 
    for line in f1:
        offsets.append(int(line.strip()))
    total=len(offsets)
'''
titleMapper=open("sortedTitlePageMapper2.txt","r")

offsetFile=open("titleOffset.txt","r")
offsets2=[]
for line in offsetFile:
	offsets2.append(int(line.strip()))
offsets2=offsets2[:-1]
'''

def stopWordRemoval(word):
    if stopWordDict[word]!=1:
          return word
    else:
	  return 

def stemWord(word):
	word=st.stemWord(word)
	return word
        

# function for binary search in file
def querySearch(query,field):
    query=stopWordRemoval(query)
    if query!=None:
    	query=stemWord(query)
    global uniqueDocs
    f2=open("vocabFileMerged.txt","r")
    high=total-1
    low=0
    count=0
    locations=[]
    while low<=high:
        mid=(low+high)/2 
        offset=offsets[mid]
        f2.seek(offset)
        line=f2.readline()
        word=line.split(' ')[0]
        if query==word:
            locations=line.strip().split(' ')[1:]
            break
        elif query<word:
            high=mid-1 
        else:
            low=mid+1

    postingList=[]
    folderpath={'t':'title','l':'links','c':'category','i':'infobox','b':'body'}
    
    if field=='':
        for location in locations:
            temp=location.split(':')
            folder=temp[0] #the folder in which the query word occurs
            fileNo=temp[1] #the file number in the folder in which the query word occurs
            path="merged/"+folderpath[folder]+"/"+fileNo+".txt.bz2"
            f=bz2.BZ2File(path,"r")
            for line in f:
                word=line.strip().split(' ')[0]
                if word==query:
                    postingList.append(line.strip())
    else:
        for location in locations:
            temp=location.split(':')
            folder=temp[0]
            fileNo=temp[1]
            if folder!=field:
                continue
            else:
                path="merged/"+folderpath[folder]+"/"+fileNo+".txt.bz2"           
		f=bz2.BZ2File(path,"r")
                for line in f:
                    word=line.strip().split(' ')[0]
                    if word==query:
                        postingList.append(line.strip())
                break
    if postingList==[]:
    	#uniqueDocs=''
	return
    else:               
	    postingdict={}
	    for posting in postingList:
		pairs=posting.split(' ')[1:]
		for pair in pairs:
		    temp=pair.split(':')
		    postingdict[temp[0]]=temp[1] #storing the unique documents in a dictionary
	    idf=math.log(N/float(len(posting))) #calculating inverse document frequency

	    for posting in postingList:
		posting=posting.split(' ')[1:]  #do not want the word itself, just its posting list. so [:1]
		for item in posting:
		    temp=item.split(':')
		    page=temp[0]
		    tf=float(temp[1])
		    uniqueDocs[page]+=(tf*idf)  #assigning scores to documents based on tf-idf score
            
    
    #return uniqueDocs
def binarySearchTitle(query):
	query=query+1
	"""
	titleMapper=open("sortedTitlePageMapper2.txt","r")
	offsetFile=open("titleOffset.txt","r")
	offsets=[]
	for line in offsetFile:
		offsets.append(int(line.strip()))
	offsets=offsets[:-1]
	total=len(offsets)
	"""
	
	high=total2
	low=0
	count=0
	while low<=high:
		mid=(low+high)/2 
		offset=offsets2[mid]
		titleMapper.seek(offset)
		line=titleMapper.readline()
		word=line.split(' ')[0]
		word=int(word)
		if query==word:
		    locations=line.strip()
		    break
		elif query<word:
		    high=mid-1 
		else:
		    low=mid+1

	locations=locations.split(' ')[1:]
	title=''
	for location in locations:
		title+=location
		title+=' '
	return title

def processQuery(query):
	query=query.lower().replace('_',' ')
    	#query=re.findall(pattern,query)
    	#words=stopWordRemoval(query)
    	#words=stemWords(words)
	fields=re.findall(fieldPattern,query)
	return fields

#Main function driver

titleMapper=open("sortedTitlePageMapper2.txt","r")
offsetFile=open("titleOffset.txt","r")
offsets2=[]
for line in offsetFile:
	offsets2.append(int(line.strip()))
offsets2=offsets2[:-1]
total2=len(offsets2)

while True:
	print "Enter a query."
	query=raw_input()
	query=query.lower().replace('_',' ')
	#query=processQuery(query)
	s=timeit.default_timer()
	fields=re.findall(fieldPattern,query)
	uniqueDocs=defaultdict(float)
	if fields==[]:
	    query=re.findall(pattern,query)
	    for q in query:
	    	querySearch(q,'')
	else:
	    for pair in fields:
		querySearch(pair[1],pair[0])

	titlePageMapper=open("titlePageMapper.txt","r")
	count=0
	#print uniqueDocs
	if uniqueDocs!={}:
		docs=uniqueDocs.items()
		uniqueDocs=sorted(docs, key=lambda x: x[-1],reverse=True)
		for doc in uniqueDocs:
		    count+=1
		    if count>10:
		    	break
		    print binarySearchTitle(int(doc[0]))
	else:
		print "Not found."
	print "Do you want to continue?(y/n)"
	response=raw_input()
	if response=='n':
		break
e=timeit.default_timer()
print e-s

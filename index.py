import sys,bz2,timeit,re,xml.sax
from shutil import copyfileobj
from collections import defaultdict, OrderedDict
from Stemmer import Stemmer

#Precompiling regular expressions and stemmers
st=Stemmer('english')
pattern=re.compile('[\d+\.]*[\d]+|[\w]+')

#Setting compression factor
compression=4

#Set counters
flag=0
pageNumber=0
TitlefileNumber=0
InfoboxfileNumber=0
LinksfileNumber=0
CategoryfileNumber=0
BodyfileNumber=0
titleCount=0
categoryCount=0
infoboxCount=0
linksCount=0
bodyCount=0

#Set file size limit
limit=10000000

#Initialise index dictionaries
indexTitle=defaultdict(dict)
indexInfobox=defaultdict(dict)
indexCategory=defaultdict(dict)
indexLinks=defaultdict(dict)
indexBody=defaultdict(dict)

#Initialise title to page mapper
f=open("titlePageMapper.txt","w")
titlePageMapper1=defaultdict(dict)

#create stop word dictionary
stopWordFile=open("stopWords.txt","r")
stopWordDict=defaultdict(int)
for line in stopWordFile:
    stopWordDict[line.strip()]=1
print "stop word dictionary built"

#Function for removal of stop words
def stopWordRemoval(words):
    wordBuffer=[]
    for word in words:
      if stopWordDict[word]!=1:
          wordBuffer.append(word)
    return wordBuffer

#Function for stemming words
def stemWords(words):
    wordBuffer=[]
    for word in words:
        word=st.stemWord(word)
        wordBuffer.append(word)
    return wordBuffer

#Function to tokenise title
#Input is title and page number
#Output is a call to title indexer function
def tokenizeTitle(title,pageNumber):
    titlePageMapper1[int(pageNumber)]=title
    f.write(pageNumber)
    f.write(' ')
    f.write(title.strip().encode('utf-8'))
    f.write('\n')
    title=title.lower().replace('_',' ')
    titleWords=re.findall(pattern,title)
    words=stopWordRemoval(titleWords)
    words=stemWords(words)
    #Call to title indexer
    titleIndexer(words,pageNumber)

#Function to tokenise text
#Input is entire text and page number
#Output is a call to text indexer function
def tokenizeText(text, pageNumber):    
    text=text.lower()
    lines=text.split('\n')
    infobox=[]
    category=[]
    body=[]
    tempLink=[]
    flag=0
    for line in lines:
        bodyFlag=0

        #Infobox extraction
        if "{{infobox" in line:
            line=line.replace("_"," ")
            words=re.findall(pattern,line)
            for word in words:
                infobox.append(word)
            bodyFlag=1
            flag=1
        if flag==1:
            line=line.replace("_"," ")
            words=re.findall(pattern,line)
            for word in words:
                infobox.append(word)
            if "'''" in line:
                flag=0
                bodyFlag=1

        #Category extraction
        if '[[category:' in line:
            words=re.findall(pattern,line)
            for word in words:
                category.append(word)
            bodyFlag=1

        #Link extraction
        if line.startswith('* [http:'):
            tempLink.append(line)
            bodyFlag=1

        #Body extraction
        if bodyFlag==0:
            words=re.findall(pattern,line)
            for word in words:
                body.append(word)
            
    #Link tokenisation
    links=[]
    for link in tempLink:
        words=link.split(' ')
        for word in words:
            if "http" not in word:
                word=re.findall(pattern,word)
                if len(word)>0:
                    links.append(word[0])
          
    #Stopword removal->Stemmer->Indexer

    infobox=stopWordRemoval(infobox)
    infobox=stemWords(infobox)
    textIndexer(infobox,pageNumber,"infobox")
                  
    category=stopWordRemoval(category)
    category=stemWords(category)
    textIndexer(category,pageNumber,"category")
                  
    links=stopWordRemoval(links)
    links=stemWords(links)
    textIndexer(links,pageNumber,"links")
                  
    body=stopWordRemoval(body)
    body=stemWords(body)
    textIndexer(body,pageNumber,"body")
    
#Function to index titles
#Input is title and page id
def titleIndexer(words,ID):
    documentLength=len(words)
    if documentLength>0:
	#Calculate inverse document length
        factor=round((1/float(documentLength)),4)
        global titleCount
        global indexTitle
	#Index unique words into dictionary with appropriate weight
        for word in words:
                if indexTitle[word].has_key(ID):
                        indexTitle[word][ID]+=factor
                else: 
                        indexTitle[word][ID]=factor    
                        titleCount+=sys.getsizeof(ID)
                        titleCount+=sys.getsizeof(indexTitle[word][ID])
	#Save to file if limit is exceeded
        if titleCount>=limit:
                writeDown(indexTitle,'title')
                indexTitle=defaultdict(dict)
                titleCount=0  

#Function to index text
#Input is text, field and page id
def textIndexer(words,ID,field):
    documentLength=len(words)
    if documentLength>0:
	  #Calculate inverse document length
	  factor=round((1/float(documentLength)),4)
          global indexInfobox
          global indexCategory
          global indexLinks
          global indexBody
          global infoboxCount
          global categoryCount
          global linksCount
          global bodyCount
	  #Index unique words into dictionary with appropriate weight
	  #Index unique words into dictionary in appropriate fields
          if field=='infobox':
                for word in words:
                      if indexInfobox[word].has_key(ID):
                          indexInfobox[word][ID]+=factor
                      else:
                          indexInfobox[word][ID]=factor
                          infoboxCount+=sys.getsizeof(ID)
                          infoboxCount+=sys.getsizeof(indexInfobox[word][ID])
		#Save to file if limit is exceeded
                if infoboxCount>=limit: 
                      writeDown(indexInfobox,'infobox')
                      indexInfobox=defaultdict(dict)
                      infoboxCount=0
          if field=='links':
                for word in words:                                  
                      if indexLinks[word].has_key(ID):
                          indexLinks[word][ID]+=factor
                      else:
                          indexLinks[word][ID]=factor
                          linksCount+=sys.getsizeof(ID)
                          linksCount+=sys.getsizeof(indexLinks[word][ID])
		#Save to file if limit is exceeded
                if linksCount>=limit:
                    writeDown(indexLinks,'links')
                    indexLinks=defaultdict(dict)
                    linksCount=0
          if field=='category':
                for word in words:                                  
                            if indexCategory[word].has_key(ID):
                                indexCategory[word][ID]+=factor
                            else:
                                indexCategory[word][ID]=factor
                                categoryCount+=sys.getsizeof(ID)
                                categoryCount+=sys.getsizeof(indexCategory[word][ID])
		#Save to file if limit is exceeded
                if categoryCount>limit:
                      writeDown(indexCategory,'category')
                      indexCategory=defaultdict(dict)
                      categoryCount=0
          if field=='body':
                for word in words:              
                      if indexBody[word].has_key(ID):
                          indexBody[word][ID]+=factor
                      else:
                          indexBody[word][ID]=factor
                          bodyCount+=sys.getsizeof(ID)
                          bodyCount+=sys.getsizeof(indexBody[word][ID])
		#Save to file if limit is exceeded
                if bodyCount>limit:
                      writeDown(indexBody,'body')
                      indexBody=defaultdict(dict)
                      bodyCount=0 

#Function to save indices to file
#Input is index and field
def writeDown(index,field):     
      global TitlefileNumber
      global InfoboxfileNumber
      global LinksfileNumber
      global CategoryfileNumber
      global BodyfileNumber
      #Sort index on the basis of keys
      index1=OrderedDict(sorted(index.items()))
      dataBuffer=[]
      #Create buffer for writing to file
      for key in index1:
            dataBuffer.append(key.encode('utf-8'))
            for item in index1[key]:
                dataBuffer.append(" ")
                dataBuffer.append(str(item))
                dataBuffer.append(":")
                dataBuffer.append(str(index1[key][item]))            
            dataBuffer.append("\n")
      #Write title
      if field=='title':
            TitlefileNumber+=1
            name='outputFiles/title/'+'t'+str(TitlefileNumber)+'.txt.bz2'
            with bz2.BZ2File(name, 'wb', compresslevel=compression) as f:
                  f.write("".join(dataBuffer))
            f.close()
      #Write infobox
      if field=='infobox':
            InfoboxfileNumber+=1
            name='outputFiles/infobox/'+'i'+str(InfoboxfileNumber)+'.txt.bz2'
            with bz2.BZ2File(name, 'wb', compresslevel=compression) as f:
                f.write("".join(dataBuffer))
            f.close()
      #Write links
      if field=='links':
            LinksfileNumber+=1
            name='outputFiles/links/'+'l'+str(LinksfileNumber)+'.txt.bz2'
            with bz2.BZ2File(name, 'wb', compresslevel=compression) as f:
                f.write("".join(dataBuffer))
            f.close()
      #Write category
      if field=='category':
            CategoryfileNumber+=1
            name='outputFiles/category/'+'c'+str(CategoryfileNumber)+'.txt.bz2'
            with bz2.BZ2File(name, 'wb', compresslevel=compression) as f:
                f.write("".join(dataBuffer))
            f.close()
      #Write body
      if field=='body':
            BodyfileNumber+=1
            name='outputFiles/body/'+'b'+str(BodyfileNumber)+'.txt.bz2'
            with bz2.BZ2File(name, 'wb', compresslevel=compression) as f:
                f.write("".join(dataBuffer))
            f.close()
                
#Function to parse Wikipedia XML using SAX
class wikipediaHandler(xml.sax.ContentHandler):
    global pageNumber
    bufferObject=""
    flag=0
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
    #Function to handle starting element of page
    def startElement(self, name, attrs):
        global pageNumber
	if name=="page":
		pageNumber+=1	
    #Function to handle ending element of page	
    def endElement(self, name):
        global titlePageMapper1
        global pageNumber
	if name=="title":
	    wikipediaHandler.title=wikipediaHandler.bufferObject
	    wikipediaHandler.titleWords=tokenizeTitle(wikipediaHandler.title, str(pageNumber))
	if name=="text":
	    wikipediaHandler.text=wikipediaHandler.bufferObject
	    wikipediaHandler.textWords=tokenizeText(wikipediaHandler.text,str(pageNumber))
	if name=="page":
	    if pageNumber%7000==0:
		    for key in titlePageMapper1:
      				f.write(str(key))
      				f.write(" ")
      				f.write(titlePageMapper1[key].strip().encode('utf-8'))
      				f.write("\n")
		    titlePageMapper1=defaultdict(str)
	    wikipediaHandler.bufferObject=""
	    wikipediaHandler.flag=0

       	wikipediaHandler.bufferObject=""

    #Function to handle content from parser
    def characters(self, content):
       	wikipediaHandler.bufferObject+=content


#Main function    
if __name__=="__main__":
  source = open("enwiki.xml")
  start = timeit.default_timer()
  xml.sax.parse(source, wikipediaHandler())
  #Keep track of number of pages
  noOfDocs=open("noOfDocs.txt","w")
  noOfDocs.write(str(pageNumber))
  noOfDocs.close()
  stop = timeit.default_timer()
  #Write indices to file
  writeDown(indexTitle,'title')
  writeDown(indexInfobox,'infobox')
  writeDown(indexCategory,'category')
  writeDown(indexLinks,'links')
  writeDown(indexBody,'body')
  f.close()
  print stop-start
  

import sys
name1=sys.argv[1]
name2=sys.argv[2]
characterCount=[]
total=0
characterCount.append(total)
with open(name1,"r") as f:
    for line in f:
        total+=(len(line))
        characterCount.append(total)
f.close()

print "finished computation"
with open(name2,"w") as f:
    for i in characterCount:
        f.write(str(i)+"\n")
f.close()


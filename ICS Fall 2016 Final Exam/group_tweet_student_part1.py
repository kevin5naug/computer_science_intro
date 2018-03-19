df = {}

#implement here

#open, read the file, and then close it

#df[i] is a two-element tuple containing the two features.

f=open('tweet_features.txt','r')
lines=f.readlines()
f.close()
j=0
for line in lines:
    target=line.strip()
    features=target.split(' ')
    df[j]=(float(features[0]),float(features[1]))
    j+=1
for i in range(10):
    print(df.get(i,"None"))

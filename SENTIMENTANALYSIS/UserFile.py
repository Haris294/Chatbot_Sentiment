import pickle
import pymysql 
import nltk
from nltk.corpus import wordnet



def prepos(sentence):

    words = nltk.word_tokenize(sentence)
    
    new_words = []
    
    temp_word = ''
    for word in words:
        antonyms = []
        if word == 'not':
            temp_word = 'not_'
        elif temp_word == 'not_':
            for syn in wordnet.synsets(word):
                for s in syn.lemmas():
                    for a in s.antonyms():
                        antonyms.append(a.name())
            if len(antonyms) >= 1:
                word = antonyms[0]
            else:
                word = temp_word + word
            temp_word = ''
        if word != 'not':
            new_words.append(word)
    
    sentence = ' '.join(new_words)
    return [sentence]

 

# Using our classifier
with open('TFIDF.pickle','rb') as f:
    tfidf = pickle.load(f)
    
with open('LogistiClassifier.pickle','rb') as f:
    clf = pickle.load(f)
    
    
#sample = "Hello , not beautiful person"
con = pymysql.connect(host='localhost', user='root', password='root', db ='Chatbot')
cur = con.cursor()
insert = True 
query = "insert into sentiment (response,positive,negative) value (%s,%s,%s)"
while True:
    sample = input("ENter:")
    temp = sample
    query_select = "select response from sentiment"
    cur.execute(query_select)
    for row in cur:
        print(row[0])
        if(row[0].lower() == temp.lower()):
            insert = False
            break
    if sample=="X":
        break
    sample = prepos(sample)
    sample = tfidf.transform(sample).toarray()
    sentiment = clf.predict_proba(sample)
    
    #print(sentiment)
    
    if(sentiment[0][1]>sentiment[0][0]):
        positive = int((sentiment[0][1]+sentiment[0][2])*100)
        negative = int((sentiment[0][0])*100)
        print("Positive: ",positive,"%")
        print("Negative :",negative,"%")
        if(insert == True):
            cur.execute(query,(temp,positive,negative))
            con.commit()
    else:
        print("Negative :",int((sentiment[0][0]+sentiment[0][2])*100),"%")
        print("Positive: ",int((sentiment[0][1])*100),"%")
        if(insert == True):
            cur.execute(query,(temp,int((sentiment[0][1])*100),int((sentiment[0][0]+sentiment[0][2])*100)))
            con.commit()
con.close()    

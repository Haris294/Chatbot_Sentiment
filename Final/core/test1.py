import nltk
import numpy as np
import random
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet
import pickle
import pymysql 

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up","hey",)

GREETING_RESPONSES = ["hi", "hey", "*nods*", "hi there", "hello", "I am glad! You are talking to me"]


def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

def Insert(user_response,roboreply):
    con = pymysql.connect(host='localhost', user='root', password='root', db ='Chatbot')
    cur = con.cursor()
    query = "insert into quesans (question,answere) value (%s,%s)"
    cur.execute(query,(user_response,roboreply))
    con.commit()
    con.close()

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


def greeting(sentence):
 
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)  

def response(user_response,sent_tokens):
    robo_response=''
    sent_tokens.append(user_response)

    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]

    if(req_tfidf==0):
        robo_response=robo_response+"I am sorry! I am unable to understand you"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response

def Sentiment(sample):
    with open('TFIDF.pickle','rb') as f:
        tfidf = pickle.load(f)
        
    with open('LogistiClassifier.pickle','rb') as f:
        clf = pickle.load(f)
    con = pymysql.connect(host='localhost', user='root', password='root', db ='Chatbot')
    cur = con.cursor()
    insert = True 
    query = "insert into sentiment (response,positive,negative) value (%s,%s,%s)"
    temp = sample
    query_select = "select response from sentiment"
    sample = prepos(sample)
    sample = tfidf.transform(sample).toarray()
    sentiment = clf.predict_proba(sample)

    cur.execute(query_select)
    for row in cur:
        if(row[0].lower() == temp.lower()):
            insert = False
            break
        
    if(sentiment[0][1]>sentiment[0][0]):
        positive = int((sentiment[0][1]+sentiment[0][2])*100)
        negative = int((sentiment[0][0])*100)
        #print("Positive: ",positive,"%")
        #print("Negative :",negative,"%")
        if(insert == True):
            cur.execute(query,(temp,positive,negative))
            con.commit()
    else:
        #print("Negative :",int((sentiment[0][0]+sentiment[0][2])*100),"%")
        #print("Positive: ",int((sentiment[0][1])*100),"%")
        if(insert == True):
            cur.execute(query,(temp,int((sentiment[0][1])*100),int((sentiment[0][0]+sentiment[0][2])*100)))
            con.commit()
    con.close()    

lemmer = nltk.stem.WordNetLemmatizer()
sent_tokens = []
word_tokens = []
remove_punct_dict = {}

def chatbotMain(user_response):
    f=open('chatbot.txt','r',errors = 'ignore')

    raw=f.read()

    raw=raw.lower()# converts to lowercase

    remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

    sent_tokens = nltk.sent_tokenize(raw)# converts to list of sentences 
    word_tokens = nltk.word_tokenize(raw)# converts to list of words

    #WordNet is a semantically-oriented dictionary of English included in NLTK.

    n_token = LemTokens(word_tokens)
    #print(n_token[:5])

    n2_token = LemNormalize(raw)
    #print(n2_token[:2]) 

    flag=True
    print("ROBO: My name is Robo. I will answer your queries about Chatbots. If you want to exit, type Bye!")
    roboreply = ''
    user_response=user_response.lower()
    Sentiment(user_response)
    if(user_response=='thanks' or user_response=='thank you' ):
        flag=False            
        roboreply="You are welcome.."                
        print("ROBO:"+roboreply)
    else:
        if(greeting(user_response)!=None):
            roboreply=greeting(user_response)
            print("ROBO:"+roboreply)
        else:
            roboreply=response(user_response,sent_tokens)
            print("ROBO:"+roboreply)
            sent_tokens.remove(user_response)
    return roboreply


if __name__ == "__main__":
    while(True):
        chatbotMain("hey")
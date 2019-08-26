#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import re
import os
import sys
import nltk
import xml.etree.cElementTree as et
import pickle
import base64
import time


# In[ ]:


stemmer = nltk.stem.SnowballStemmer('english')
stop_words = {}
stop_file = open("stop_words.txt", "r")
words = stop_file.read()
words = words.split(",")
for word in words:
    word = word.strip()
    if word:
        stop_words[word[1:-1]] = 1
# print(stop_words)


# In[ ]:


pattern = re.compile("[^a-zA-Z]")


# In[ ]:


# arguments = sys.argv
# wikipedia_dump = arguments[0]
wikipedia_dump = "/home/vatsal/Documents/IIIT/Sem-3/IRE/wikipedia/wiki.xml"
content = et.iterparse(wikipedia_dump, events=("start", "end"))
content = iter(content)
# document_title = open("index/document_title.pickle", "wb")


# In[ ]:


title_inverted_index = {}
body_inverted_index = {}
category_inverted_index = {}
infobox_inverted_index = {}


# In[ ]:


document_no = 0
title_freq = {}
body_freq = {}
category_freq = {}
infobox_freq = {}
document_title = {}
document_word = {}
start = time.time()


# In[ ]:


for event,context in content:
    tag = re.sub(r"{.*}", "", context.tag)
    
    if event == "end":
        
        if tag == "title":
            
            title_text = context.text
            document_title[document_no]=title_text
            title_text = title_text.lower()
            try:
                words = re.split(pattern, title_text)
                for word in words:
#                     word=word.strip()
                    word = stemmer.stem(word)
                    if word and word not in stop_words:
                        if word not in title_freq:
                            title_freq[word] = 1
                        else:
                            title_freq[word] += 1
            except:
                pass
        
        elif tag == "text":
            
            try:
                body_text = context.text
                category_words = re.findall("\[\[Category:(.*?)\]\]", body_text);
                if category_words != "":
                    for category_word in category_words:
                        words = re.split(pattern, category_word)
                        for word in words:
#                             word=word.strip()
                            word = stemmer.stem(word.lower())
                            if  word and word not in stop_words:
                                if word not in category_freq:
                                    category_freq[word] = 1
                                else:
                                    category_freq[word] += 1
            except:
                pass
            
            try:

                info_words = re.findall("{{Infobox((.|\n)*?)}}", body_text)
                if info_words != "":
                    for info_word in info_words:
                        for i_word in info_word:
                            words = re.split(pattern, i_word)
                            for word in words:
#                                 word=word.strip()
                                word = stemmer.stem(word.lower())
                                if word and word not in stop_words:
                                    if word not in infobox_freq:
                                        infobox_freq[word] = 1
                                    else:
                                        infobox_freq[word] += 1
            except:
                pass
                                    
            try:
                words = re.split(pattern, body_text)

                for word in words:
                    word = stemmer.stem(word.lower())
                    if word and word not in stop_words:
                        if word not in body_freq:
                            body_freq[word] = 1
                        else:
                            body_freq[word] += 1
            except:
                pass
            
        elif tag == "page":
            d_no = str(document_no)
            for word in body_freq:
                if word not in body_inverted_index:
                    body_inverted_index[word]=[]
                body_inverted_index[word].append(d_no + ":" + str(body_freq[word]))
            
            body_freq = {}

            for word in title_freq:
                if word not in title_inverted_index:
                    title_inverted_index[word]=[]
                title_inverted_index[word].append(d_no + ":" + str(title_freq[word]))
            
            title_freq = {}

            for word in category_freq:
                if word not in category_inverted_index:
                    category_inverted_index[word]=[]
                category_inverted_index[word].append(d_no + ":" + str(category_freq[word]))
            
            category_freq = {}

            for word in infobox_freq:
                if word not in infobox_inverted_index:
                    infobox_inverted_index[word]=[]
                infobox_inverted_index[word].append(d_no + ":" + str(infobox_freq[word]))
            
            infobox_freq = {}
                
            document_no += 1


# In[ ]:


filename = "index/title.txt"
title_file = open(filename, "w+")
pointer = 0
for word in sorted(title_inverted_index) :
    posting_list = ",".join(title_inverted_index[word])
    posting_list = posting_list + "\n"
    document_word[word] = {}
    document_word[word]['t'] = pointer
    title_file.write(posting_list)
    pointer += len(posting_list)
title_file.close()


# In[ ]:


filename = "index/category.txt"
category_file = open(filename, "w+")
pointer = 0
for word in sorted(category_inverted_index) :
    posting_list = ",".join(category_inverted_index[word])
    posting_list = posting_list + "\n"
    if word not in document_word:
        document_word[word] = {}
    document_word[word]['c'] = pointer
    category_file.write(posting_list)
    pointer += len(posting_list)
category_file.close()


# In[ ]:


filename = "index/infobox.txt"
infobox_file = open(filename, "w+")
pointer = 0
for word in sorted(infobox_inverted_index) :
    posting_list = ",".join(infobox_inverted_index[word])
    posting_list = posting_list + "\n"
    if word not in document_word:
        document_word[word] = {}
    document_word[word]['i'] = pointer
    infobox_file.write(posting_list)
    pointer += len(posting_list)
infobox_file.close()


# In[ ]:


filename = "index/body_text.txt"
body_text_file = open(filename, "w+")
pointer = 0
for word in sorted(body_inverted_index) :
    posting_list = ",".join(body_inverted_index[word])
    posting_list = posting_list + "\n"
    if word not in document_word:
        document_word[word] = {}
    document_word[word]['b'] = pointer
    body_text_file.write(posting_list)
    pointer += len(posting_list)
body_text_file.close()


# In[ ]:


file = open("index/title_doc_no.pickle", "wb")
pickle.dump(document_title, file)
file.close()


# In[ ]:


file = open("index/word_position.pickle", "wb")
pickle.dump(document_word, file)
file.close()


# In[ ]:


end = time.time()
print("Time Taken :- ",(end-start))


#!/usr/bin/env python
# coding: utf-8

# # Detect Spam Emails

#  ## Importing Needed Libraries 

# In[1]:


import pandas as pd  #converts our data into dataframe
import numpy as np  # for numerical operations
import matplotlib.pyplot as plt #for data visualizations
import seaborn as sns  #for data visualizations
import string  #bc our data is categorical data


# ## Loading Dataset & EDA

# In[2]:


#loading spam dataset
spam_df = pd.read_csv("spam.csv", encoding='latin-1') #using latin-1 encoding to handle special characters


# In[3]:


spam_df  


# our data has 5572 rows and 5 columns . 3 useless columns that we need to drop.

# In[4]:


# dropping out the three noisy columns
spam_df=spam_df.drop(columns=['Unnamed: 2','Unnamed: 3','Unnamed: 4'])
#renaming our columns into meaningful names
spam_df=spam_df.rename(columns={'v1':'label' ,
                                'v2':'message'})
# encoding
spam_df['label']=spam_df['label'].map({'ham':0 , 'spam':1})


# In[5]:


spam_df  


# **so basically our spam dataset is too old and it doesn't have nowadays phishing emails, so i added some phishing msgs from another dataset.**

# In[6]:


# loading phishing dataset
phishing_df=pd.read_csv("phishing_email.csv" , encoding='latin-1')
phishing_df=phishing_df.rename(columns={'text_combined':'message'}) # rename to match
phishing_df.columns = ['message', 'label'] 
# sample down to only 10k rows
phishing_sample = phishing_df.groupby('label', group_keys=False).apply(lambda x: x.sample(5000, random_state=42)).reset_index(drop=True) 


# In[7]:


# merging 
combined_df = pd.concat([spam_df, phishing_sample], ignore_index=True)
combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)


# In[8]:


print(combined_df['label'].value_counts())
print("Total:", len(combined_df))


# ## Exploratory Data Analysis 

# In[9]:


combined_df.info()


# In[10]:


combined_df.isna().sum() 


# In[11]:


combined_df.nunique()


# In[12]:


combined_df.duplicated().sum()


# ### Data cleaning

# In[13]:


#dropping duplicates 
df= combined_df.drop_duplicates()


# In[14]:


df.duplicated().sum()


# now our data is clean 

# #### Text Preprocessing & Cleaning

# In[15]:


#converting txt into lowercase 
df['clean_msg'] = df['message'].apply(lambda s: s.lower())


# In[16]:


#removing punctuation
df['clean_msg'] = df['clean_msg'].apply(lambda s: s.translate(str.maketrans('', '',string.punctuation)))


# In[17]:


#importing Regular Expressions to remove numbers 
import re
def removeNums(msg):
    return re.sub(r'\d+', '', msg) #any digit 0-9 one or more
df['clean_msg'] = df['clean_msg'].apply(removeNums)    
df.head()


# In[18]:


#importing Natural Language Toolkit to remove stopwords
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords #corpus: a large collection of text

print(stopwords.words('english')[:20])


# In[19]:


stop_words = set(stopwords.words('english'))  # different name

def removeStopwords(msg):
    words = msg.split()
    return " ".join([w for w in words if w not in stop_words])  # use stop_words


# In[20]:


df['clean_msg'] = df['clean_msg'].apply(removeStopwords)


# In[21]:


combined_df['clean_msg'] = combined_df['message'].apply(removeStopwords)


# In[22]:


combined_df = combined_df.drop_duplicates().reset_index(drop=True)
combined_df['clean_msg'] = combined_df['message'].apply(lambda s: s.lower())
combined_df['clean_msg'] = combined_df['clean_msg'].apply(lambda s: s.translate(str.maketrans('', '', string.punctuation)))
combined_df['clean_msg'] = combined_df['clean_msg'].apply(removeNums)
combined_df['clean_msg'] = combined_df['clean_msg'].apply(removeStopwords)


# ### Data Visualization

# **Bar Chart**

# In[23]:


categories = ["ham","spam"]
values =combined_df['label'].value_counts()
plt.bar(categories, values, width=0.3,color=('green','red'))
plt.title('Bar Chart - Category Comparison' )
plt.xlabel('label')
plt.ylabel('value')
plt.show()


# class imbalance

# **Histogram:**

# *comparing message length between spam and ham*

# In[24]:


combined_df['msg_length']= combined_df['clean_msg'].apply(len)
ham_msgs =combined_df[combined_df['label']==0]
spam_msgs =combined_df[combined_df['label']==1]
ham = ham_msgs['msg_length']
spam = spam_msgs['msg_length']

plt.hist(ham, bins=20,edgecolor="black")
plt.title('Histogram - Data Distribution')
plt.xlabel('value')
plt.ylabel('frequent')

plt.hist(spam, bins=20,edgecolor="brown")
plt.xlabel('value')
plt.ylabel('frequent')
plt.show()


#  Spam messages tend to be longer 

# **Wordcloud:**

# *shows most frequent words in spam messages*

# In[25]:


from wordcloud import WordCloud


# In[26]:


spam_txt=" ".join(spam_msgs['clean_msg'])


# In[63]:


wordCloud = WordCloud(min_word_length=3, random_state=42).generate(spam_txt)
plt.imshow(wordCloud)
plt.axis('off')
plt.show()


# The most common words in spam messages are 'news'and 'free'...

# ## Modeling

# ### Naive Bayes Model

# In[88]:


#importing our model
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

X = combined_df['clean_msg']
y = combined_df['label']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

vectorizer = CountVectorizer()
X_train_counts = vectorizer.fit_transform(X_train)
X_test_counts = vectorizer.transform(X_test)

model = MultinomialNB()
model.fit(X_train_counts, y_train)

predictions = model.predict(X_test_counts)

print(f"Accuracy: {accuracy_score(y_test, predictions) * 100:.2f}%")
print(classification_report(y_test, predictions))


# **Naive Bayes CM:**

# In[89]:


from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test,predictions)


# In[90]:


sns.heatmap(cm, annot=True,fmt='d')
plt.show()


# ## using SMOTE to handle our imbalanced data

# **SMOTE + Naive Bayes**

# In[91]:


from imblearn.over_sampling import SMOTE

sm = SMOTE(random_state=42)
X_train_smote, y_train_smote = sm.fit_resample(X_train_counts, y_train)

print("Before SMOTE:",np.unique(y_train, return_counts=True))

print("After SMOTE:",np.unique(y_train_smote, return_counts=True))


# In[93]:


model_sm = MultinomialNB()
model_sm.fit(X_train_smote,y_train_smote)
predictions_sm = model_sm.predict(X_test_counts)
print(f"Accuracy: {accuracy_score(y_test, predictions_sm) * 100:.2f}%")
print(classification_report(y_test, predictions_sm))


# *okay , UNEXPECTED bad results (WAY too bad)*

# In[94]:


cm = confusion_matrix(y_test,predictions_sm)
sns.heatmap(cm, annot=True,fmt='d')
plt.show()


# **trying another model for better accuracy**

# ## RandomForestClassifier Model

# In[80]:


from sklearn.ensemble import RandomForestClassifier
model_rfc = RandomForestClassifier(random_state=42)
model_rfc.fit(X_train_counts,y_train)
predictions_rfc = model_rfc.predict(X_test_counts)
print(f"Accuracy: {accuracy_score(y_test, predictions_rfc) * 100:.2f}%")
print(classification_report(y_test, predictions_rfc))


# In[81]:


cm = confusion_matrix(y_test,predictions_rfc)
sns.heatmap(cm, annot=True,fmt='d')
plt.show()


# ### SMOTE + RandomForestClassifier Model

# In[85]:


model_sm2 = RandomForestClassifier(random_state=42)
model_sm2.fit(X_train_smote,y_train_smote)
predictions_sm2 = model_sm2.predict(X_test_counts)
print(f"Accuracy: {accuracy_score(y_test, predictions_sm2) * 100:.2f}%")
print(classification_report(y_test, predictions_sm2))


# *STILL bad accuracy*

# In[58]:


cm = confusion_matrix(y_test,predictions_sm2)
sns.heatmap(cm, annot=True,fmt='d')
plt.show()


# In[59]:


# trying to remove the noisy news msgs maybe they are the problem


# In[60]:


# noises = combined_df['clean_msg'].str.contains('cnn|cable|network news', case=False)
# combined_df[noises & (combined_df['label'] == 1)]['message'].head(10)


# In[61]:


# noise_keywords = ['daily top 10', 'cnn alerts', 'cnncom']

# noises = combined_df['clean_msg'].str.contains('|'.join(noise_keywords), case=False)
# print(combined_df[noises]['label'].value_counts())
# print("Rows to remove:", noises.sum())


# In[62]:


# combined_df = combined_df[~noises]
# combined_df.shape


# In[42]:


# *re-runing cells from Naive Bayes Model to SMOTE for RandomForestClassifier to check if there's any improvements*


# *so after all that cleaning and imbalance handling..STILL GETTING WORSE ACCURACY EVERYTIME HAHAHAHAHAHAHAHAHAHASHASDAWBDAWDBAHSBDAGDHSADHSVDHSAVDASVDVWWGDDBSDSHVHSVDHAVSA*

# **Comparing the 4 models to see which one to pick و خلاص**

# **Naive Bayes:**
# 
#  Accuracy: 92.60% 
#  
# **Naive Bayes + SMOTE:**
# 
# Accuracy: 91.41% 
# 
# **RandomForestClassifier:**
# 
# Accuracy: 95.05%     -highest accuracy
#            
# **RandomForestClassifier + SMOTE:**
# 
# Accuracy: 92.84% 

# ### Saving the model

# *saving the trained SMOTE model and Count Vectorizer for deployment in the streamlit app*

# In[95]:


import pickle

with open('model.pkl', 'wb') as f:
    pickle.dump(model_rfc, f)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)


# ## Test

# In[96]:


user_input=["free.money.win@scam.com"]
input_data_features = vectorizer.transform(user_input)
prediction = model.predict(input_data_features)
print ("spam" if  prediction == 1 else "not spam" )


import streamlit as st
import pickle
import string
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))


st.title("📧 Spam Emails Detector")


message = st.text_area("Enter your email:")

if st.button("Check"):
    
    
    msg = message.lower()
    msg = re.sub(r'\d+', '', msg)
    msg = msg.translate(str.maketrans('', '', string.punctuation))
    

    words = msg.split()
    clean = []
    for word in words:
        if word not in stopwords.words('english'):
            clean.append(word)
    msg = ' '.join(clean)
    
    msg_transformed = vectorizer.transform([msg])
    
    result = model.predict(msg_transformed)[0]
    
    if result == 1:
        st.error("🚨 SPAM!")
    else:
        st.success("✅ Not Spam!")
    
st.markdown("---")
st.markdown("Built with Streamlit")

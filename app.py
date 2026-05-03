import streamlit as st
import pickle
import string
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
# Load saved model and vectorizer
model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))


# App title
st.title("📧 AI Spam Emails Detector")

# Text box for user input
message = st.text_area("Enter your message here")

# When user clicks the button
if st.button("Check"):
    
    # Step 1: Clean the message (same pipeline as notebook)
    msg = message.lower()
    msg = re.sub(r'\d+', '', msg)
    msg = msg.translate(str.maketrans('', '', string.punctuation))
    
    # Remove stopwords
    words = msg.split()
    clean = []
    for word in words:
        if word not in stopwords.words('english'):
            clean.append(word)
    msg = ' '.join(clean)
    
    # Step 2: TF-IDF transform
    msg_transformed = vectorizer.transform([msg])
    
    # Step 3: Predict
    result = model.predict(msg_transformed)[0]
    
    # Show result
    if result == 1:
        st.error("🚨 SPAM!")
    else:
        st.success("✅ Not Spam!")
    
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Made by Habiba Hossam </p>", unsafe_allow_html=True)
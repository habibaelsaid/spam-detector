import streamlit as st
import pickle
import string
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

stop_words = set(stopwords.words('english'))

spam_words = ['free', 'winner', 'prize', 'offer', 'limited', 'earn', 'cash', 'click', 'buy', 'discount']
phishing_words = ['verify', 'confirm', 'account', 'suspended', 'login', 'password', 'credit', 'update', 'urgent', 'identity']

def clean_text(msg):
    msg = msg.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))
    msg = re.sub(r'\d+', '', msg)
    words = msg.split()
    return " ".join([w for w in words if w not in stop_words])

st.title("📧 Spam & Phishing Detector")
message = st.text_area("Enter your email or message:")

if st.button("Check"):
    cleaned = clean_text(message)
    transformed = vectorizer.transform([cleaned])
    result = model.predict(transformed)[0]

    if result == 1:
        words_in_msg = set(cleaned.split())
        found_phishing = [w for w in phishing_words if w in words_in_msg]
        found_spam = [w for w in spam_words if w in words_in_msg]

        is_phishing = len(message) > 100 and len(found_phishing) > 0

        if is_phishing:
            st.error("🚨 PHISHING ALERT!")
            st.warning("⚠️ Hackers are trying to fool you into giving your personal info. Don't fall for it!")
            if found_phishing:
                st.info(f"🔍 Suspicious words found: {', '.join(found_phishing)}")
        else:
            st.error("🚨 SPAM!")
            st.warning("⚠️ Spammers use these words to grab your attention. Don't be fooled!")
            if found_spam:
                st.info(f"🔍 Spammy words found: {', '.join(found_spam)}")
    else:
        st.success("✅ Not Spam!")

st.markdown("---")
st.markdown("Built with Streamlit by Habiba")
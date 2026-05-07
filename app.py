import streamlit as st
import pickle
import string
import re
import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords

st.set_page_config(page_title="AI Spam & Phishing Detector", page_icon="🛡️", layout="centered")

st.markdown("""
<style>
    body { background-color: #0d0d0d; }
    .stTextArea textarea {
        background-color: #1a1a2e;
        color: #00ff99;
        border: 1px solid #00ff99;
        font-family: monospace;
        font-size: 14px;
    }
    .stButton>button {
        background-color: #00ff99;
        color: #0d0d0d;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
        font-size: 16px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #00cc77;
    }
</style>
""", unsafe_allow_html=True)

model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
stop_words = set(stopwords.words('english'))

spam_words = ['free', 'winner', 'prize', 'offer', 'limited', 'earn', 'cash', 'click', 'buy', 'discount']
phishing_words = ['verify', 'confirm', 'account', 'suspended', 'login', 'password', 'credit', 'update', 'urgent', 'identity']

def clean_text(msg):
    msg = msg.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))
    msg = re.sub(r'\d+', '', msg)
    return " ".join([w for w in msg.split() if w not in stop_words])

st.markdown("# 🛡️ Spam & Phishing Detector")
st.markdown("#### *AI-powered protection against spam and phishing attacks*")
st.markdown("---")

message = st.text_area("📩 Paste your email or message here:", height=200, placeholder="Enter suspicious message...")

if st.button("🔍 Analyze Message"):
    if not message.strip():
        st.warning("Please enter a message first!")
    else:
        with st.spinner("🤖 Scanning message..."):
            cleaned = clean_text(message)
            transformed = vectorizer.transform([cleaned])
            result = model.predict(transformed)[0]

        if result == 1:
            words_in_msg = set(cleaned.split())
            found_phishing = [w for w in phishing_words if w in words_in_msg]
            found_spam = [w for w in spam_words if w in words_in_msg]
            is_phishing = len(message) > 100 and len(found_phishing) > 0

            if is_phishing:
                st.error("🚨 PHISHING DETECTED!")
                st.markdown("""
                > ⚠️ **Hackers are trying to steal your personal information.**  
                > Do NOT click any links or provide any credentials.
                """)
                if found_phishing:
                    st.info(f"🔍 **Suspicious words found:** `{'`, `'.join(found_phishing)}`")
            else:
                st.error("🚨 SPAM DETECTED!")
                st.markdown("""
                > ⚠️ **This message is trying to grab your attention with false promises.**  
                > Don't be fooled!
                """)
                if found_spam:
                    st.info(f"🔍 **Spammy words found:** `{'`, `'.join(found_spam)}`")
        else:
            st.success("✅ Looks Safe!")
            st.markdown("> No spam or phishing patterns detected.")

st.markdown("---")
st.markdown("<center><sub>🛡️ Built with Streamlit by Habiba</sub></center>", unsafe_allow_html=True)
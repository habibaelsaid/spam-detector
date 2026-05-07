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
    .stTextArea textarea {
        background-color: #1a1a2e;
        color: #7eb8f7;
        border: 1px solid #7eb8f7;
        font-family: monospace;
        font-size: 14px;
    }
    .stButton>button {
        background-color: #7eb8f7;
        color: #0d0d0d;
        font-weight: bold;
        border-radius: 8px;
        width: 100%;
        font-size: 16px;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #5a9fd4;
    }
</style>
""", unsafe_allow_html=True)

model = pickle.load(open('model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))
stop_words = set(stopwords.words('english'))

spam_words = ['free', 'winner', 'prize', 'offer', 'limited', 'earn', 'cash', 'click', 'buy', 'discount', 'congratulations', 'selected', 'reward', 'bonus', 'guaranteed', 'exclusive']
phishing_words = ['verify', 'confirm', 'account', 'suspended', 'login', 'password', 'credit', 'update', 'urgent', 'identity', 'secure', 'bank', 'unusual', 'activity', 'credentials', 'immediately', 'restore', 'protect', 'breach']

def clean_text(msg):
    msg = msg.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))
    msg = re.sub(r'\d+', '', msg)
    return " ".join([w for w in msg.split() if w not in stop_words])

def get_suspicious_phrases(text):
    text_lower = text.lower()
    suspicious_phrases = [
        "verify your account", "account suspended", "login to secure", 
        "secure your account", "update your password", "click here", 
        "claim your", "you won a free", "free prize", "urgent action", 
        "immediately", "account has been", "confirm your identity"
    ]
    return [phrase for phrase in suspicious_phrases if phrase in text_lower]

def is_spammy_context(text):
    text_lower = text.lower()
    
    # Only flag if dangerous phrases exist
    dangerous_patterns = [
        "update your password", "update your account", "confirm your identity",
        "verify your account", "click here to", "secure your account now",
        "you won a free", "free prize", "claim your free"
    ]
    return any(phrase in text_lower for phrase in dangerous_patterns)

st.markdown("# 🛡️ AI Spam & Phishing Detector")
st.markdown("---")

message = st.text_area("📩 Paste your email or message here:", height=200, placeholder="Enter suspicious message...")

if st.button("🔍 Analyze Message"):
    if not message.strip():
        st.warning("Please enter a message first!")
    else:
        cleaned = clean_text(message)
        transformed = vectorizer.transform([cleaned])
        result = model.predict(transformed)[0]

        words_in_msg = set(cleaned.split())
        found_phishing = [w for w in phishing_words if w in words_in_msg]
        found_spam = [w for w in spam_words if w in words_in_msg]

        suspicious_expressions = get_suspicious_phrases(message)
        has_dangerous_context = is_spammy_context(message)

        # Stronger & Smarter Conditions
        is_phishing = (len(message) > 60 and len(found_phishing) >= 2) or has_dangerous_context or len(suspicious_expressions) > 0
        is_spam = len(found_spam) >= 2 or result == 1

        if result == 1 or is_phishing or len(found_spam) > 0:
            if is_phishing or len(suspicious_expressions) > 0:
                st.error("🚨 PHISHING DETECTED!")
                st.markdown("""
                > ⚠️ **Hackers are trying to steal your personal information.**  
                > Do NOT click any links or provide any credentials.
                """)
                if suspicious_expressions:
                    st.info(f"🔍 **Suspicious expressions found:** `{'`, `'.join(suspicious_expressions)}`")
                elif found_phishing:
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
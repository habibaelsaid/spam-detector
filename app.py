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

spam_words = ['free', 'winner', 'prize', 'offer', 'limited', 'earn', 'cash', 'click', 'buy', 'discount', 
              'congratulations', 'selected', 'reward', 'bonus', 'guaranteed', 'exclusive']

phishing_words = ['verify', 'confirm', 'account', 'suspended', 'login', 'password', 'credit', 'update', 
                  'urgent', 'identity', 'secure', 'bank', 'unusual', 'activity', 'credentials', 
                  'immediately', 'restore', 'protect', 'breach']


def clean_text(msg):
    msg = msg.lower()
    msg = msg.translate(str.maketrans('', '', string.punctuation))
    msg = re.sub(r'\d+', '', msg)
    return " ".join([w for w in msg.split() if w not in stop_words])

def highlight_words(text, words_list, is_phishing=False):
    if not words_list:
        return text
    color = "#ff4444" if is_phishing else "#ffaa00"
    for word in sorted(words_list, key=len, reverse=True):
        replacement = f'<span style="background-color: {color}; color: white; font-weight: bold; padding: 2px 6px; border-radius: 4px;">{word}</span>'
        text = re.sub(re.escape(word), replacement, text, flags=re.IGNORECASE)
    return text

def extract_urls(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.findall(text)

def is_suspicious_url(url):
    suspicious_domains = ['.xyz', '.top', '.ml', '.tk', '.ga', 'bit.ly', 'tinyurl', 'short.ly']
    url_lower = url.lower()
    return any(domain in url_lower for domain in suspicious_domains)

def has_suspicious_context(word, text):
    text_lower = text.lower()
    
    suspicious_patterns = {
        'free': ['win a free','won a free' ,'free prize', 'get free', 'claim your free'],
        'update': ['update your password now', 'update your information immediately'],
        'click': ['click here', 'click the link', 'click below', 'click now'],
        'account': ['account has been suspended', 'account will be locked', 'your account is at risk'],
        'password': ['change your password now', 'reset your password immediately'],
        'verify': ['verify your identity immediately', 'verify now'],
        'secure': ['secure your account immediately'],
    }
    
    if word in suspicious_patterns:
        for phrase in suspicious_patterns[word]:
            if phrase in text_lower:
                return True
    return False

st.markdown("# 🛡️ AI Spam & Phishing Detector")
st.markdown("---")

message = st.text_area("📩 Paste your email or message here:", height=250, 
                      placeholder="Paste email here...")

if st.button("🔍 Analyze Message", type="primary"):
    if not message.strip():
        st.warning("Please enter a message first!")
    else:
        cleaned = clean_text(message)
        transformed = vectorizer.transform([cleaned])
        model_result = model.predict(transformed)[0]

        words_in_msg = set(cleaned.split())
        found_phishing = [w for w in phishing_words if w in words_in_msg]
        found_spam = [w for w in spam_words if w in words_in_msg]

    
        strong_phishing = [w for w in found_phishing if has_suspicious_context(w, message)]
        strong_spam = [w for w in found_spam if has_suspicious_context(w, message)]

        urls = extract_urls(message)
        suspicious_urls = [url for url in urls if is_suspicious_url(url)]

    
        is_phishing = (
            len(strong_phishing) > 0 or 
            len(suspicious_urls) > 0 or 
            (len(found_phishing) >= 3 and len(message) > 100)
        )

        is_spam = (len(strong_spam) > 1) or (model_result == 1 and len(found_spam) > 0)

    
        if is_phishing:
            st.error("🚨 PHISHING DETECTED!")
            st.markdown("> ⚠️ **Hackers are trying to steal your personal information.**  \n> Do NOT click any links or share credentials.")
            
            if urls:
                st.warning(f"🔗 **Found {len(urls)} link(s)** — Always be careful with links!")
            if suspicious_urls:
                st.error("🚩 Suspicious shortener or risky domain detected!")
            
            highlighted = highlight_words(message, strong_phishing or found_phishing, True)
            st.markdown("**Phishing indicators:**", unsafe_allow_html=True)
            st.markdown(highlighted, unsafe_allow_html=True)

        elif is_spam:
            st.error("🚨 SPAM DETECTED!")
            st.markdown("> ⚠️ **Spammers are trying to grap your attention with false promsises.**  \n> Do NOT be fooled.")
            highlighted = highlight_words(message, strong_spam or found_spam, False)
            st.markdown("**Spammy indicators:**", unsafe_allow_html=True)
            st.markdown(highlighted, unsafe_allow_html=True)

        else:
            st.success("✅ Looks Safe!")
            st.markdown("> No spam or phishing patterns detected.")

       
        with st.expander("🔍 See Analysis Details"):
            st.write("**Model says:**", "Spam/Phishing" if model_result == 1 else "Safe")
            st.write("**Found Phishing Words:**", found_phishing)
            st.write("**Strong Phishing Words:**", strong_phishing)
            st.write("**URLs Found:**", urls)
            if suspicious_urls:
                st.write("**Suspicious URLs:**", suspicious_urls)

st.markdown("---")
st.markdown("<center><sub>🛡️ Built with Streamlit by Habiba Hossam</sub></center>", unsafe_allow_html=True)
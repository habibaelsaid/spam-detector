import streamlit as st
import joblib
import string
import re
import nltk
nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords

st.set_page_config(page_title="AI Spam & Phishing Detector", page_icon="🛡️", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
        background-color: #0a0a0f;
        color: #e0e0e0;
    }
    .stTextArea textarea {
        background-color: #111118;
        color: #c9d1d9;
        border: 1px solid #2a2a3d;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        border-radius: 10px;
    }
    .stTextArea textarea:focus {
        border-color: #7eb8f7;
        box-shadow: 0 0 0 2px rgba(126,184,247,0.15);
    }
    .stButton>button {
        background: linear-gradient(135deg, #1a6bbd, #0e4a8a);
        color: #ffffff;
        font-weight: 700;
        font-family: 'Syne', sans-serif;
        border-radius: 10px;
        width: 100%;
        font-size: 16px;
        padding: 12px;
        border: none;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2281e0, #1a6bbd);
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(126,184,247,0.25);
    }
    .result-box {
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
        font-family: 'Syne', sans-serif;
    }
    .result-safe {
        background: rgba(46, 160, 67, 0.12);
        border: 1px solid rgba(46, 160, 67, 0.4);
    }
    .result-phishing {
        background: rgba(248, 81, 73, 0.12);
        border: 1px solid rgba(248, 81, 73, 0.4);
    }
    .result-spam {
        background: rgba(210, 153, 34, 0.12);
        border: 1px solid rgba(210, 153, 34, 0.4);
    }
    .highlight-box {
        background: #111118;
        border: 1px solid #2a2a3d;
        border-radius: 10px;
        padding: 16px 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        line-height: 1.8;
        margin-top: 12px;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .hl-phishing {
        background: rgba(248, 81, 73, 0.3);
        color: #ff9999;
        border-radius: 3px;
        padding: 1px 4px;
        font-weight: 700;
    }
    .hl-spam {
        background: rgba(210, 153, 34, 0.3);
        color: #ffd700;
        border-radius: 3px;
        padding: 1px 4px;
        font-weight: 700;
    }
    .legend {
        display: flex;
        gap: 16px;
        margin-top: 10px;
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .dot-phishing {
        width: 10px; height: 10px;
        background: rgba(248, 81, 73, 0.7);
        border-radius: 2px;
        display: inline-block;
    }
    .dot-spam {
        width: 10px; height: 10px;
        background: rgba(210, 153, 34, 0.7);
        border-radius: 2px;
        display: inline-block;
    }
    .stat-row {
        display: flex;
        gap: 12px;
        margin-top: 12px;
        flex-wrap: wrap;
    }
    .stat-chip {
        background: #1a1a2e;
        border: 1px solid #2a2a3d;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
        color: #7eb8f7;
    }
    h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }
    .footer { text-align: center; color: #444; font-size: 12px; margin-top: 40px; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    model = joblib.load('spam_detector_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    return model, vectorizer

model, vectorizer = load_model()
stop_words = set(stopwords.words('english'))

spam_words = [
    'free', 'winner', 'prize', 'offer', 'limited', 'earn', 'cash',
    'click', 'buy', 'discount', 'congratulations', 'selected', 'reward',
    'bonus', 'guaranteed', 'exclusive', 'deal', 'promo', 'cheap', 'order'
]
phishing_words = [
    'verify', 'confirm', 'account', 'suspended', 'login', 'password',
    'credit', 'update', 'urgent', 'identity', 'secure', 'bank', 'unusual',
    'activity', 'credentials', 'immediately', 'restore', 'protect',
    'breach', 'unauthorized', 'expire', 'access', 'security'
]
suspicious_phrases = [
    "verify your account", "account suspended", "login to secure",
    "secure your account", "update your password", "click here",
    "claim your", "you won a free", "free prize", "urgent action",
    "account has been", "confirm your identity", "unusual activity",
    "your password has", "your account will"
]


def clean_text(msg):
    msg = msg.lower()
    msg = msg.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
    msg = re.sub(r'\d+', ' ', msg)
    msg = re.sub(r'escape\w*', ' ', msg)
    msg = re.sub(r'\s+', ' ', msg).strip()
    msg = " ".join([w for w in msg.split() if w not in stop_words and len(w) >= 3])
    return msg

def highlight_text(original_msg, found_phishing, found_spam, found_phrases):
    highlighted = original_msg

    for phrase in sorted(found_phrases, key=len, reverse=True):
        pattern = re.compile(re.escape(phrase), re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f'<span class="hl-phishing">{m.group()}</span>', highlighted
        )

    
    for word in found_phishing:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f'<span class="hl-phishing">{m.group()}</span>', highlighted
        )

    
    for word in found_spam:
        pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
        highlighted = pattern.sub(
            lambda m: f'<span class="hl-spam">{m.group()}</span>', highlighted
        )

    return highlighted


st.markdown("# 🛡️ AI Spam & Phishing Detector")
st.markdown("Paste any email or message below.")
st.markdown("---")

message = st.text_area("📩 Message:", height=200, placeholder="Paste your email or message here...")

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
        found_phrases = [p for p in suspicious_phrases if p in message.lower()]

        has_dangerous_context = len(found_phrases) > 0 or len(found_phishing) >= 2

        
        if result == 1:
            is_phishing = has_dangerous_context

            if is_phishing:
                st.markdown("""
                <div class="result-box result-phishing">
                    <h3 style="color:#ff6b6b; margin:0">🚨 PHISHING DETECTED</h3>
                    <p style="margin:8px 0 0; color:#ffaaaa">Hackers are trying to steal your personal information.<br>
                    Do <strong>NOT</strong> click any links or provide any credentials.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-box result-spam">
                    <h3 style="color:#ffd700; margin:0">⚠️ SPAM DETECTED</h3>
                    <p style="margin:8px 0 0; color:#ffe680">This message is trying to grab your attention with false promises.<br>
                    Don't be fooled!</p>
                </div>
                """, unsafe_allow_html=True)

            
            chips = ""
            if found_phrases:
                chips += f'<span class="stat-chip">🔴 {len(found_phrases)} suspicious phrase(s)</span>'
            if found_phishing:
                chips += f'<span class="stat-chip">🔴 {len(found_phishing)} phishing word(s)</span>'
            if found_spam:
                chips += f'<span class="stat-chip">🟡 {len(found_spam)} spam word(s)</span>'
            if chips:
                st.markdown(f'<div class="stat-row">{chips}</div>', unsafe_allow_html=True)

            
            all_phishing = found_phishing
            all_spam = found_spam
            if all_phishing or all_spam or found_phrases:
                st.markdown("#### 🔍 Highlighted Message")
                highlighted = highlight_text(message, all_phishing, all_spam, found_phrases)
                st.markdown(f'<div class="highlight-box">{highlighted}</div>', unsafe_allow_html=True)
                st.markdown("""
                <div class="legend">
                    <div class="legend-item"><span class="dot-phishing"></span> Phishing indicator</div>
                    <div class="legend-item"><span class="dot-spam"></span> Spam indicator</div>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div class="result-box result-safe">
                <h3 style="color:#56d364; margin:0">✅ Looks Safe</h3>
                <p style="margin:8px 0 0; color:#aaffaa">No spam or phishing patterns detected in this message.</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="footer">🛡️ Built with Streamlit | By Habiba Hossam· </div>', unsafe_allow_html=True)
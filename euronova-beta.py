import streamlit as st
import requests
import re
import json

# Hårdkodad CassidyAI API-nyckel och Assistant ID
API_KEY = "mitPxZU_ier-oAVubaLv1SscDTpJNASPvwdr7rrznBs"
ASSISTANT_ID = "cm4toc4e607xtofca5l0v1g3a"

# API-endpoints
CREATE_THREAD_URL = "https://app.cassidyai.com/api/assistants/thread/create"
SEND_MESSAGE_URL = "https://app.cassidyai.com/api/assistants/message/create"

# Lösenord för autentisering
PASSWORD = "stakeholder"

# Initialisera session state för autentisering, tråd ID, meddelandehistorik och referenser
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None

if 'messages' not in st.session_state:
    # Lägg till det första meddelandet från assistenten
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome! I'm here to guide you through key focus areas. Which topic would you like to start with: IP, Brain Health, Critical Medicines Act, EU Life Sciences Strategy, or Advanced Therapy Medicinal Products?"}
    ]

if 'all_references' not in st.session_state:
    st.session_state.all_references = []  # Lista av dicts med 'n', 'name', 'description'

def local_css():
    st.markdown(
        """
        <style>
        /* Importera Roboto-fonten */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@100&display=swap');

        /* Färgpalett */
        .first-color { 
            background: #ffffff; 
        }
        .second-color { 
            background: #e8e8e8;  /* Ny bakgrundsfärg för user-bubble */
        }
        .third-color { 
            background: #f0f2f6;  /* Ny bakgrundsfärg för assistant-bubble */
        }
        .fourth-color { 
            background: #254aa5;  /* Ersätter #7c73e6 */
        }

        /* Allmän styling */
        body, .stApp, [class*="css"] {
            background-color: #ffffff !important;
            font-family: 'Roboto', sans-serif;
            color: #262626;
        }

        /* Avatarer */
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
        }
        .user-avatar {
            /* Använder fjärde färgen, nu #254aa5 */
            background-color: #254aa5; 
            width: 40px;
            height: 40px;
            border-radius: 50%;
        }
        .assistant-avatar {
            content: url("https://i.imgur.com/8Km9tLL.png");
            width: 40px;
            height: 40px;
            border-radius: 50%;
        }

        /* Chatbubblor */
        .chat-container {
            display: flex;
            flex-direction: column;
            max-height: 70vh;
            overflow-y: auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .message-row {
            display: flex;
            align-items: flex-end;
            gap: 10px;
            margin-bottom: 20px;
        }
        .user-bubble {
            align-self: flex-end;
            /* Ny bakgrundsfärg = .second-color => #e8e8e8 */
            background-color: #e8e8e8; 
            color: #262626;
            padding: 10px 15px;
            border-radius: 20px;
            max-width: 100%;
            word-wrap: break-word;
        }
        .assistant-bubble {
            align-self: flex-start;
            /* Ny bakgrundsfärg = .third-color => #f0f2f6 */
            background-color: #f0f2f6; 
            color: #262626;
            padding: 10px 15px;
            border-radius: 20px;
            max-width: 100%;
            word-wrap: break-word;
        }

        /* Referenslistan */
        .references {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        .references h3 {
            margin-bottom: 10px;
            color: #262626;
        }
        .references ul {
            list-style-type: decimal;
            padding-left: 20px;
        }
        .references li {
            margin-bottom: 5px;
            color: #262626;
        }

        /* Typing Indicator */
        .typing-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
            margin-top: 10px;
        }
        .typing-indicator .dot {
            width: 8px;
            height: 8px;
            /* Samma färg som .fourth-color => #254aa5 */
            background-color: #254aa5;
            border-radius: 50%;
            animation: typing 1.4s infinite both;
        }
        .typing-indicator .dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        .typing-indicator .dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        @keyframes typing {
            0% {
                transform: translateY(0);
                opacity: 0.7;
            }
            50% {
                transform: translateY(-8px);
                opacity: 1;
            }
            100% {
                transform: translateY(0);
                opacity: 0.7;
            }
        }

        /* Scrollbar styling */
        .chat-container::-webkit-scrollbar {
            width: 8px;
        }
        .chat-container::-webkit-scrollbar-track {
            background: #f1f1f1; 
        }
        .chat-container::-webkit-scrollbar-thumb {
            background: #888; 
            border-radius: 4px;
        }
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #555; 
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Funktion för autentisering
def authenticate():
    st.title("Secure login")
    with st.form("login_form"):
        password_input = st.text_input("Password:", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if password_input == PASSWORD:
                st.session_state.authenticated = True
            else:
                st.error("Wrong password. Try again.")

def create_thread():
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "assistant_id": ASSISTANT_ID
    }
    try:
        response = requests.post(CREATE_THREAD_URL, headers=headers, json=data)
        response.raise_for_status()
        json_response = response.json()
        thread_id = json_response.get("thread_id")
        if not thread_id:
            st.error("Tråd ID saknas i API-svaret.")
        return thread_id
    except requests.exceptions.RequestException as e:
        st.error(f"Fel vid skapande av tråd: {e}")
        return None

def send_message(thread_id, message):
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "thread_id": thread_id,
        "message": message
    }
    try:
        response = requests.post(SEND_MESSAGE_URL, headers=headers, json=data)
        response.raise_for_status()
        json_response = response.json()

        assistant_response = json_response.get("content") or json_response.get("content_with_references")
        references = json_response.get("references", [])

        if not assistant_response:
            st.error("Assistentens svar saknas i API-svaret.")
            return "Ursäkta, något gick fel.", []

        updated_content, new_references = process_references(assistant_response, references)
        return updated_content, new_references
    except requests.exceptions.RequestException as e:
        st.error(f"Fel vid skickande av meddelande: {e}")
        return "Ursäkta, något gick fel.", []

def process_references(content_with_refs, references):
    markers = re.findall(r'\[\[(\d+)\]\]', content_with_refs)
    updated_content = content_with_refs

    for marker in markers:
        index = int(marker)
        if index < len(references):
            ref = references[index]
            ref_key = ref['url']
            existing_ref = next((item for item in st.session_state.all_references if item['url'] == ref_key), None)
            if existing_ref:
                global_n = existing_ref['n']
            else:
                global_n = len(st.session_state.all_references) + 1
                st.session_state.all_references.append({
                    "n": global_n,
                    "name": ref['name'],
                    "description": extract_description(ref['name'], ref['url'])
                })
            updated_content = updated_content.replace(f'[[{marker}]]', f'[[{global_n}]]')

    return updated_content, []

def extract_description(name, url):
    return f"{name}."

def format_chat_history(messages):
    history = ""
    for msg in messages:
        if msg["role"] == "user":
            history += f"Human: {msg['content']}\n"
        else:
            history += f"AI: {msg['content']}\n"
    return history.strip()

def main_app():
    local_css()

    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <h3 style="margin:0; color: #262626;">Euronova EU-level mapping (Experimental by Gullers)</h3>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.thread_id is None:
        with st.spinner("Skapar chatttråd..."):
            thread_id = create_thread()
            if thread_id:
                st.session_state.thread_id = thread_id
            else:
                st.stop()

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                    <div class="message-row">
                        <div class="user-avatar"></div>
                        <div class="user-bubble">{msg["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="message-row">
                        <img src="https://i.imgur.com/8Km9tLL.png" alt="Assistant Avatar" class="avatar assistant-avatar">
                        <div class="assistant-bubble">{msg["content"]}</div>
                    </div>
                    """, unsafe_allow_html=True)

    typing_placeholder = st.empty()

    user_input = st.chat_input("Ask a question...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with chat_container:
            st.markdown(f"""
                <div class="message-row">
                    <div class="user-avatar"></div>
                    <div class="user-bubble">{user_input}</div>
                </div>
                """, unsafe_allow_html=True)

        with typing_placeholder.container():
            st.markdown("""
                <div class="typing-indicator">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                </div>
                """, unsafe_allow_html=True)

        assistant_reply, _ = send_message(st.session_state.thread_id, user_input)

        typing_placeholder.empty()

        st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
        with chat_container:
            st.markdown(f"""
                <div class="message-row">
                    <img src="https://i.imgur.com/8Km9tLL.png" alt="Assistant Avatar" class="avatar assistant-avatar">
                    <div class="assistant-bubble">{assistant_reply}</div>
                </div>
                """, unsafe_allow_html=True)

    if st.session_state.all_references:
        st.markdown("""
            <div class="references">
                <h3>Referenser:</h3>
                <ul>
        """, unsafe_allow_html=True)
        for ref in st.session_state.all_references:
            st.markdown(f"<li><strong>{ref['n']}. {ref['name']}</strong>. {ref['description']}</li>", unsafe_allow_html=True)
        st.markdown("</ul></div>", unsafe_allow_html=True)

if not st.session_state.authenticated:
    authenticate()
else:
    main_app()

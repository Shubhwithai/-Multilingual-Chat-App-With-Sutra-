import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.callbacks.base import BaseCallbackHandler

# Page configuration
st.set_page_config(
    page_title="Sutra Multilingual Chat",
    page_icon="🌐",
    layout="wide"
)

# Define supported languages
languages = [
    "English", "Hindi", "Gujarati", "Bengali", "Tamil", 
    "Telugu", "Kannada", "Malayalam", "Punjabi", "Marathi", 
    "Urdu", "Assamese", "Odia", "Sanskrit", "Korean", 
    "Japanese", "Arabic", "French", "German", "Spanish", 
    "Portuguese", "Russian", "Chinese", "Vietnamese", "Thai", 
    "Indonesian", "Turkish", "Polish", "Ukrainian", "Dutch", 
    "Italian", "Greek", "Hebrew", "Persian", "Swedish", 
    "Norwegian", "Danish", "Finnish", "Czech", "Hungarian", 
    "Romanian", "Bulgarian", "Croatian", "Serbian", "Slovak", 
    "Slovenian", "Estonian", "Latvian", "Lithuanian", "Malay", 
    "Tagalog", "Swahili"
]

# Define welcome messages for each language
welcome_messages = {
    "English": "I'm your Sutra, ask me any question...",
    "Hindi": "मैं आपकी सूत्र हूं, मुझसे कोई भी प्रश्न पूछें...",
    "Gujarati": "હું તમારી સૂત્ર છું, મને કોઈપણ પ્રશ્ન પૂછો...",
    "Bengali": "আমি আপনার সূত্র, আমাকে যেকোনো প্রশ্ন জিজ্ঞাসা করুন...",
    "Tamil": "நான் உங்கள் சூத்திரம், என்னிடம் எந்த கேள்வியும் கேளுங்கள்...",
    "Telugu": "నేను మీ సూత్రం, నన్ను ఏదైనా ప్రశ్న అడగండి...",
    "Kannada": "ನಾನು ನಿಮ್ಮ ಸೂತ್ರ, ನನ್ನನ್ನು ಯಾವುದೇ ಪ್ರಶ್ನೆ ಕೇಳಿ...",
    "Malayalam": "ഞാൻ നിങ്ങളുടെ സൂത്രം, എന്നോട് ഏത് ചോദ്യവും ചോദിക്കൂ...",
    "Punjabi": "ਮੈਂ ਤੁਹਾਡੀ ਸੂਤਰ ਹਾਂ, ਮੈਨੂੰ ਕੋਈ ਵੀ ਸਵਾਲ ਪੁੱਛੋ...",
    "Marathi": "मी तुमची सूत्र आहे, मला कोणताही प्रश्न विचारा...",
    "Urdu": "میں آپ کی سترا ہوں، مجھ سے کوئی بھی سوال پوچھیں...",
    "Assamese": "মই আপোনাৰ সূত্ৰ, মোক যিকোনো প্ৰশ্ন সুধক...",
    "Odia": "ମୁଁ ଆପଣଙ୍କର ସୂତ୍ର, ମୋତେ ଯେକୌଣସି ପ୍ରଶ୍ନ ପଚାରନ୍ତୁ...",
    "Sanskrit": "अहं तव सूत्रं, मां किमपि प्रश्नं पृच्छतु...",
    "Korean": "저는 당신의 수트라입니다, 어떤 질문이든 물어보세요...",
    "Japanese": "私はあなたのスートラです、どんな質問でも聞いてください...",
    "Arabic": "أنا سترا الخاص بك، اسألني أي سؤال...",
    "French": "Je suis votre Sutra, posez-moi n'importe quelle question...",
    "German": "Ich bin dein Sutra, stelle mir jede Frage...",
    "Spanish": "Soy tu Sutra, hazme cualquier pregunta...",
    "Portuguese": "Eu sou seu Sutra, faça-me qualquer pergunta...",
    "Russian": "Я ваш Сутра, задайте мне любой вопрос...",
    "Chinese": "我是你的经，问我任何问题...",
    "Vietnamese": "Tôi là Sutra của bạn, hãy hỏi tôi bất kỳ câu hỏi nào...",
    "Thai": "ฉันคือสูตรของคุณ ถามฉันได้ทุกคำถาม...",
    "Indonesian": "Saya adalah Sutra Anda, tanyakan apa saja...",
    "Turkish": "Ben senin Sutra'nım, bana herhangi bir soru sor...",
    "Polish": "Jestem twoim Sutrą, zadaj mi dowolne pytanie...",
    "Ukrainian": "Я ваша Сутра, задайте мені будь-яке питання...",
    "Dutch": "Ik ben je Sutra, stel me elke vraag...",
    "Italian": "Sono il tuo Sutra, fammi qualsiasi domanda...",
    "Greek": "Είμαι η Σούτρα σου, κάνε μου οποιαδήποτε ερώτηση...",
    "Hebrew": "אני הסוטרה שלך, שאל אותי כל שאלה...",
    "Persian": "من سترای شما هستم، هر سوالی بپرسید...",
    "Swedish": "Jag är din Sutra, ställ mig vilken fråga som helst...",
    "Norwegian": "Jeg er din Sutra, spør meg hvilken som helst spørsmål...",
    "Danish": "Jeg er din Sutra, spørg mig om hvad som helst...",
    "Finnish": "Olen Sutrasi, kysy minulta mitä tahansa...",
    "Czech": "Jsem tvůj Sutra, zeptej se mě na cokoliv...",
    "Hungarian": "Én vagyok a Sutrád, kérdezz bármit...",
    "Romanian": "Sunt Sutra ta, întreabă-mă orice...",
    "Bulgarian": "Аз съм твоята Сутра, питай ме каквото искаш...",
    "Croatian": "Ja sam tvoj Sutra, pitaj me bilo što...",
    "Serbian": "Ја сам твоја Сутра, питај ме шта год желиш...",
    "Slovak": "Som tvoja Sutra, opýtaj sa ma čokoľvek...",
    "Slovenian": "Jaz sem tvoja Sutra, vprašaj me karkoli...",
    "Estonian": "Ma olen sinu Sutra, küsi minult mida iganes...",
    "Latvian": "Es esmu tava Sutra, jautā man jebko...",
    "Lithuanian": "Aš esu tavo Sutra, klausk manęs ko nori...",
    "Malay": "Saya adalah Sutra anda, tanya saya apa-apa...",
    "Tagalog": "Ako ang iyong Sutra, tanungin mo ako ng kahit ano...",
    "Swahili": "Mimi ni Sutra yako, niulize swali lolote..."
}

# Streaming callback handler
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
        self.run_id_ignore_token = None
    
    def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        self.container.markdown(self.text)

# Initialize the ChatOpenAI model - base instance for caching
@st.cache_resource
def get_base_chat_model(api_key):
    return ChatOpenAI(
        api_key=api_key,
        base_url="https://api.two.ai/v2",
        model="sutra-v2",
        temperature=0.7,
    )

# Create a streaming version of the model with callback handler
def get_streaming_chat_model(api_key, callback_handler=None):
    # Create a new instance with streaming enabled
    return ChatOpenAI(
        api_key=api_key,
        base_url="https://api.two.ai/v2",
        model="sutra-v2",
        temperature=0.7,
        streaming=True,
        callbacks=[callback_handler] if callback_handler else None
    )

# Sidebar for language selection and API key
st.sidebar.image("https://framerusercontent.com/images/3Ca34Pogzn9I3a7uTsNSlfs9Bdk.png", use_container_width=True)
with st.sidebar:
    st.title("🌐 Sutra Chat :")
    
    # API Key section
    st.markdown("### API Key")
    st.markdown("Get your free API key from [Sutra API](https://www.two.ai/sutra/api)")
    api_key = st.text_input("Enter your Sutra API Key:", type="password")
    
    # Language selector
    selected_language = st.selectbox("Select language:", languages)
    
    st.divider()
    st.markdown(f"Currently chatting in: **{selected_language}**")
    
    # About section
    st.markdown("### About Sutra LLM")
    st.markdown("Sutra is a multilingual model supporting 50+ languages with high-quality responses.")

st.markdown(
    f'<h1><img src="https://framerusercontent.com/images/9vH8BcjXKRcC5OrSfkohhSyDgX0.png" width="60"/> Sutra Multilingual Chatbot 🤖</h1>',
    unsafe_allow_html=True
    )

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []
if "welcome_shown" not in st.session_state:
    st.session_state.welcome_shown = False
if "last_language" not in st.session_state:
    st.session_state.last_language = selected_language

# Show welcome message when language changes or on first load
if st.session_state.last_language != selected_language or not st.session_state.welcome_shown:
    welcome_msg = welcome_messages.get(selected_language, welcome_messages["English"])
    st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
    st.session_state.welcome_shown = True
    st.session_state.last_language = selected_language

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
user_input = st.chat_input("Type your message here...")

# Process user input
if user_input:
    if not api_key:
        st.error("Please enter your Sutra API key in the sidebar.")
    else:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Generate response
        try:
            # Create message placeholder
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                
                # Create a stream handler
                stream_handler = StreamHandler(response_placeholder)
                
                # Get streaming model with handler
                chat = get_streaming_chat_model(api_key, stream_handler)
                
                # Create system message indicating preferred language
                system_message = f"You are a helpful assistant. Please respond in {selected_language}."
                
                # Generate streaming response
                messages = [
                    HumanMessage(content=f"{system_message}\n\nUser message: {user_input}")
                ]
                
                response = chat.invoke(messages)
                answer = response.content
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")
            if "API key" in str(e):
                st.error("Please check your Sutra API key in the sidebar.")

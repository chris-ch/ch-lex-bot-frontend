
import os
import streamlit
import gettext
import base64

from mistralai import Mistral, SystemMessage, UserMessage

from helpers import string_to_stream


def render_svg(svg_file: str) -> str:
    with open(svg_file, "r") as f:
        svg_content = f.read()
    
    b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
    html = f'<img src="data:image/svg+xml;base64,{b64}" alt="Revault sàrl logo">'
    
    return html


def load_translations(lang):
    localedir = os.path.abspath(os.path.join(os.path.curdir, 'resources', 'locale'))
    if not os.path.exists(localedir):
        raise BaseException(f"Locale folder not found: {localedir}")
    translate = gettext.translation('messages', localedir, languages=[lang])
    translate.install()
    return translate.gettext


def start():
    # Initialize session state
    if "language" not in streamlit.session_state:
        streamlit.session_state.language = "en"
    if "user_description" not in streamlit.session_state:
        streamlit.session_state.user_description = ""
    if "previous_user_description" not in streamlit.session_state:
        streamlit.session_state.previous_user_description = ""
    
    streamlit.markdown("""
        <style>
        .language-selector {
            position: fixed;
            top: 10px;
            right: 10px;
            z-index: 1000;
        }
        .language-selector .stSelectbox {
            min-width: 50px;
            max-width: 50px;
        }
        .language-selector .stSelectbox > div > div {
            padding: 2px;
        }
        </style>
        """, unsafe_allow_html=True)
    
    language_options = {
        "🇩🇪": "de",
        "🇬🇧": "en",
        "🇫🇷": "fr",
        "🇮🇹": "it"
    }
    
    col1, col2 = streamlit.columns([7, 1])  # Adjust the ratio as needed

    # In the first (narrower) column, place your selectbox
    with col1:
        streamlit.image("resources/img/logo-revault-transp.png", width=200) 

    # In the second (wider) column, place your other content
    with col2:        
        # You can add more elements here as needed
        with streamlit.container():
            streamlit.markdown('<div class="language-selector">', unsafe_allow_html=True)
            selected_flag = streamlit.selectbox(
                " ",
                options=list(language_options.keys()),
                format_func=lambda x: x,
                key='language_selector',
                label_visibility="collapsed"
            )
            streamlit.markdown('</div>', unsafe_allow_html=True)
    
    if streamlit.session_state.language != language_options[selected_flag]:
        streamlit.session_state.language = language_options[selected_flag]
        streamlit.rerun()
        
    _ = load_translations(streamlit.session_state.language)
    
    # Show title and description.
    streamlit.title("💬 Lex Bot 🇨🇭")
    streamlit.write(
        _("Welcome to our virtual legal assistant.")
    )
    streamlit.write(
        _("Please briefly describe your legal situation below.")
    )
    streamlit.write(
        _("Our system will analyze your case and provide you with "
          "relevant references to applicable legal texts.")
    )
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    if not mistral_api_key:
        mistral_api_key = streamlit.text_input("Mistral API Key", type="password")
    if not mistral_api_key:
        streamlit.info(_("Please add your Mistral API key to continue."), icon="🗝️")
    else:

        # Create a Mistral client.
        client_llm = Mistral(api_key=mistral_api_key)

        # Create a session state variable to store the chat messages. This ensures that the
        # messages persist across reruns.
        if "messages" not in streamlit.session_state:
            streamlit.session_state.messages = []

        # Display the existing chat messages via `streamlit.chat_message`.
        for message in streamlit.session_state.messages:
            with streamlit.chat_message(message["role"]):
                streamlit.markdown(message["content"])

        # Create a chat text area to allow the user to enter a message.
        # This will display automatically at the bottom of the page.
        user_input = streamlit.empty()
        with user_input.container():
            user_description = streamlit.text_area(_("Please briefly describe your situation..."), height=150)
            submit_button = streamlit.button(_("Send"))

        if submit_button or streamlit.session_state.user_description != streamlit.session_state.get('user_description', ''):
            if user_description:
                streamlit.session_state['user_description'] = user_description
                streamlit.session_state.previous_user_description = streamlit.session_state.user_description
                streamlit.session_state.messages.append({"role": "user", "content": user_description})
                with streamlit.chat_message("user"):
                    streamlit.markdown(user_description)

                user_input.empty()

                # Generate a response using the Mistral API.
                system_message = SystemMessage(content=_("System prompt") + "\n\n" + _("Binding system and user messages") + "\n")
                user_message = UserMessage(content=user_description)
                response = client_llm.chat.complete(
                    model="open-mistral-nemo-2407",
                    messages=[system_message, user_message],
                    max_tokens=None,
                    temperature=0.,
                    )
                answer = response.choices[0].message.content
                stream = string_to_stream(answer)

                # Stream the response to the chat using `streamlit.write_stream`, then store it in 
                # session state.
                with streamlit.chat_message("assistant"):
                    response = streamlit.write_stream(stream)
                streamlit.session_state.messages.append({"role": "assistant", "content": response})
                

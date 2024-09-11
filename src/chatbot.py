
from enum import IntEnum
import logging
import os
import streamlit
import base64

from mistralai import Mistral, SystemMessage, UserMessage

import helpers
import i18n


class WorkflowStage(IntEnum):
    INITIAL = 1
    MORE_SUGGESTIONS = 2
    ANALYSIS = 3
    
    
def render_svg(svg_file: str) -> str:
    with open(svg_file, "r") as f:
        svg_content = f.read()
    
    b64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
    html = f'<img src="data:image/svg+xml;base64,{b64}" alt="Revault sàrl logo">'
    
    return html


def start():
    
    helpers.setup_logging_levels()
    
    language_options = {
        "🇩🇪": "de",
        "🇬🇧": "en",
        "🇫🇷": "fr",
        "🇮🇹": "it"
    }
    
    # Initialize session state
    if "language" not in streamlit.session_state:
        # Get language from query parameter, default to English if not specified
        default_lang_code = streamlit.query_params.get("lang", "fr")
        if default_lang_code not in language_options.values():
            default_lang_code = "fr"
        logging.info("defaulting to language '%s'", default_lang_code)
        streamlit.session_state.language = default_lang_code
    if "user_description" not in streamlit.session_state:
        streamlit.session_state.user_description = ""
    if "previous_user_description" not in streamlit.session_state:
        streamlit.session_state.previous_user_description = ""
    if "stage" not in streamlit.session_state:
        streamlit.session_state.stage = WorkflowStage.INITIAL
    
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
    
    col1, col2 = streamlit.columns([7, 1])  # Adjust the ratio as needed

    # In the first (narrower) column, place your selectbox
    with col1:
        streamlit.image("resources/img/logo-revault-transp.png", width=200) 

    # In the second (wider) column, place your other content
    with col2:        
        # You can add more elements here as needed
        with streamlit.container():
            streamlit.markdown('<div class="language-selector">', unsafe_allow_html=True)
            index_of_current_lang = list(language_options.values()).index(streamlit.session_state.language)
            selected_flag = streamlit.selectbox(
                " ",
                options=list(language_options.keys()),
                format_func=lambda x: x,
                key='language_selector',
                label_visibility="collapsed",
                index=index_of_current_lang
            )
            streamlit.markdown('</div>', unsafe_allow_html=True)
    
    if streamlit.session_state.language != language_options[selected_flag]:
        streamlit.session_state.language = language_options[selected_flag]
        streamlit.rerun()
        
    _ = i18n.load_translations(streamlit.session_state.language)
    
    # Show title and description.
    streamlit.title("💬 Lex Bot 🇨🇭")
    if streamlit.session_state.stage in (WorkflowStage.INITIAL, WorkflowStage.MORE_SUGGESTIONS):
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
    elif streamlit.session_state.stage == WorkflowStage.ANALYSIS:
        streamlit.write(
            _("The system is now analysing the case based on relevant legal references.")
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
                streamlit.markdown(message["content"], unsafe_allow_html=True)

        if streamlit.session_state.stage != WorkflowStage.ANALYSIS:
            # Create a chat text area to allow the user to enter a message.
            # This will display automatically at the bottom of the page.
            user_input = streamlit.empty()
            with user_input.container():
                user_description = streamlit.text_area(_("Case description..."), height=150, value=streamlit.session_state.user_description)
        
        move_forward_button = None
        suggestion_button = None
        if streamlit.session_state.stage == WorkflowStage.INITIAL:
            suggestion_button = streamlit.button(_("Send"))
        elif streamlit.session_state.stage == WorkflowStage.MORE_SUGGESTIONS:
            col1, col2 = streamlit.columns([1, 1])
            with col1:
                suggestion_button = streamlit.button(_("More Suggestions"))
            
            with col2:
                move_forward_button = streamlit.button(_("Move Forward"), type="primary")

        if move_forward_button:
            streamlit.session_state.stage = WorkflowStage.ANALYSIS
            streamlit.session_state.messages = [{"role": "assistant", "content": "Processing request:\n{0}".format(user_description)}]
            streamlit.rerun()
            
            with streamlit.chat_message("assistant"):
                placeholder = streamlit.empty()
                response_analysis = "The case is being processed..."
                placeholder.markdown(response_analysis, unsafe_allow_html=True)
            
        elif suggestion_button or streamlit.session_state.user_description != streamlit.session_state.get('user_description', ''):
            if streamlit.session_state.stage == WorkflowStage.INITIAL:
                streamlit.session_state.stage = WorkflowStage.MORE_SUGGESTIONS
                
            if user_description:
                streamlit.session_state['user_description'] = user_description
                streamlit.session_state.previous_user_description = streamlit.session_state.user_description
                streamlit.session_state.messages.append({"role": "user", "content": user_description})
                with streamlit.chat_message("user"):
                    streamlit.markdown(user_description)

                user_input.empty()

                # Generate a response using the Mistral API.
                system_prompt_quality_check = _("SYSTEM_PROMPT_QUALITY_CHECK")
                system_message = SystemMessage(content=system_prompt_quality_check + "\n")
                user_message = UserMessage(content=user_description)
               
                response = client_llm.chat.complete(
                    model="open-mistral-7b",  # "mistral-large-2407", "open-mistral-nemo-2407", "open-mistral-7b"
                    messages=[system_message, user_message],
                    max_tokens=None,
                    temperature=0.,
                    )
                answer = response.choices[0].message.content
                stream = helpers.string_to_stream(answer)
                # Stream the response to the chat using `streamlit.write_stream`, then store it in 
                # session state.
                with streamlit.chat_message("assistant"):
                    placeholder = streamlit.empty()
                    full_response = ""
                    
                    for chunk in stream:
                        full_response += chunk
                        placeholder.markdown(full_response, unsafe_allow_html=True)
                    
                    #placeholder.markdown(f"```markdown\n{full_response}\n```")
                    #response = streamlit.write_stream(stream)

                streamlit.session_state.messages.append({"role": "assistant", "content": answer})
                
                streamlit.rerun()
                
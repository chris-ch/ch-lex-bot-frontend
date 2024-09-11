"""Chatbot manager.
"""
from enum import IntEnum
import logging
import os
import streamlit

import handlers
import helpers
import i18n
import lang


class WorkflowStage(IntEnum):
    INITIAL = 1
    MORE_SUGGESTIONS = 2
    ANALYSIS = 3


def start():
    
    helpers.setup_logging_levels()
    
    # Initialize session state
    if "language" not in streamlit.session_state:
        default_lang_code = lang.get_default_language("fr")
        logging.info("defaulting to language '%s'", default_lang_code)
        streamlit.session_state.language = default_lang_code
    if "user_description" not in streamlit.session_state:
        streamlit.session_state.user_description = ""
    if "previous_user_description" not in streamlit.session_state:
        streamlit.session_state.previous_user_description = ""
    if "stage" not in streamlit.session_state:
        streamlit.session_state.stage = WorkflowStage.INITIAL
    if "messages" not in streamlit.session_state:
        streamlit.session_state.messages = []
    
    col1, col2 = streamlit.columns([7, 1])  # Adjust the ratio as needed

    with col1:
        streamlit.image("resources/img/logo-revault.svg", width=200) 

    with col2:
        current_language = streamlit.session_state.language
        selected_flag = lang.language_selector(current_language)
    
    if streamlit.session_state.language != lang.language_options[selected_flag]:
        streamlit.session_state.language = lang.language_options[selected_flag]
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
                user_input.empty()
                answer = handlers.handle_new_user_description(user_description)
                streamlit.session_state.messages.append({"role": "assistant", "content": answer})
                streamlit.rerun()

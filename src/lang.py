import streamlit


language_options = {
    "🇩🇪": "de",
    "🇬🇧": "en",
    "🇫🇷": "fr",
    "🇮🇹": "it"
}

def get_default_language(default_language_code: str) -> str:
    # Get language from query parameter
    lang_code = streamlit.query_params.get("lang", default_language_code)
    if lang_code not in language_options.values():
        lang_code = default_language_code
    return lang_code


def language_selector(current_language_code: str):
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
    
    with streamlit.container():
        streamlit.markdown('<div class="language-selector">', unsafe_allow_html=True)
        index_of_current_lang = list(language_options.values()).index(current_language_code)
        selected_flag = streamlit.selectbox(
            " ",
            options=list(language_options.keys()),
            format_func=lambda x: x,
            key='language_selector',
            label_visibility="collapsed",
            index=index_of_current_lang
        )
        streamlit.markdown('</div>', unsafe_allow_html=True)
    return selected_flag

import os
import streamlit

import helpers

from mistralai import Mistral, SystemMessage, UserMessage


def handle_new_user_description(user_description: str) -> str:
    
    with streamlit.chat_message("user"):
        streamlit.markdown(user_description)

    # Generate a response using the Mistral API.
    system_prompt_quality_check = _("SYSTEM_PROMPT_QUALITY_CHECK")
    system_message = SystemMessage(content=system_prompt_quality_check + "\n")
    user_message = UserMessage(content=user_description)
    
    # Create a Mistral client.
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    client_llm = Mistral(api_key=mistral_api_key)
        
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
    return answer
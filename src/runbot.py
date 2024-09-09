
import streamlit
from helpers import string_to_stream


def start():
    
    # Show title and description.
    streamlit.title("💬 Lex Bot 🇨🇭")
    streamlit.write(
        "This is a simple chatbot that simply echoes your inputs to generate responses. "
        "TODO: connect to backend."
    )

    # Ask user for their OpenAI API key via `streamlit.text_input`.
    # Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
    # via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    mistral_api_key = streamlit.text_input("Mistral API Key", type="password")
    if not mistral_api_key:
        streamlit.info("Please add your Mistral API key to continue.", icon="🗝️")
    else:

        # Create an Mistral client.
        #client = Mistral(api_key=mistral_api_key)

        # Create a session state variable to store the chat messages. This ensures that the
        # messages persist across reruns.
        if "messages" not in streamlit.session_state:
            streamlit.session_state.messages = []

        # Display the existing chat messages via `st.chat_message`.
        for message in streamlit.session_state.messages:
            with streamlit.chat_message(message["role"]):
                streamlit.markdown(message["content"])

        # Create a chat input field to allow the user to enter a message. This will display
        # automatically at the bottom of the page.
        if prompt := streamlit.chat_input("What is up?"):

            # Store and display the current prompt.
            streamlit.session_state.messages.append({"role": "user", "content": prompt})
            with streamlit.chat_message("user"):
                streamlit.markdown(prompt)

            # Generate a response using the OpenAI API.
            _ = """ stream = client.chat.completions.create(
                model="mistral-nemo-12b",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in streamlit.session_state.messages
                ],
                stream=True,
            ) """
            stream = string_to_stream(prompt)

            # Stream the response to the chat using `st.write_stream`, then store it in 
            # session state.
            with streamlit.chat_message("assistant"):
                response = streamlit.write_stream(stream)
            streamlit.session_state.messages.append({"role": "assistant", "content": response})

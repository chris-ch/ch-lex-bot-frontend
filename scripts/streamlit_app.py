import time
import streamlit as st


def string_to_stream(input_string, delay=0.05):
    for word in input_string.split():
        yield word + " "
        time.sleep(delay)


def main():
    # Show title and description.
    st.title("💬 Chatbot")
    st.write(
        "This is a simple chatbot that simply echoes your inputs to generate responses. "
        "TODO: connect to backend."
    )

    # Ask user for their OpenAI API key via `st.text_input`.
    # Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
    # via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    mistral_api_key = st.text_input("Mistral API Key", type="password")
    if not mistral_api_key:
        st.info("Please add your Mistral API key to continue.", icon="🗝️")
    else:

        # Create an Mistral client.
        #client = Mistral(api_key=mistral_api_key)

        # Create a session state variable to store the chat messages. This ensures that the
        # messages persist across reruns.
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display the existing chat messages via `st.chat_message`.
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Create a chat input field to allow the user to enter a message. This will display
        # automatically at the bottom of the page.
        if prompt := st.chat_input("What is up?"):

            # Store and display the current prompt.
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate a response using the OpenAI API.
            _ = """ stream = client.chat.completions.create(
                model="mistral-nemo-12b",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            ) """
            stream = string_to_stream(prompt)

            # Stream the response to the chat using `st.write_stream`, then store it in 
            # session state.
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
    

if __name__ == "__main__":
    main()

import streamlit as st
from streamlit_oauth import OAuth2Component
import base64
import json
from fetch import fetch
import time
import urllib.parse

# Declare Maintenance
maintenance = False
if maintenance == True:
        st.title("Tweet Generator")
        st.write("The application is currently under maintenance. Please try again later.")
        st.stop()
else:
    # import logging
    # logging.basicConfig(level=logging.INFO)

    # create an OAuth2Component instance
    CLIENT_ID = st.secrets["google"]["CLIENT_ID"]
    CLIENT_SECRET = st.secrets["google"]["CLIENT_SECRET"]
    AUTHORIZE_ENDPOINT = st.secrets["google"]["AUTHORIZE_ENDPOINT"]
    TOKEN_ENDPOINT = st.secrets["google"]["TOKEN_ENDPOINT"]
    REVOKE_ENDPOINT = st.secrets["google"]["REVOKE_ENDPOINT"]

    if "auth" not in st.session_state:
        # create a button to start the OAuth2 flow
        oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)
        st.title("Tweet Generator")
        st.divider()
        st.write("Please login to continue.")
        result = oauth2.authorize_button(
            name="Continue with Google",
            icon="https://www.google.com.tw/favicon.ico",
            redirect_uri="https://tweet-generator-ai.streamlit.app/",
            scope="openid email profile",
            key="google",
            extras_params={"prompt": "consent", "access_type": "offline"},
            use_container_width=True,
            pkce='S256',
        )
        
        if result:
            st.write(result)
            # decode the id_token jwt and get the user's email address
            id_token = result["token"]["id_token"]
            # verify the signature is an optional step for security
            payload = id_token.split(".")[1]
            # add padding to the payload if needed
            payload += "=" * (-len(payload) % 4)
            payload = json.loads(base64.b64decode(payload))
            email = payload["email"]
            st.session_state["auth"] = email
            st.session_state["token"] = result["token"]
            st.rerun()
    else:
        st.title("Tweet Generator")
        st.divider()
        with st.form("tweet_form"):
            topic = st.text_input("Enter the topic of the tweet")
            mood = st.text_input("Enter the mood of the tweet")
            style = st.text_input("Enter the style of the tweet")
            generate_button = st.form_submit_button("Generate Tweet")

            if generate_button:
                with st.spinner("Generating tweet..."):
                    try:
                        tweet = fetch(topic, mood, style)
                    except KeyError:
                        st.error("An error occurred while generating the tweet. Please try again.")
                    else:
                        def stream_data():
                            for word in tweet.split(" "):
                                yield word + " "
                                time.sleep(0.7)  # Adjust the sleep time to control the speed of the stream
                        if tweet:
                            st.success("Tweet generated!")
                        st.write(tweet)
                        encoded_tweet = urllib.parse.quote(tweet)
                        tweet_url = f"https://twitter.com/intent/tweet?text={encoded_tweet}"
                        button_css = """
                        <style>
                        .tweet-button {
                            display: inline-block;
                            padding: 10px 20px;
                            font-size: 16px;
                            cursor: pointer;
                            text-align: center;
                            text-decoration: none;
                            outline: none;
                            color: #fff;
                            background-color: #000;
                            border: 2px solid transparent;
                            border-color: #565E5F;
                            border-radius: 5px;
                            transition: border-color 0.3s;
                        }
                        .tweet-button:hover {
                            border-color: #fff;
                        }
                        .tweet-button:active {
                            border-color: #fff;
                            box-shadow: 0 5px #666;
                            transform: translateY(4px);
                        }
                        </style>
                        """
                        
                        button_html = f"""
                        <a href="{tweet_url}" target="_blank" class="tweet-button">Post Tweet</a>
                        """
                        
                        st.markdown(button_css + button_html, unsafe_allow_html=True)

        if st.button("Logout"):
            del st.session_state["auth"]
            del st.session_state["token"]
            st.rerun()

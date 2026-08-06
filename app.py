"""
==========================================================
🎨 ArtStyle Advisor
AI Chat + AI Image Generator
Built with Streamlit + Groq + Pollinations AI
==========================================================
"""

import os
import re
import base64
import requests

from io import BytesIO
from PIL import Image

import streamlit as st

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)


# ==========================================================
# LOAD ENV
# ==========================================================

load_dotenv()

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="ArtStyle Advisor",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ==========================================================
# PATHS
# ==========================================================

CURRENT_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CSS_PATH = os.path.join(
    CURRENT_DIR,
    "assets",
    "style.css"
)

BACKGROUND_PATH = os.path.join(
    CURRENT_DIR,
    "art bg.png"
)


# ==========================================================
# LOAD CSS
# ==========================================================

def load_css():

    if os.path.exists(CSS_PATH):

        with open(
            CSS_PATH,
            encoding="utf-8"
        ) as f:

            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )


# ==========================================================
# BACKGROUND
# ==========================================================

def get_base64(file_path):

    with open(file_path, "rb") as img:

        return base64.b64encode(
            img.read()
        ).decode()


def set_background():

    if not os.path.exists(BACKGROUND_PATH):

        return

    encoded = get_base64(
        BACKGROUND_PATH
    )

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-image:
                url("data:image/png;base64,{encoded}");

            background-size: cover;

            background-position: center center;

            background-repeat: no-repeat;

            background-attachment: fixed;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


load_css()
set_background()


# ==========================================================
# MODEL SETTINGS
# ==========================================================

MODEL_NAME = "llama-3.1-8b-instant"

TEMPERATURE = 0.3


SECTION_HEADERS = [

    "Brief Explanation",

    "Step-by-step Guidance",

    "Advantages",

    "Disadvantages",

    "Precautions",
 
    "Best Practices",

]


SYSTEM_PROMPT = """
You are ArtStyle Advisor.

Only answer questions related to:

Drawing
Painting
Sketching
Anime
Realism
Digital Art
Watercolor
Mandala
Portrait
Landscape
Perspective
Color Theory
Character Design
Creativity
Art Practice

If user asks anything else politely refuse.

For every art question always answer using these six headings:

1. Brief Explanation

2. Step-by-step Guidance

3. Advantages

4. Disadvantages

5. Precautions

6. Best Practices

Never use markdown.

Never use HTML.

Only plain readable text.
"""


# ==========================================================
# SESSION STATE
# ==========================================================

if "chat_response" not in st.session_state:

    st.session_state.chat_response = ""


if "generated_image" not in st.session_state:

    st.session_state.generated_image = None


if "generated_text" not in st.session_state:

    st.session_state.generated_text = ""


if "history" not in st.session_state:

    st.session_state.history = []


# ==========================================================
# GROQ CHATBOT
# ==========================================================

def get_ai_response(question):

    if not GROQ_API_KEY:

        return (
            "Please add GROQ_API_KEY "
            "in your .env file."
        )

    try:

        llm = ChatGroq(

            groq_api_key=GROQ_API_KEY,

            model_name=MODEL_NAME,

            temperature=TEMPERATURE,

        )

        messages = [

            SystemMessage(
                content=SYSTEM_PROMPT
            ),

            HumanMessage(
                content=question
            ),

        ]

        result = llm.invoke(
            messages
        )

        answer = result.content.strip()

        answer = (
            answer
            .replace("**", "")
            .replace("##", "")
            .replace("###", "")
            .replace("`", "")
        )

        return answer

    except Exception as e:

        return f"❌ Error: {e}"


def generate_image(prompt):
    try:
        prompt = requests.utils.quote(prompt.strip())

        image_url = (
            f"https://image.pollinations.ai/prompt/{prompt}"
            "?width=1024"
            "&height=1024"
            "&model=flux"
            "&enhance=true"
            "&nologo=true"
        )

        print("=" * 50)
        print("URL:", image_url)

        response = requests.get(
            image_url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=180
        )

        print("Status Code:", response.status_code)
        print("Content-Type:", response.headers.get("Content-Type"))

        if response.status_code != 200:
            print(response.text[:500])
            return None, f"Server Error: {response.status_code}"

        # Make sure server returned an image
        if "image" not in response.headers.get("Content-Type", ""):
            print(response.text[:500])
            return None, "Server did not return an image."

        image = Image.open(BytesIO(response.content))

        return image, "✅ Image generated successfully."

    except Exception as e:
        print("ERROR:", e)
        return None, str(e)

# ==========================================================
# RESPONSE FORMATTER
# ==========================================================

HEADER_PATTERN = re.compile(

    r"^\s*\d+\.\s*(" +

    "|".join(
        re.escape(h)
        for h in SECTION_HEADERS
    )

    + r")\s*:?\s*$",

    re.IGNORECASE

)


def format_response(answer):

    html = ""

    for line in answer.split("\n"):

        line = line.strip()

        if not line:

            html += "<br>"

            continue

        if HEADER_PATTERN.match(line):

            html += (
                '<div class="section-heading">'
                f'{line}'
                '</div>'
            )

        else:

            html += (
                '<div class="section-line">'
                f'{line}'
                '</div>'
            )

    return html


# ==========================================================
# CHAT HISTORY
# ==========================================================

def save_chat(
    question,
    answer
):

    st.session_state.history.append(

        {
            "question": question,
            "answer": answer
        }

    )


def clear_chat():

    st.session_state.history = []

    st.session_state.chat_response = ""


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    """
    <div class="app-title">
        🎨 ArtStyle Advisor
    </div>

    <div class="app-subtitle">
        Your AI Mentor for Drawing, Painting, Sketching & Creativity
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# CHAT / DRAW SWITCH
# ==========================================================

from streamlit_option_menu import option_menu

left, center, right = st.columns([1.5, 2, 1.5])

with center:
    selected = option_menu(
        menu_title=None,
        options=["Chat", "Draw"],
        icons=["chat-fill", "palette-fill"],
        orientation="horizontal",
        styles={
            "container": {
                "padding": "8px",
                "background-color": "#e5d1f1",
                "border-radius": "16px",
            },
            "nav-link": {
                "font-size": "18px",
                "font-weight": "600",
                "color": "#6A1BB1",
                "border-radius": "15px",
                "margin": "0px 8px",
                "text-align": "center",
            },
            "nav-link-selected": {
                "background-color": "#AA60EF",
                "color": "white",
                "border-radius": "15px",
            },
        },
    )

mode = "💬 Chat" if selected == "Chat" else "🖌 Draw"

# ==========================================================
# CHAT
# ==========================================================

if mode == "💬 Chat":

    st.markdown(
        """
        <div class="input-label">
            Ask your art question
        </div>
        """,
        unsafe_allow_html=True
    )


    user_question = st.text_area(

        "question",

        placeholder=(
            "Example : How do I draw realistic eyes?"
        ),

        height=150,

        key="chat_input",

        label_visibility="collapsed"

    )


    if st.button(

        "✨ Ask ArtStyle Advisor",

        use_container_width=True,

        key="chat_btn"

    ):

        if user_question.strip():

            with st.spinner(
                "Thinking..."
            ):

                answer = get_ai_response(
                    user_question
                )

                st.session_state.chat_response = (
                    answer
                )

                save_chat(
                    user_question,
                    answer
                )

        else:

            st.warning(
                "Please enter a question."
            )


    # ------------------------------------------------------
    # RESPONSE
    # ------------------------------------------------------

    if st.session_state.chat_response:

        with st.container(
            key="response_card"
        ):

            st.markdown(
                """
                <div class="response-title">
                    🤖 ArtStyle Advisor
                </div>

                <hr class="response-divider">
                """,
                unsafe_allow_html=True
            )


            st.markdown(

                f"""
                <div class="response-text">

                {format_response(
                    st.session_state.chat_response
                )}

                </div>
                """,

                unsafe_allow_html=True

            )


# ==========================================================
# DRAW
# ==========================================================

else:

    st.markdown(
        """
        <div class="input-label">
            Describe your imagination
        </div>
        """,
        unsafe_allow_html=True
    )


    image_prompt = st.text_area(

        "image_prompt",

        placeholder=(
            "Example : Anime girl painting "
            "in a magical forest"
        ),

        height=150,

        key="draw_input",

        label_visibility="collapsed"

    )


    if st.button(

        "🎨 Generate Artwork",

        use_container_width=True,

        key="draw_btn"

    ):

        if image_prompt.strip():

            with st.spinner(
                "Generating artwork..."
            ):

                image, text = generate_image(
                    image_prompt
                )
                st.write(text)

                st.session_state.generated_image = (
                    image
                )

                st.session_state.generated_text = (
                    text
                )

        else:

            st.warning(
                "Please enter an image prompt."
            )


    # ------------------------------------------------------
    # GENERATED IMAGE
    # ------------------------------------------------------

    if st.session_state.generated_image is not None:

        st.image(
            st.session_state.generated_image,
            use_container_width=True
        )


        buffer = BytesIO()

        st.session_state.generated_image.save(
            buffer,
            format="PNG"
        )


        st.download_button(

            label="📥 Download Image",

            data=buffer.getvalue(),

            file_name="artstyle_artwork.png",

            mime="image/png",

            use_container_width=True

        )


        if st.session_state.generated_text:

            st.success(
                st.session_state.generated_text
            )


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title(
        "🎨 ArtStyle Advisor"
    )


    st.write(
        """
Welcome to ArtStyle Advisor!

This AI assistant helps you with:

🎨 Drawing

🖌 Painting

✏ Sketching

🌸 Anime

🧑‍🎨 Character Design

🌄 Landscape

🎭 Creativity

💡 Art Practice
        """
    )


    st.divider()


    if st.button(
        "🗑 Clear Chat",
        use_container_width=True
    ):

        clear_chat()

        st.session_state.generated_image = None

        st.session_state.generated_text = ""

        st.rerun()


    st.divider()


    st.subheader(
        "🕘 Chat History"
    )


    if len(
        st.session_state.history
    ) == 0:

        st.info(
            "No conversation yet."
        )

    else:

        for item in reversed(
            st.session_state.history
        ):

            with st.expander(
                item["question"][:40] + "..."
            ):

                st.write(
                    item["answer"]
                )


# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
    """
    <div class="footer">
        Made with ❤️ using Streamlit • Groq AI • Pollinations AI
    </div>
    """,
    unsafe_allow_html=True
)

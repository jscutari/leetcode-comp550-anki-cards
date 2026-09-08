import base64
import io

import streamlit as st
import google.generativeai as genai

from PIL import Image


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="Flashcard Generator",
    page_icon="◼",
    layout="centered",
)


# ============================================================
# GEMINI SETUP
# ============================================================

# Replace with your actual Gemini API key
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

model = genai.GenerativeModel("gemini-3.8-flash")


# ============================================================
# GLOBAL STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- Main page ---------- */

    .stApp {
        background-color: #F4EFE4;
        color: #111111;
    }

    .block-container {
        max-width: 850px;
        padding-top: 3.5rem;
        padding-bottom: 5rem;
    }

    [data-testid="stHeader"] {
        background-color: transparent;
    }

    /* ---------- Typography ---------- */

    h1, h2, h3, h4, h5, h6,
    p, label, span, div {
        color: #111111;
    }

    .app-title {
        font-size: 2.6rem;
        font-weight: 650;
        letter-spacing: -0.045em;
        line-height: 1.05;
        margin-bottom: 0.35rem;
    }

    .app-subtitle {
        color: #6D685F;
        font-size: 0.95rem;
        margin-bottom: 2.5rem;
    }

    .section-label {
        font-size: 0.78rem;
        font-weight: 650;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 1.4rem;
        margin-bottom: 0.55rem;
    }

    .image-count {
        color: #6D685F;
        font-size: 0.85rem;
        margin-top: 0.3rem;
        margin-bottom: 0.8rem;
    }

    /* ---------- Text area ---------- */

    textarea {
        background-color: #FBF8F1 !important;
        color: #111111 !important;
        border: 1px solid #BEB7AA !important;
        border-radius: 10px !important;
    }

    textarea:focus {
        border-color: #111111 !important;
        box-shadow: 0 0 0 1px #111111 !important;
    }

    /* ---------- Buttons ---------- */

    .stButton > button {
        background-color: transparent;
        color: #111111;
        border: 1px solid #111111;
        border-radius: 9px;
        font-weight: 550;
        transition: 0.15s ease;
    }

    .stButton > button:hover {
        background-color: #111111;
        color: #F4EFE4;
        border-color: #111111;
    }

    /* Main Generate button */

    .generate-button .stButton > button {
        background-color: #111111;
        color: #F4EFE4;
        border: 1px solid #111111;
        min-height: 3rem;
        font-size: 1rem;
    }

    .generate-button .stButton > button:hover {
        background-color: #292929;
        color: #F4EFE4;
    }

    /* ---------- Radio ---------- */

    [data-testid="stRadio"] {
        margin-bottom: 0.5rem;
    }

    [data-testid="stRadio"] label {
        color: #111111 !important;
    }

    /* ---------- Checkbox ---------- */

    [data-testid="stCheckbox"] label {
        color: #111111 !important;
    }

    /* ---------- Containers ---------- */

    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FBF8F1;
        border-color: #C8C1B5 !important;
        border-radius: 12px;
    }

    /* ---------- Image previews ---------- */

    [data-testid="stImage"] img {
        border-radius: 8px;
        border: 1px solid #D0C9BD;
    }

    /* ---------- Alerts ---------- */

    [data-testid="stAlert"] {
        background-color: #FBF8F1;
        color: #111111;
        border: 1px solid #C8C1B5;
    }

    /* ---------- Spinner ---------- */

    [data-testid="stSpinner"] {
        color: #111111;
    }

    /* ---------- Divider ---------- */

    hr {
        border-color: #C8C1B5;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PASTE COMPONENT
# ============================================================

paste_zone = st.components.v2.component(
    name="image_paste_zone",

    html="""
        <div
            id="paste-zone"
            tabindex="0"
            contenteditable="true"
            spellcheck="false"
        >
            <div class="paste-plus">+</div>

            <div class="paste-title">
                Paste image(s)
            </div>

            <div class="paste-description">
                Click here, then press ⌘V / Ctrl+V
            </div>

            <div class="paste-secondary">
                Paste again to add another image
            </div>
        </div>
    """,

    css="""
        #paste-zone {
            width: 100%;
            box-sizing: border-box;

            min-height: 175px;

            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;

            background: #FBF8F1;

            border: 1.5px dashed #777168;
            border-radius: 13px;

            cursor: text;
            user-select: none;
            caret-color: transparent;

            transition:
                border-color 120ms ease,
                background-color 120ms ease;
        }

        #paste-zone:hover {
            border-color: #111111;
            background: #F8F3EA;
        }

        #paste-zone:focus {
            outline: none;
            border: 1.5px solid #111111;
            background: #F8F3EA;
        }

        .paste-plus {
            width: 34px;
            height: 34px;

            border: 1px solid #111111;
            border-radius: 50%;

            display: flex;
            align-items: center;
            justify-content: center;

            color: #111111;

            font-family: Arial, sans-serif;
            font-size: 23px;
            font-weight: 300;

            margin-bottom: 12px;
        }

        .paste-title {
            color: #111111;

            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            font-size: 16px;
            font-weight: 600;

            margin-bottom: 5px;
        }

        .paste-description {
            color: #57524B;

            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            font-size: 13px;
        }

        .paste-secondary {
            color: #918A80;

            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;

            font-size: 12px;

            margin-top: 4px;
        }
    """,

    js="""
        export default function(component) {

            const {
                parentElement,
                setTriggerValue
            } = component;

            const zone =
                parentElement.querySelector("#paste-zone");


            async function fileToDataURL(file) {

                return new Promise((resolve, reject) => {

                    const reader = new FileReader();

                    reader.onload = () => {
                        resolve(reader.result);
                    };

                    reader.onerror = reject;

                    reader.readAsDataURL(file);
                });
            }


            async function processClipboard(event) {

                event.preventDefault();

                const items =
                    Array.from(event.clipboardData.items);

                const imageFiles = [];

                for (const item of items) {

                    if (item.type.startsWith("image/")) {

                        const file = item.getAsFile();

                        if (file) {
                            imageFiles.push(file);
                        }
                    }
                }


                if (imageFiles.length === 0) {

                    const description =
                        zone.querySelector(".paste-description");

                    const oldText =
                        description.textContent;

                    description.textContent =
                        "Clipboard does not contain an image";

                    setTimeout(() => {
                        description.textContent = oldText;
                    }, 1500);

                    return;
                }


                const images =
                    await Promise.all(
                        imageFiles.map(fileToDataURL)
                    );


                setTriggerValue(
                    "images",
                    images
                );
            }


            zone.addEventListener(
                "paste",
                processClipboard
            );


            zone.addEventListener(
                "click",
                () => zone.focus()
            );
        }
    """,
)


# ============================================================
# IMAGE HELPERS / SESSION STATE
# ============================================================

if "pasted_images" not in st.session_state:
    st.session_state.pasted_images = []


def data_url_to_image(data_url):

    # Data URL format:
    # data:image/png;base64,AAAA....
    _, encoded = data_url.split(",", 1)

    image_bytes = base64.b64decode(encoded)

    image = Image.open(
        io.BytesIO(image_bytes)
    )

    return image.convert("RGB")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="app-title">
        Flashcard Generator
    </div>

    <div class="app-subtitle">
        LeetCode + COMP 550 → Anki
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# UI CONTROLS
# ============================================================

st.markdown(
    '<div class="section-label">Mode</div>',
    unsafe_allow_html=True,
)

mode = st.radio(
    "Select Mode:",
    ("LeetCode", "COMP 550"),
    horizontal=True,
    label_visibility="collapsed",
)


if mode == "LeetCode":

    skip_brute = st.checkbox(
        "Skip Brute Force Explanation"
    )

else:

    skip_brute = False


st.markdown(
    '<div class="section-label">Extra Notes</div>',
    unsafe_allow_html=True,
)

extra_notes = st.text_area(
    "Extra Notes to append to the bottom of the card:",
    placeholder="Optional notes...",
    height=110,
    label_visibility="collapsed",
)


# ============================================================
# IMAGE PASTE AREA
# ============================================================

st.markdown(
    '<div class="section-label">Images</div>',
    unsafe_allow_html=True,
)


# Callback is required so the trigger value exists.
paste_result = paste_zone(
    on_images_change=lambda: None,
    key="image_paste_zone",
)


# New image(s) were pasted
if paste_result.images:

    for data_url in paste_result.images:

        try:

            image = data_url_to_image(data_url)

            st.session_state.pasted_images.append(
                image
            )

        except Exception as e:

            st.error(
                f"Could not read pasted image: {e}"
            )


# ============================================================
# IMAGE PREVIEWS
# ============================================================

images = st.session_state.pasted_images


if images:

    count = len(images)

    st.markdown(
        f"""
        <div class="image-count">
            {count} image{"s" if count != 1 else ""} added
        </div>
        """,
        unsafe_allow_html=True,
    )


    # Display three previews per row
    for row_start in range(0, len(images), 3):

        row_images = images[
            row_start:row_start + 3
        ]

        cols = st.columns(3)

        for offset, image in enumerate(row_images):

            index = row_start + offset

            with cols[offset]:

                st.image(
                    image,
                    use_container_width=True,
                )

                if st.button(
                    "Remove",
                    key=f"remove_image_{index}",
                    use_container_width=True,
                ):

                    del st.session_state.pasted_images[
                        index
                    ]

                    st.rerun()


    if len(images) > 1:

        if st.button(
            "Clear all images",
            use_container_width=False,
        ):

            st.session_state.pasted_images = []

            st.rerun()


else:

    st.markdown(
        """
        <div class="image-count">
            No images added yet.
        </div>
        """,
        unsafe_allow_html=True,
    )


st.write("")


# ============================================================
# GENERATE BUTTON
# ============================================================

st.markdown(
    '<div class="generate-button">',
    unsafe_allow_html=True,
)

generate = st.button(
    "Generate Anki Card",
    use_container_width=True,
)

st.markdown(
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# GENERATION LOGIC
# ============================================================

if generate:

    if images:

        # ====================================================
        # BASE PROMPTS
        # ====================================================

        if mode == "LeetCode":

            brute_force_rule = (
                "Skip the brute force explanation entirely."
                if skip_brute
                else
                "For brute force only discuss the solution conceptually. "
                "Talk about time complexity/space considerations for each "
                "solution as you go in each solution."
            )


            prompt = f"""

            Create a front/back anki card (non-latex). First summarize the problem/optimal solution and subpattern in one sentence (tell me enough to remember how to do the solution). 

            Then explain the pattern of this problem, total time complexity/space in both the brute force and optimized solutions. 

            Make a coding conceptual solution that walks through each step of optimized code. 

            {brute_force_rule}

            Make note at the bottom of: {extra_notes}

            Don't use analogies, explain practically and simply. Front should mention subpattern as well (don't say img reference).

            """


        else:

            prompt = f"""

            Create a front/back anki card (non-latex). First summarize the problem/optimal solution and subpattern in one sentence (tell me enough to remember how to do the solution). 

            Then explain the pattern of this problem, summarize the lectures notes in depth and any different problem solving approaches that are mentioned. 

            Then make a conceptual guide that walks through each step of the pseudocode and repeat the optimized pseudocode from the textbook. 

            Talk about time complexity/space considerations for each solution as you go in each solution. 

            Final ends by relating this problem to leetcode by naming the related leetcode problem and providing a python coded solution.

            Make note at the bottom of: {extra_notes}

            Don't use analogies, explain practically and simply. Only title for the front card should be the exact name of the problem from the textbook (you still include relevant information on the front).

            Also rewrite names of methods, classes, and variables to snake_case and more similar to python.

            """


        # ====================================================
        # GEMINI REQUEST
        # ====================================================

        with st.spinner(
            "Analyzing pasted image(s) and generating card..."
        ):

            try:

                payload = [prompt] + images

                response = model.generate_content(
                    payload
                )


                st.divider()

                st.markdown(
                    '<div class="section-label">Generated Card</div>',
                    unsafe_allow_html=True,
                )

                with st.container(border=True):

                    st.markdown(
                        response.text
                    )


            except Exception as e:

                st.error(
                    f"Gemini request failed: {e}"
                )


    else:

        st.warning(
            "Please paste at least one image first."
        )
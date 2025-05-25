import os

os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

import re
import io
import streamlit as st
import pandas as pd
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 1) Streamlit page config must be first Streamlit command
st.set_page_config(page_title="AI STD Generator", layout="wide")

# 2) Get default API key from .env
default_api_key = os.getenv("OPENAI_API_KEY", "")

# 3) Sidebar: let user override API key at runtime
st.sidebar.subheader("OpenAI Configuration")
api_key_input = st.sidebar.text_input(
    "Your OpenAI API Key",
    value=default_api_key,
    type="password",
    help="Enter a key starting with sk- or leave blank to use .env"
)
effective_api_key = api_key_input.strip() or default_api_key
if not effective_api_key:
    st.sidebar.error("Please enter a valid OpenAI API key.")
    st.stop()

# 4) Custom CSS for styling
st.markdown(
    """
    <style>
    /* Button styling */
    .stButton>button {
        background-color: #0052CC;
        color: white;
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: bold;
    }
    /* Expander (test case card) styling */
    .stExpander {
        background: #FFFFFF;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        padding: 16px;
        margin-bottom: 16px;
    }
    /* Header styling */
    .title {
        font-size: 2.5rem;
        color: #0052CC;
        font-weight: 600;
        margin-bottom: 24px;
    }
    /* Increase sidebar width */
    section.stSidebar {
        width: 400px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 5) Title
st.markdown("<div class='title'>AI STD Generator</div>", unsafe_allow_html=True)

# 6) Sidebar inputs: feature spec
st.sidebar.header("Input Specifications")
feature_name = st.sidebar.text_input(
    "Feature Name",
    placeholder="Enter feature name..."
)
characterization = st.sidebar.text_area(
    "Characterization (spec text)",
    height=200,
    placeholder="Paste specification here..."
)
upload_file = st.sidebar.file_uploader(
    "Or upload .txt spec file",
    type=["txt"]
)

# 7) Sidebar: upload spec images
uploaded_images = st.sidebar.file_uploader(
    "Upload spec images",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 8) If images provided, show thumbnails & produce captions via BLIP
image_captions = []
if uploaded_images:
    # load processor always in slow mode
    processor = BlipProcessor.from_pretrained(
        "Salesforce/blip-image-captioning-base",
        use_fast=False     # ← force the slow processor
    )
    cap_model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )

    for img_file in uploaded_images:
        img = Image.open(img_file)
        st.sidebar.image(img, caption=img_file.name, use_container_width=True)
        # prepare inputs & generate
        inputs = processor(images=img, return_tensors="pt")
        out_ids = cap_model.generate(**inputs)
        caption = processor.decode(out_ids[0], skip_special_tokens=True)
        image_captions.append(f"{img_file.name}: {caption}")

# 9) Sidebar: model choice + action buttons
st.sidebar.subheader("Generation Settings")
model = st.sidebar.selectbox(
    "Select Model",
    ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"],
    index=0
)
col1, col2 = st.sidebar.columns(2)
with col1:
    generate = st.sidebar.button("Generate STD")
with col2:
    download = st.sidebar.button("Download CSV")

# 10) Initialize OpenAI client
client = OpenAI(api_key=effective_api_key)

# 11) Session state for tests
if 'tests' not in st.session_state:
    st.session_state.tests = []

# 12) Generate test cases
if generate:
    spec_text = (
        upload_file.getvalue().decode('utf-8')
        if upload_file else
        characterization
    )
    if not feature_name or not spec_text:
        st.error("Please provide both Feature Name and specification text.")
    else:
        # assemble prompt
        prompt = (
            f"Generate test cases in JSON array format for Testmo import.\n"
            f"Feature: {feature_name}\n"
            f"Specification:\n{spec_text}\n"
        )
        if image_captions:
            prompt += "\nImage Descriptions:\n"
            for c in image_captions:
                prompt += f"- {c}\n"
        prompt += (
            "\nEach object should include: "
            "title, preconditions, severity, steps (array), expected, tags (array)."
        )

        with st.spinner("Generating test cases..."):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a test case generator."},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )

        raw = response.choices[0].message.content
        # extract JSON
        match = re.search(r"\[.*\]", raw, flags=re.DOTALL)
        json_str = match.group(0) if match else raw

        try:
            tests_json = pd.read_json(io.StringIO(json_str))
            st.session_state.tests = tests_json.to_dict(orient='records')
        except Exception as e:
            st.error(f"Failed to parse LLM response: {e}")
            st.code(raw, language='')

# 13) Display generated tests
if st.session_state.tests:
    st.markdown("### Generated Test Cases")
    select_all = st.checkbox("Select All Tests", key="select_all")
    selected = []

    for idx, test in enumerate(st.session_state.tests):
        cols = st.columns([1, 9])
        checked = cols[0].checkbox(
            label=f"chk_{idx}",
            key=f"chk_{idx}",
            value=select_all,
            label_visibility="hidden"
        )
        with cols[1].expander(test["title"]):
            st.markdown(f"**Preconditions:** {test.get('preconditions','')}")
            st.markdown(f"**Severity:** {test.get('severity','')}")
            st.markdown("**Steps:**")
            for step in test.get('steps', []):
                st.markdown(f"- {step}")
            st.markdown(f"**Expected:** {test.get('expected','')}")
            st.markdown(f"**Tags:** {', '.join(test.get('tags',[]))}")
        if checked:
            selected.append(test)

    # Download as CSV
    if download:
        df = pd.DataFrame(selected or st.session_state.tests)
        df.rename(
            columns={'title':'Title','steps':'Steps','expected':'Expected'},
            inplace=True
        )
        df['Steps'] = df['Steps'].apply(
            lambda s: '\n'.join(s) if isinstance(s, list) else s
        )
        df['Folder'] = feature_name
        df['Tags'] = df['tags'].apply(
            lambda t: ','.join(t) if isinstance(t, list) else t
        )
        csv_data = df[['Title','Steps','Expected','Folder','Tags']].to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="testmo_import.csv",
            mime='text/csv'
        )

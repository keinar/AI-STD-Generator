import os
import re
import streamlit as st
import pandas as pd
import io
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.sidebar.error("Please set OPENAI_API_KEY in your .env file and restart.")
    st.stop()

# Page config
st.set_page_config(page_title="AI STD Generator", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    /* Button styling */
    .stButton>button { background-color: #0052CC; color: white; border-radius: 8px; padding: 8px 20px; font-weight: bold; }
    /* Expander (test case card) styling */
    .stExpander { background: #FFFFFF; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); padding: 16px; margin-bottom: 16px; }
    /* Header styling */
    .title { font-size: 2.5rem; color: #0052CC; font-weight: 600; margin-bottom: 24px; }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("<div class='title'>AI STD Generator</div>", unsafe_allow_html=True)

# Sidebar inputs
st.sidebar.header("Input Specifications")
feature_name = st.sidebar.text_input("Feature Name", placeholder="Enter feature name...", key="feature_name")
characterization = st.sidebar.text_area("Characterization (spec text)", height=200, placeholder="Paste specification here...", key="characterization")
upload_file = st.sidebar.file_uploader("Or upload .txt file", type=["txt"], key="upload_file")

# OpenAI Configuration
st.sidebar.subheader("OpenAI Configuration")
model = st.sidebar.selectbox("Select Model", ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"], index=0)
col1, col2 = st.sidebar.columns(2)
with col1:
    generate = st.button("Generate STD")
with col2:
    download = st.button("Download CSV")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Session state for tests
if 'tests' not in st.session_state:
    st.session_state.tests = []

# Generate test cases
if generate:
    spec_text = upload_file.getvalue().decode('utf-8') if upload_file else characterization
    if not feature_name or not spec_text:
        st.error("Please provide both Feature Name and specification text.")
    else:
        prompt = (
            f"Generate test cases in JSON array format for Testmo import. "
            f"Feature: {feature_name}\nSpecification:\n{spec_text}\n"
            "Each object: title, preconditions, severity, steps (array), expected, tags (array)."
        )
        with st.spinner("Generating test cases..."):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a test case generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
        raw = response.choices[0].message.content
        # Extract JSON array from response
        match = re.search(r"\[.*\]", raw, flags=re.DOTALL)
        json_str = match.group(0) if match else raw
        try:
            tests_json = pd.read_json(io.StringIO(json_str))
            st.session_state.tests = tests_json.to_dict(orient='records')
        except Exception as e:
            st.error(f"Failed to parse LLM response: {e}")
            st.code(raw, language='')

# Display generated tests
if st.session_state.tests:
    st.markdown("### Generated Test Cases")
    # Select All Tests checkbox
    select_all = st.checkbox("Select All Tests", key="select_all")
    selected = []
    for idx, test in enumerate(st.session_state.tests):
        cols = st.columns([1, 9])
        # Hide empty label for accessibility
        checked = cols[0].checkbox(
            label=f"chk_{idx}", key=f"chk_{idx}", value=select_all, label_visibility="hidden"
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
        df.rename(columns={'title':'Title','steps':'Steps','expected':'Expected'}, inplace=True)
        df['Steps'] = df['Steps'].apply(lambda s: '\n'.join(s) if isinstance(s,list) else s)
        df['Folder'] = feature_name
        df['Tags'] = df['tags'].apply(lambda t: ','.join(t) if isinstance(t,list) else t)
        csv_data = df[['Title','Steps','Expected','Folder','Tags']].to_csv(index=False)
        st.download_button(label="Download CSV", data=csv_data, file_name="testmo_import.csv", mime='text/csv')

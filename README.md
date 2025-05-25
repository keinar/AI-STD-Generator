# AI STD Generator

A Streamlit-based application that uses OpenAI's large language model 
to **generate software test cases** (STDs) from feature specifications. 
It formats the generated cases into a CSV compatible with Testmo import.

![image](https://github.com/user-attachments/assets/e6ac8f72-0db3-4ae5-bae7-d130bd9810f1)


## 🔗 Live Demo

[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge)](https://ai-std-generator.onrender.com/)


---

## Key Features

- **Specification Input**: Enter a feature name and detailed specification via text area or upload a `.txt` file.
- **LLM-Powered Generation**: Uses OpenAI’s GPT models (`gpt-4o-mini`, `gpt-4`, `gpt-3.5-turbo`) to produce structured test cases.
- **Interactive UI**: Expander cards for each test case with preconditions, severity, steps, expected results, and tags.
- **Select & Export**: Checkbox selection (including “Select All”) to choose tests and export as `Title, Steps, Expected, Folder, Tags` CSV for Testmo.
- **Theming & Styling**: Custom CSS for a clean, professional look.

---

## Prerequisites

- Python 3.8+ (3.10 recommended)
- Docker (optional, for containerized deployment)
- OpenAI API key (secret key, starts with `sk-`)

---

## Setup & Local Development

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd ai-std-generator
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure your OpenAI key**
   - Create a `.env` file in the project root:
     ```dotenv
     OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXXXXX
     ```
   - The app will load this key automatically via `python-dotenv`.

5. **Run the Streamlit app**
   ```bash
   streamlit run ai_std_generator.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:8501` to interact with the generator.

---

## Docker Deployment

1. **Build the image**
   ```bash
   docker build -t ai-std-generator:latest .
   ```

2. **Run the container**
   ```bash
   docker run -p 8501:8501 --env-file .env ai-std-generator:latest
   ```

3. **Access the app**
   Visit `http://localhost:8501` in your browser.

---

## Project Structure

```
ai-std-generator/
├── .dockerignore       # Files and dirs to exclude from Docker build
├── .env                # Environment variables (OpenAI API key)
├── ai_std_generator.py # Main Streamlit application
├── Dockerfile          # Docker build configuration
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation (this file)
```

---

## Customization & Styling

- **Models**: Change the default or add more GPT variants in the sidebar select box.
- **CSS**: Modify the `<style>` block in `ai_std_generator.py` for branding or theme adjustments.
- **Output Template**: Adapt the CSV columns or mapping logic in the code to fit other test management systems.

---

## Troubleshooting

- **401 Authentication Error**: Ensure `OPENAI_API_KEY` in your `.env` is correct (secret key, not project ID).
- **Parsing Errors**: If the LLM response doesn’t return valid JSON, check the raw output displayed under the generation error for clues.
- **Port Conflicts**: Default Streamlit uses port 8501; change via `--server.port` CLI flag or env var.

---

## License

This project is released under the [MIT License](LICENSE). Feel free to use and adapt.

---

**Enjoy generating your test cases!**

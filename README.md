# Wevently Streamlit Chatbot

This project is a Streamlit application designed to provide intelligent assistance for event management through natural language processing and machine learning techniques. It leverages various NLP models and a Neo4j database to analyze user queries and provide relevant solutions.

## Project Structure

```
wevently-streamlit
├── src
│   ├── streamlit_app.py       # Main entry point for the Streamlit application
│   └── langchain.py           # Logic for NLP, sentiment analysis, and database interaction
├── requirements.txt            # Python dependencies for the project
├── .streamlit
│   └── config.toml            # Configuration settings for the Streamlit application
├── .env                      # environment variables for ollama and huggingface
├── .gitignore                  # Files and directories to be ignored by Git
├── tests
│   └── test_app.py            # Test cases for the Streamlit application
└── README.md                   # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <https://github.com/crosaless/wevently-streamlit.git>
   cd wevently-streamlit
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - fill the `.env` file with the necessary values.

5. **Run the Streamlit application:**
   ```bash
   streamlit run src/streamlit_app.py
   ```

## Usage

- Open your web browser and navigate to `http://localhost:8501` to access the Wevently Chatbot.
- Select your role and enter your query to receive assistance.

## Testing

- To run the tests, execute the following command:
  ```bash
  pytest tests/test_app.py
  ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
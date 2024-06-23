# OSINT Tool for Email, Phone Number, Name, and Image Lookup

This repository contains an OSINT (Open Source Intelligence) tool that performs reverse lookups on emails, phone numbers, names, and images. It generates summaries and analyses using GPT-4 and searches archived web pages using the Wayback Machine.

## Features

- Reverse lookup for email addresses, phone numbers, and names
- Email breach check using Have I Been Pwned API
- Named entity extraction using spaCy
- Sentiment analysis using TextBlob
- Text summarization and analysis using GPT-4
- Image recognition using Google Cloud Vision
- Web page archiving lookup using Wayback Machine
- Visualization of relationships with NetworkX and Matplotlib
- Task queue management with Redis and RQ
- Integration with Elasticsearch and Neo4j

## Prerequisites

- Python 3.x
- Redis server
- API keys for OpenAI, Pipl, FullContact, Have I Been Pwned, Google Cloud Vision

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/osint_tool.git
    cd osint_tool
    ```

2. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Download the spaCy language model:
    ```bash
    python -m spacy download en_core_web_sm
    ```

5. Configure your API keys in `osint_tools.py`:
    ```python
    openai.api_key = 'YOUR_OPENAI_API_KEY'
    ```

## Running the Application

1. Start the Redis server:
    ```bash
    redis-server
    ```

2. Start an RQ worker:
    ```bash
    rq worker
    ```

3. Run the Flask application:
    ```bash
    python app.py
    ```

4. Open your browser and navigate to:
    - Reverse Lookup: [http://127.0.0.1:5000/reverse_lookup](http://127.0.0.1:5000/reverse_lookup)
    - Name Search: [http://127.0.0.1:5000/search_name](http://127.0.0.1:5000/search_name)
    - Image Search: [http://127.0.0.1:5000/search_image](http://127.0.0.1:5000/search_image)
    - Email Search: [http://127.0.0.1:5000/search_email](http://127.0.0.1:5000/search_email)
    - Generate Summary: [http://127.0.0.1:5000/generate_summary](http://127.0.0.1:5000/generate_summary)
    - Generate Analysis: [http://127.0.0.1:5000/generate_analysis](http://127.0.0.1:5000/generate_analysis)
    - Search Wayback Machine: [http://127.0.0.1:5000/search_wayback](http://127.0.0.1:5000/search_wayback)

## Usage

### Reverse Lookup

1. Navigate to [http://127.0.0.1:5000/reverse_lookup](http://127.0.0.1:5000/reverse_lookup)
2. Enter an email address or phone number.
3. Click "Search" to perform a reverse lookup using Pipl, FullContact, and Have I Been Pwned APIs.

### Name Search

1. Navigate to [http://127.0.0.1:5000/search_name](http://127.0.0.1:5000/search_name)
2. Enter a name.
3. Click "Search" to perform a name lookup using Pipl and FullContact APIs.

### Image Search

1. Navigate to [http://127.0.0.1:5000/search_image](http://127.0.0.1:5000/search_image)
2. Upload an image file.
3. Click "Search" to perform image recognition using Google Cloud Vision API.

### Email Search

1. Navigate to [http://127.0.0.1:5000/search_email](http://127.0.0.1:5000/search_email)
2. Enter an email address.
3. Click "Search" to enqueue a scraping task for the email.
4. Check the results page for extracted entities, sentiment analysis, summaries, and relationship graphs.

### Generate Summary

1. Submit text to [http://127.0.0.1:5000/generate_summary](http://127.0.0.1:5000/generate_summary) to get a summary using GPT-4.

### Generate Analysis

1. Submit data to [http://127.0.0.1:5000/generate_analysis](http://127.0.0.1:5000/generate_analysis) to get an analysis or summary using GPT-4.

### Search Wayback Machine

1. Submit a URL to [http://127.0.0.1:5000/search_wayback](http://127.0.0.1:5000/search_wayback) to find archived versions of the page.

## Example Configuration in `app.py`

See the provided code examples in this repository for how to configure the routes and functionality.

## Contributing

If you want to contribute to this project, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.

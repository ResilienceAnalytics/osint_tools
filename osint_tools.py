import openai
import requests
import spacy
from textblob import TextBlob
from googletrans import Translator
from elasticsearch import Elasticsearch
from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt
from google.cloud import vision
from google.cloud.vision_v1 import types
from PIL import Image
import argparse

# Configure OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Initialize models and APIs
nlp = spacy.load("en_core_web_sm")

def reverse_lookup_pipl(name, api_key):
    try:
        url = f"https://api.pipl.com/search/?key={api_key}&name={name}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during Pipl API request: {e}")
        return None

def reverse_lookup_fullcontact(name, api_key):
    try:
        headers = {
            'Authorization': f'Bearer {api_key}'
        }
        url = f"https://api.fullcontact.com/v3/person.enrich?name={name}"
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during FullContact API request: {e}")
        return None

def recognize_image(image_path):
    try:
        client = vision.ImageAnnotatorClient()
        with open(image_path, 'rb') as image_file:
            content = image_file.read()
        image = types.Image(content=content)
        response = client.annotate_image({
            'image': image,
            'features': [{'type': vision.enums.Feature.Type.TEXT_DETECTION},
                         {'type': vision.enums.Feature.Type.LABEL_DETECTION}],
        })
        return response
    except Exception as e:
        print(f"Error during image recognition: {e}")
        return None

def check_haveibeenpwned(email, api_key):
    try:
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {
            'hibp-api-key': api_key,
            'User-Agent': 'Python Script'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f"Error during Have I Been Pwned API request: {e}")
        return None

def extract_entities(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = {
        'polarity': blob.sentiment.polarity,
        'subjectivity': blob.sentiment.subjectivity
    }
    return sentiment

def generate_summary(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Summarize the following text."},
                {"role": "user", "content": text}
            ]
        )
        summary = response['choices'][0]['message']['content'].strip()
        return summary
    except openai.error.OpenAIError as e:
        print(f"Error during summary generation: {e}")
        return None

def translate_text(text, dest='en'):
    translator = Translator()
    translated = translator.translate(text, dest=dest)
    return translated.text

def create_relationship_graph(data):
    G = nx.Graph()

    for record in data:
        email = record['_source']['email']
        page_url = record['_source']['page_url']
        entities = record['_source'].get('entities', [])

        G.add_node(email, type='email')
        G.add_node(page_url, type='url')

        G.add_edge(email, page_url)

        for entity, label in entities:
            G.add_node(entity, type=label)
            G.add_edge(page_url, entity)
    
    return G

def visualize_graph(G, filename='static/graph.png'):
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 12))
    nx.draw(G, pos, with_labels=True, node_size=5000, node_color='skyblue', font_size=10, font_color='black', font_weight='bold')
    plt.savefig(filename)
    plt.close()

class Neo4jClient:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_relationship(self, email, url, entities):
        with self.driver.session() as session:
            session.write_transaction(self._create_and_return_relationship, email, url, entities)

    @staticmethod
    def _create_and_return_relationship(tx, email, url, entities):
        query = (
            "MERGE (e:Email {address: $email}) "
            "MERGE (u:URL {address: $url}) "
            "MERGE (e)-[:REGISTERED_AT]->(u) "
        )
        for entity, label in entities:
            query += (
                f"MERGE (ent:{label} {{name: $entity}}) "
                f"MERGE (u)-[:MENTIONS]->(ent) "
            )
        tx.run(query, email=email, url=url, entities=entities)

def search_wayback_machine(url):
    try:
        api_url = f"http://archive.org/wayback/available?url={url}"
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during Wayback Machine search: {e}")
        return None

def generate_summary_or_analysis(data):
    prompt = "Analyze the following data and provide a summary:\n\n"
    for key, value in data.items():
        prompt += f"{key}: {value}\n"
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Analyze the following data and provide a summary."},
                {"role": "user", "content": prompt}
            ]
        )
        summary_or_analysis = response['choices'][0]['message']['content'].strip()
        return summary_or_analysis
    except openai.error.OpenAIError as e:
        print(f"Error during summary or analysis generation: {e}")
        return None

def generate_osint_description(image_path, prompt_type):
    prompts = {
        "person": f"You are HAL-GPT, an advanced language model developed by OpenAI, based on the GPT-4 architecture, specializing in OSINT. Analyze the given image and identify and describe in detail the people present. Mention physical characteristics, clothing, accessories, and any distinctive features that could aid in identification. Additionally, specify the context of the scene if possible.",
        "scene": f"You are HAL-GPT, an advanced language model developed by OpenAI, based on the GPT-4 architecture, with a focus on OSINT and crisis management. Analyze the given image in detail. Describe the environment, objects present, and ongoing activities. Mention any elements that could indicate the location or context of the scene. Include details on weather conditions, time of day, and any indication of the period when the image was taken.",
        "vehicle": f"You are HAL-GPT, an advanced language model developed by OpenAI, based on the GPT-4 architecture, specializing in OSINT and engineering. Describe in detail the vehicles visible in the given image. Include information on makes, models, colors, and distinctive features. If license plates are visible, transcribe the information and provide details on their format and possible origin.",
        "object": f"You are HAL-GPT, an advanced language model developed by OpenAI, based on the GPT-4 architecture, with expertise in OSINT and technology. Examine the given image to identify and describe in detail all visible objects and devices. Mention their possible utility, condition (new, worn, damaged), and any distinctive marks or features. Include hypotheses on the usage of these objects in the context of the scene.",
        "document": f"You are HAL-GPT, an advanced language model developed by OpenAI, based on the GPT-4 architecture, specializing in OSINT and document analysis. Describe in detail all documents, writings, or displays visible in the given image. Transcribe readable text and provide an analysis of its content, format, and possible origin. Mention any seals, logos, or other distinctive elements."
    }

    prompt = prompts.get(prompt_type, "Invalid prompt type")

    if prompt == "Invalid prompt type":
        print("Invalid prompt type provided.")
        return None

    image_context = "Image provided for analysis."
    final_prompt = f"{prompt} Image Context: {image_context}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Generate a detailed OSINT description."},
                {"role": "user", "content": final_prompt}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.error.OpenAIError as e:
        print(f"Error during OSINT description generation: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Generate OSINT description from an image.")
    parser.add_argument('image_path', type=str, help="Path to the image file")
    parser.add_argument('prompt_type', type=str, choices=['person', 'scene', 'vehicle', 'object', 'document'], help="Type of OSINT analysis to be performed")

    args = parser.parse_args()

    description = generate_osint_description(args.image_path, args.prompt_type)
    if description:
        print(description)
    else:
        print("Failed to generate OSINT description.")

if __name__ == '__main__':
    main()

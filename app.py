from flask import Flask, request, render_template, url_for
from elasticsearch import Elasticsearch
from osint_tools import (
    reverse_lookup_pipl,
    reverse_lookup_fullcontact,
    check_haveibeenpwned,
    create_relationship_graph,
    visualize_graph,
    generate_summary,
    generate_summary_or_analysis,  
    search_wayback_machine,
    recognize_image
)
from tasks import enqueue_scraping_task

# Initialize Flask app
app = Flask(__name__)

# Initialize Elasticsearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# API keys (replace with your actual keys)
api_key_pipl = 'YOUR_PIPL_API_KEY'
api_key_fullcontact = 'YOUR_FULLCONTACT_API_KEY'
api_key_hibp = 'YOUR_HAVEIBEENPWNED_API_KEY'
webhook_url = 'YOUR_WEBHOOK_URL'
openai_api_key = 'YOUR_OPENAI_API_KEY'

@app.route('/reverse_lookup', methods=['GET', 'POST'])
def reverse_lookup():
    """
    Perform a reverse lookup for an email or phone number and display the results.
    """
    if request.method == 'POST':
        email_or_phone = request.form['email_or_phone']
        
        pipl_results = reverse_lookup_pipl(email_or_phone, api_key_pipl)
        fullcontact_results = reverse_lookup_fullcontact(email_or_phone, api_key_fullcontact)
        hibp_results = check_haveibeenpwned(email_or_phone, api_key_hibp) if "@" in email_or_phone else None
        
        return render_template('reverse_lookup_results.html', pipl_results=pipl_results, fullcontact_results=fullcontact_results, hibp_results=hibp_results)
    return render_template('reverse_lookup.html')

@app.route('/search_name', methods=['GET', 'POST'])
def search_name():
    """
    Search for information based on a name and display the results.
    """
    if request.method == 'POST':
        name = request.form['name']
        
        pipl_results = reverse_lookup_pipl(name, api_key_pipl)
        fullcontact_results = reverse_lookup_fullcontact(name, api_key_fullcontact)
        
        return render_template('name_lookup_results.html', pipl_results=pipl_results, fullcontact_results=fullcontact_results)
    return render_template('search_name.html')

@app.route('/search_image', methods=['GET', 'POST'])
def search_image():
    """
    Search for information based on an uploaded image and display the results.
    """
    if request.method == 'POST':
        image = request.files['image']
        image_path = f"static/{image.filename}"
        image.save(image_path)
        
        image_results = recognize_image(image_path)
        
        return render_template('image_lookup_results.html', image_results=image_results)
    return render_template('search_image.html')

@app.route('/search_email', methods=['GET', 'POST'])
def search_email():
    """
    Search for an email and display the results, including relationships and visualizations.
    """
    if request.method == 'POST':
        email = request.form['email']
        
        start_urls = [
            'https://www.linkedin.com',
            'https://www.twitter.com',
            'https://www.facebook.com',
            'https://www.instagram.com',
            'https://www.github.com',
            'https://www.pinterest.com',
            'https://www.reddit.com',
            'https://www.gravatar.com',
            'https://haveibeenpwned.com',
            'https://pipl.com',
            'https://www.fullcontact.com',
            'https://www.spokeo.com',
            'https://www.beenverified.com',
            'https://www.truecaller.com',
            'https://archive.org/web'
        ]
        
        for url in start_urls:
            enqueue_scraping_task(url, email, api_key_hibp, webhook_url)
        
        return render_template('task_submitted.html', email=email)
    return render_template('search_email.html')

@app.route('/search_results', methods=['GET', 'POST'])
def search_results():
    """
    Display the search results for an email, including relationships and visualizations.
    """
    if request.method == 'POST':
        email = request.form['email']
        
        search_results = es.search(index='email_occurrences', body={
            'query': {
                'match': {
                    'email': email
                }
            }
        })

        breaches = check_haveibeenpwned(email, api_key_hibp)
        G = create_relationship_graph(search_results['hits']['hits'])
        visualize_graph(G)
        
        return render_template('search_email_results.html', results=search_results['hits']['hits'], breaches=breaches, graph_image=url_for('static', filename='graph.png'))
    return render_template('search_email.html')

@app.route('/generate_summary', methods=['POST'])
def generate_summary_route():
    """
    Generate a summary for the provided text using GPT-4.
    """
    text = request.form['text']
    summary = generate_summary(text)
    return render_template('summary_results.html', summary=summary)

@app.route('/generate_analysis', methods=['POST'])
def generate_analysis_route():
    """
    Generate an analysis or summary for the provided data using GPT-4.
    """
    data = request.form.to_dict()
    analysis = generate_summary_or_analysis(data)
    return render_template('analysis_results.html', analysis=analysis)

@app.route('/search_wayback', methods=['POST'])
def search_wayback_route():
    """
    Search the Wayback Machine for archived versions of a URL.
    """
    url = request.form['url']
    wayback_results = search_wayback_machine(url)
    return render_template('wayback_results.html', wayback_results=wayback_results)

if __name__ == '__main__':
    app.run(debug=True)

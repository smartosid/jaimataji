from flask import Flask, request, render_template
from markupsafe import escape as html_escape
from datetime import datetime, timedelta
from pymongo.mongo_client import MongoClient
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Update the URI with your MongoDB Atlas connection string with TLS settings
uri = "mongodb+srv://vs2379:siddhu@test1.e8e9uvv.mongodb.net/?retryWrites=true&w=majority&appName=test1&tls=true&tlsAllowInvalidCertificates=true"

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    app.logger.info("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    app.logger.error(f"Failed to connect to MongoDB: {e}")

# Access the database from the client
db = client['final']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        last_modified_date = request.form.get('last_modified_date')

        try:
            last_modified_date = datetime.strptime(last_modified_date, '%Y-%m-%d')
        except ValueError:
            app.logger.error("Invalid date format provided")
            return 'Invalid date format. Please enter the date in YYYY-MM-DD format.'

        try:
            # Use count_documents to get the count of documents
            document_count = db.finall.count_documents({'last_modified_date': {'$gte': last_modified_date, '$lt': last_modified_date + timedelta(days=1)}})
            documents = db.finall.find({'last_modified_date': {'$gte': last_modified_date, '$lt': last_modified_date + timedelta(days=1)}})
            
            if document_count == 0:
                return render_template('index.html', html='<p>No data found for the given date.</p>')
            else:
                html = "<h1>DRDO DATABASE</h1>"
                for doc in documents:
                    html += f"<h2>{html_escape(doc['file_name'])}</h2>"
                    html += f"<p>File Path: {html_escape(doc['file_path'])}</p>"
                    html += f"<pre>{html_escape(doc['content'])}</pre>"
                    html += f"<p>Upload Date: {doc['upload_date'].strftime('%Y-%m-%d')}</p>"
                    html += f"<p>Last Modified Date: {doc['last_modified_date'].strftime('%Y-%m-%d')}</p>"
                    html += "<hr>"
                return render_template('index.html', html=html)
        except Exception as e:
            app.logger.error(f"Error querying the database: {e}")
            return 'An error occurred while querying the database. Please try again later.'
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run()



from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Ensure the database directory exists
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'db/sqlLite/file_metadata.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_PATH}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Database Model
class FileMetadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)

# Create Tables Before Running the App
with app.app_context():
    db.create_all()

    # Sample Data Insertion (Fix: Use app context)
    def insert_sample_data():
        if not FileMetadata.query.first():  # Check if data exists
            sample_files = [
                FileMetadata(filename="report.pdf", size=2048),
                FileMetadata(filename="data.xlsx", size=5120)
            ]
            db.session.add_all(sample_files)
            db.session.commit()

    insert_sample_data()  # Run inside app context

# Define Route for HTML Page
@app.route('/')
def index():
    files = FileMetadata.query.all()
    return render_template('index.html', files=files)

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)

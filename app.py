from flask import Flask
from api.ollama import ollama_endpoint

app = Flask(__name__)
app.register_blueprint(ollama_endpoint)

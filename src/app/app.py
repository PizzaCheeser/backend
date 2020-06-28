from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app, defaults_prefix="pizza")
CORS(app)

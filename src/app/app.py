import logging

from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from config import load_config


sentry_sdk.init(
    integrations=[FlaskIntegration()]
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
load_config(app)
metrics = PrometheusMetrics(app, defaults_prefix="pizza")
CORS(app)


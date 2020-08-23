from flask import Flask
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from config import SENTRY_DSN

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[FlaskIntegration()]
)

app = Flask(__name__)
metrics = PrometheusMetrics(app, defaults_prefix="pizza")
CORS(app)


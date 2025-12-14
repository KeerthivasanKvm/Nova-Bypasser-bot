import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from web.routes import setup_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.FLASK_SECRET_KEY
CORS(app)

# Setup routes
setup_routes(app)

# Health check endpoint
@app.route('/')
def index():
    return jsonify({
        'status': 'online',
        'service': 'Link Bypasser Bot',
        'version': '2.0.0',
        'endpoints': {
            'health': '/health',
            'webhook': '/webhook',
            'api': '/api/bypass'
        }
    }), 200

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': os.environ.get('HEROKU_RELEASE_CREATED_AT', 'N/A')
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = Config.PORT
    logger.info(f"Starting Flask server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

import logging
from flask import request, jsonify, render_template_string
from bypasser.core import LinkBypasser

logger = logging.getLogger(__name__)

def setup_routes(app):
    """Setup Flask routes"""
    
    bypasser = LinkBypasser()
    
    @app.route('/api/bypass', methods=['POST'])
    async def api_bypass():
        """API endpoint for bypassing links"""
        try:
            data = request.get_json()
            
            if not data or 'url' not in data:
                return jsonify({
                    'success': False,
                    'error': 'URL is required'
                }), 400
            
            url = data['url']
            
            # Perform bypass
            result = await bypasser.bypass(url)
            
            return jsonify(result), 200 if result['success'] else 400
            
        except Exception as e:
            logger.error(f"API bypass error: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/supported-sites', methods=['GET'])
    def api_supported_sites():
        """Get list of supported sites"""
        try:
            sites = bypasser.get_supported_sites()
            return jsonify({
                'success': True,
                'sites': sites,
                'count': len(sites)
            }), 200
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/webhook', methods=['POST'])
    def webhook():
        """Webhook endpoint for Telegram"""
        # This can be used for webhook mode instead of polling
        return jsonify({'status': 'ok'}), 200
    
    @app.route('/docs')
    def api_docs():
        """API documentation page"""
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Link Bypasser Bot - API Documentation</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 50px auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .container {
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    border-bottom: 3px solid #007bff;
                    padding-bottom: 10px;
                }
                h2 {
                    color: #555;
                    margin-top: 30px;
                }
                .endpoint {
                    background: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #007bff;
                    margin: 20px 0;
                }
                code {
                    background: #e9ecef;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }
                .method {
                    display: inline-block;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-weight: bold;
                    margin-right: 10px;
                }
                .post {
                    background: #28a745;
                    color: white;
                }
                .get {
                    background: #17a2b8;
                    color: white;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔗 Link Bypasser Bot API</h1>
                <p>Welcome to the Link Bypasser Bot API documentation.</p>
                
                <h2>Endpoints</h2>
                
                <div class="endpoint">
                    <span class="method post">POST</span>
                    <strong>/api/bypass</strong>
                    <p>Bypass a link and get the direct URL.</p>
                    <h4>Request Body:</h4>
                    <pre><code>{
    "url": "https://example.com/short-link"
}</code></pre>
                    <h4>Response:</h4>
                    <pre><code>{
    "success": true,
    "bypassed_url": "https://direct-link.com/file",
    "type": "shortener"
}</code></pre>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/api/supported-sites</strong>
                    <p>Get list of all supported sites.</p>
                    <h4>Response:</h4>
                    <pre><code>{
    "success": true,
    "sites": ["gdtot.com", "sharer.pw", ...],
    "count": 25
}</code></pre>
                </div>
                
                <div class="endpoint">
                    <span class="method get">GET</span>
                    <strong>/health</strong>
                    <p>Health check endpoint.</p>
                </div>
                
                <h2>Rate Limiting</h2>
                <p>API endpoints are rate-limited. Please don't exceed:</p>
                <ul>
                    <li>Free users: 10 requests per day</li>
                    <li>Premium users: Unlimited</li>
                </ul>
                
                <h2>Support</h2>
                <p>For support, contact <a href="https://t.me/YourUsername">@YourUsername</a></p>
            </div>
        </body>
        </html>
        '''
        return render_template_string(html)

    logger.info("Flask routes registered successfully")

# مثال مبسط لخادم الويب باستخدام Flask
from flask import Flask, jsonify, request, render_template
import threading

class WebServer:
    def __init__(self, autogpt_system, host="127.0.0.1", port=5000):
        self.autogpt = autogpt_system
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self._setup_routes()
        
    def _setup_routes(self):
        @self.app.route('/')
        def home():
            return render_template('index.html')
            
        @self.app.route('/api/agents', methods=['GET'])
        def list_agents():
            agents = self.autogpt.list_agents()
            return jsonify(agents)
            
        @self.app.route('/api/agents', methods=['POST'])
        def create_agent():
            data = request.json
            agent = self.autogpt.create_agent(
                name=data['name'],
                goal=data['goal'],
                tools=data.get('tools')
            )
            return jsonify({'id': agent.id, 'name': agent.name})
            
        # المزيد من المسارات...
        
    def start(self, debug=False):
        """بدء تشغيل خادم الويب"""
        if debug:
            self.app.run(host=self.host, port=self.port, debug=True)
        else:
            # تشغيل في خيط منفصل
            thread = threading.Thread(target=self.app.run, kwargs={
                'host': self.host,
                'port': self.port
            })
            thread.daemon = True
            thread.start()
            return thread
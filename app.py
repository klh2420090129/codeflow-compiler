from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from compiler.pipeline import compile_source
import os

app = Flask(__name__, 
            template_folder=os.path.abspath('frontend/templates'),
            static_folder=os.path.abspath('frontend/static'))
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "CodeFlow Compiler"
    })

@app.route('/api/compile', methods=['POST'])
def compile_code():
    data = request.get_json()
    if not data or 'source' not in data:
        return jsonify({"success": False, "error": "No source provided"}), 400
        
    source = data['source']
    execute = data.get('execute', True)
    trace = data.get('trace', False)
    language = data.get('language', 'minilang')
    
    result = compile_source(source, execute=execute, trace=trace, language=language)
    return jsonify(result.to_dict())

if __name__ == "__main__":
    app.run(debug=True, port=5000)

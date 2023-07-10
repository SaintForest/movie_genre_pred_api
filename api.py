from flask import Flask, request, jsonify, render_template, g
from infer import load_model, main


app = Flask(__name__)

app.config['MODEL'] = load_model()  # Load the model and store it in the app configuration

def get_model():
    return app.config['MODEL']


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        description = request.form.get('description')
        if description is not None:
            description = description.strip()
        result = analyze_data(description)
        return render_template('index.html', result=result)

    return render_template('index.html')



@app.route('/analyze', methods=['POST'])

def analyze_data():
    description = request.form.get('description')
    if description is not None:
        description = description.strip()
    if description is None:
        return jsonify({'error': 'Missing required field: description'}), 400


    if len(description) < 10:
        return jsonify({'error': 'Description argument is less than 10'}), 400

    if len(description) > 1000:
        return jsonify({'error': 'Description argument is too large'}), 400

    if any(not c.isalnum() for c in description.split()):
        return jsonify({'error': 'Title and description have non-alphanumeric characters'}), 400
    
    if description is None:
        return jsonify({'error': 'Missing required field: description'}), 400
    try:
        
        model = get_model()  # Retrieve the loaded model from the application context
        
        result= main(model, ["--description", description])
        
        if len(result)>0:
            return str(result)
        else:
            return "No suitable genre found for the given description"

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 404 Not Found
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Endpoint not found. Please use a valid endpoint.'}), 404

# 400 Bad Request
@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({'error': 'Bad request. Please check your request data.'}), 400

# 401 Unauthorized
@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({'error': 'Unauthorized. Please provide valid credentials.'}), 401

# 403 Forbidden
@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({'error': 'Forbidden. You do not have permission to access this resource.'}), 403

# 500 Internal Server Error
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error. Please try again later.'}), 500

# 503 Service Unavailable
@app.errorhandler(503)
def service_unavailable_error(error):
    return jsonify({'error': 'Service temporarily unavailable. Please try again later.'}), 503

# 405 Method Not Allowed
@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({'error': 'Method not allowed. Please use a valid HTTP method.'}), 405

@app.route('/analyze', methods=['GET'])
def handle_get_request():
    return jsonify({'error': 'Method not allowed. Please use a POST request.'}), 405


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True,port=8000)







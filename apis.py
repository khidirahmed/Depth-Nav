from openai import OpenAI
from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
import os

# Load API key from environment variable
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No OpenAI API key found. Please set the OPENAI_API_KEY environment variable.")

chat_client = OpenAI(api_key=api_key)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


prompt = 'You are a helpful AI bot named "Deb" who will help people find the specific business or service they are looking for and you will offer a business recommendation. First off you will start by asking what day of the week is it, the time, location, and what type of service or restaurant they are looking for. Then you will return some options from the yelp dataset. After if there is information on menus, you can ask if they are looking for any specific meal or service. Let the reviews guide you to a specific service or restaurant. After the person chooses, tell them they made a good choice and then maybe send a positive review from the dataset. '

@app.route('/')
def index():
    return render_template('trial.html')

@app.route('/', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message')

    if 'conversation' not in session:
        session['conversation'] = [{"role": "system", "content": prompt}]

    session['conversation'].append({"role": "user", "content": message})

    response = chat_client.chat.completions.create(
        model='gpt-4o-mini',
        messages=session['conversation'],
        max_tokens=150  
    )

    assistant_message = response.choices[0].message.content.strip()
    session['conversation'].append({"role": "assistant", "content": assistant_message})

    if len(session['conversation']) > 10:
        session['conversation'] = session['conversation'][-10:]
    
    session.modified = True  
    
    return jsonify({'reply': assistant_message})

@app.route('/reset', methods=['POST'])
def reset_conversation():
    session['conversation'] = [{"role": "system", "content": prompt}]
    session.modified = True
    return jsonify({'message': 'Conversation reset successfully'})


'''
--- Below this point is the google maps API integration ---
'''





if __name__ == '__main__':
    app.run(port=5000, debug=False)

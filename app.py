import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("MYFUCKING_API_KEY")
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

def get_decision_factors(question):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a wise decision-making assistant. For any decision question, identify exactly 5 key factors that matter most to the person. Make each factor conversational and personal, like 'Your Daily Time Availability' or 'Your Living Space Setup'. For each factor, provide two realistic options that describe different preferences or situations. Return ONLY valid JSON in this format: {\"factors\": [{\"name\": \"Your Factor Name\", \"options\": [\"Option A description\", \"Option B description\"]}]}. Make it feel like a friendly conversation, not a formal analysis."
            },
            {"role": "user", "content": f"Decision: {question}"}
        ]
    }
    try:
        print(f"Making API call for question: {question}")
        response = requests.post(API_URL, json=data, headers=headers, timeout=30)
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"API Error: {response.status_code} - {response.text}")
            return '{"factors": [{"name": "Your Time Availability", "options": ["I have several hours daily for active involvement", "I prefer minimal time commitment"]}, {"name": "Your Living Space", "options": ["I have plenty of space and outdoor access", "I live in a smaller space with limited options"]}, {"name": "Your Lifestyle Preferences", "options": ["I want an active companion for activities", "I prefer a more independent companion"]}, {"name": "Your Experience Level", "options": ["I\'m comfortable with training and challenges", "I prefer something naturally well-behaved"]}, {"name": "Your Schedule Flexibility", "options": ["I\'m usually home and rarely travel", "I travel sometimes and need flexibility"]}]}'
        
        result = response.json()
        print(f"API Response: {result}")
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print(f"AI Response Content: {content}")
            
            # Clean markdown formatting
            content = content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
            content = content.strip()
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            # Try to parse as JSON
            try:
                import json
                json.loads(content)  # Validate JSON
                print(f"Valid JSON found: {content}")
                return content
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return '{"factors": [{"name": "Your Time Availability", "options": ["I have several hours daily for active involvement", "I prefer minimal time commitment"]}, {"name": "Your Living Space", "options": ["I have plenty of space and outdoor access", "I live in a smaller space with limited options"]}, {"name": "Your Lifestyle Preferences", "options": ["I want an active companion for activities", "I prefer a more independent companion"]}, {"name": "Your Experience Level", "options": ["I\'m comfortable with training and challenges", "I prefer something naturally well-behaved"]}, {"name": "Your Schedule Flexibility", "options": ["I\'m usually home and rarely travel", "I travel sometimes and need flexibility"]}]}'
        else:
            print(f"No choices in response: {result}")
            return '{"factors": [{"name": "Your Time Availability", "options": ["I have several hours daily for active involvement", "I prefer minimal time commitment"]}, {"name": "Your Living Space", "options": ["I have plenty of space and outdoor access", "I live in a smaller space with limited options"]}, {"name": "Your Lifestyle Preferences", "options": ["I want an active companion for activities", "I prefer a more independent companion"]}, {"name": "Your Experience Level", "options": ["I\'m comfortable with training and challenges", "I prefer something naturally well-behaved"]}, {"name": "Your Schedule Flexibility", "options": ["I\'m usually home and rarely travel", "I travel sometimes and need flexibility"]}]}'
    except Exception as e:
        print(f"API Error: {e}")
        return '{"factors": [{"name": "Your Time Availability", "options": ["I have several hours daily for active involvement", "I prefer minimal time commitment"]}, {"name": "Your Living Space", "options": ["I have plenty of space and outdoor access", "I live in a smaller space with limited options"]}, {"name": "Your Lifestyle Preferences", "options": ["I want an active companion for activities", "I prefer a more independent companion"]}, {"name": "Your Experience Level", "options": ["I\'m comfortable with training and challenges", "I prefer something naturally well-behaved"]}, {"name": "Your Schedule Flexibility", "options": ["I\'m usually home and rarely travel", "I travel sometimes and need flexibility"]}]}'

def get_recommendation(question, selections):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a wise, friendly advisor. Based on the person's choices, give a clear, conversational recommendation. Start with a brief recommendation (like 'Adopt a cat' or 'Choose option A'), then explain why this fits their situation in 2-3 sentences. Be encouraging and understanding, like talking to a friend. Keep it under 100 words total."
            },
            {"role": "user", "content": f"Decision: {question}. Choices: {selections}"}
        ]
    }
    try:
        response = requests.post(API_URL, json=data, headers=headers, timeout=30)
        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
    except:
        return "Based on your choices, I'd recommend considering what feels right for your situation. Trust your instincts!"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_factors', methods=['POST'])
def get_factors():
    question = request.json.get('question')
    factors = get_decision_factors(question)
    return jsonify({'factors': factors})

@app.route('/get_recommendation', methods=['POST'])
def get_recommendation_route():
    data = request.json
    recommendation = get_recommendation(data['question'], data['selections'])
    return jsonify({'recommendation': recommendation})

@app.route('/recents')
def recents():
    return render_template('recents.html')

if __name__ == '__main__':
    app.run(debug=True)
import google.generativeai as genai
api='api'
genai.configure(api_key=api)

# Load the Gemini model
model = genai.GenerativeModel('models/gemma-3-12b-it')
def remove_asterisks(text):
    return text.replace('*', '')

def generate_gemini_response(prompt):
    
    # Sends a prompt to Gemini and returns the response.

    if not prompt:
        return "Error: Empty prompt provided."
    try:
        
        response = model.generate_content(prompt)
        clean_response = remove_asterisks(response.text)

        return clean_response
    except Exception as e:
        return "Error:"

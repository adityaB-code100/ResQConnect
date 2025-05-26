import google.generativeai as genai

# Configure Gemini with your API key
api='AIzaSyBEcCPyPPlo5r9O09ftFdYYdk9V6TewDZo'
genai.configure(api_key=api)

# Load the Gemini model
model = genai.GenerativeModel('models/gemma-3-12b-it')
def remove_asterisks(text):
    return text.replace('*', '')

def generate_gemini_response(prompt):
    """
    Sends a prompt to Gemini and returns the response.
    """
    if not prompt:
        return "Error: Empty prompt provided."
    try:
        
        response = model.generate_content(prompt)
        clean_response = remove_asterisks(response.text)

        return clean_response
    except Exception as e:
        return f"Error: {str(e)}"

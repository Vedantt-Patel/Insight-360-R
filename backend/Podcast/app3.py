import os
import re
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

def generate_introduction():
    """Generate introduction using Groq API."""
    # Get API key from environment variable
    api_key = os.getenv('GROQ_API_KEY')
    
    # Validate API key
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")

    # Initialize Groq client
    client = Groq(api_key=api_key)

    # Prompt for introduction generation
    prompt = """Create a podcast introduction between Alex (host) and Martin (guest) discussing a research paper on system design generation and evaluation. 
    Alex should introduce himself, Martin, and briefly mention the podcast topic. Avoid including the phrase "Here is a potential podcast introduction."

    Dialogue Format:
    Alex: [Introduction of himself and the guest, Martin, and the podcast topic]
    Martin: [Martin gives a short greeting]"""

    try:
        # Generate introduction using Groq API
        chat_completion = client.chat.completions.create(
            messages=[ 
                {"role": "system", "content": "You are creating an introduction for a podcast between Alex (host) and Martin (guest)."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192"
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating introduction: {str(e)}"

def refine_dialog(input_file='final.txt', output_file='final1.txt'):
    """Refine the dialog content by removing unnecessary phrases and only saving the actual dialog."""
    # Open the input file (final.txt) and read the content
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remove unwanted introductory lines and any lines before the actual dialog
    refined_content = re.sub(r"(Here is the dialog(?: between Alex and Martin)?:?\s*)", "", content)
    refined_content = re.sub(r"(Here is a potential podcast introduction:.*?Alex:)", "", refined_content, flags=re.DOTALL)
    
    # Keep only dialog lines: Ensure content only contains 'Alex' and 'Martin' dialogue format
    refined_content = re.sub(r"^(?!Alex:|Martin:).*\n", "", refined_content, flags=re.MULTILINE)

    # Strip leading/trailing whitespace
    refined_content = refined_content.strip()

    # If content is empty after cleaning, return early
    if not refined_content:
        print("No valid dialog content found.")
        return

    # Generate introduction
    introduction = generate_introduction()

    # Prepend the introduction to the dialog content, only if dialog exists
    final_content = f"{introduction}\n\n{refined_content}"

    # Save the refined dialog with introduction into final1.txt
    with open(output_file, 'w', encoding='utf-8') as output_file:
        output_file.write(final_content)

    print(f"Refined dialog with introduction saved to {output_file.name}")

    # Delete the original final.txt after saving
    if os.path.exists(input_file):
        os.remove(input_file)
        print(f"Deleted {input_file}")

def clean_non_dialog_lines(file_path='final1.txt'):
    """Ensure all lines in final1.txt start with 'Alex:' or 'Martin:'. Remove any non-dialog lines."""
    if not os.path.exists(file_path):
        print(f"{file_path} not found.")
        return

    # Read file content
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Filter lines that start with "Alex:" or "Martin:"
    cleaned_lines = [line for line in lines if line.strip().startswith(("Alex:", "Martin:"))]

    # Save cleaned content back to final1.txt
    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(cleaned_lines)

    print(f"Non-dialog lines removed from {file_path}")

# Call the functions to process final.txt and clean final1.txt
refine_dialog()
clean_non_dialog_lines()

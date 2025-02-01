import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

def generate_dialog(text_content):
    """Generate dialog based on text content using Groq API."""
    # Get API key from environment variable
    api_key = os.getenv('GROQ_API_KEY')
    
    # Validate API key
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in .env file")

    # Initialize Groq client
    client = Groq(api_key=api_key)

    # Prompt for dialog generation with detailed question-answer conversation
    prompt = f"""Create a detailed, informative dialog between Alex (host) and Martin (expert) that explains the key points from the following text. The dialog should break down the content into clear, concise questions and answers. Each question should probe deeper into the findings, methodologies, or conclusions of the research paper, and the answers should provide well-explained, comprehensive responses.

**Make sure the dialog is clear, engaging, and includes the following:**
- Alex should ask insightful questions about the content.
- Martin should give comprehensive answers that explain concepts, results, and details.
- The dialog should aim to clarify the research paper in a conversational tone.

Text Content:
{text_content}

Dialog Format:
Alex: [Engaging question that explains a key concept or finding]
Martin: [Clear, detailed explanation of the concept or finding]
Alex: [Follow-up question exploring further]
Martin: [Further explanation, including relevant details]"""

    try:
        # Generate dialog using Llama3 model
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are creating a dialog between Alex (host) and Martin (expert) that explains the key points from academic research papers."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192"
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating dialog: {str(e)}"

def process_generated_slides():
    # Output file for final dialogs
    final_output_path = 'final.txt'
    
    # Flag to track first dialog
    first_dialog = True
    
    # Ensure generated_slides exists
    os.makedirs('generated_slides', exist_ok=True)
    
    # Open final output file in append mode
    with open(final_output_path, 'a', encoding='utf-8') as final_file:
        # Iterate through files in generated_slides
        for filename in os.listdir('generated_slides'):
            # Skip title_authors.txt and delete it
            if filename == 'title_authors.txt':
                os.remove(os.path.join('generated_slides', filename))
                continue
            
            # Process only .txt files
            if filename.endswith('.txt'):
                file_path = os.path.join('generated_slides', filename)
                
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Generate dialog
                dialog = generate_dialog(content)
                
                # Append dialog to final output
                if first_dialog:
                    final_file.write(f"Here is the dialog between Alex and Martin:\n\n{dialog}\n\n")
                    first_dialog = False
                else:
                    final_file.write(f"{dialog}\n\n")
                
                # Delete processed file
                os.remove(file_path)
        
        print("Dialog generation complete. Check final.txt")

# Ensure script can be run directly or imported
if __name__ == "__main__":
    process_generated_slides()

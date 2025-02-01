import os
import re
import sys
from groq import Groq
import io

# Force UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')



# Get command line argument for abstract inclusion
include_abstract = sys.argv[1].lower() == 'true' if len(sys.argv) > 1 else False

# Set the directory where all input files are stored
input_dir = "generated_slides/"

title = ""
authors = ""

# Read title and authors from title_authors.txt inside generated_slides/
title_authors_path = os.path.join(input_dir, "title_authors.txt")
with open(title_authors_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line.startswith("Title:"):
            title = line.replace("Title:", "").strip()
        elif line.startswith("Authors:"):
            authors = line.replace("Authors:", "").strip()

abstract_content = ""
abstract_path = os.path.join(input_dir, "abstract.txt")
if include_abstract and os.path.exists(abstract_path):
    with open(abstract_path, "r", encoding="utf-8") as f:
        abstract_content = f.read().strip()

def abs_prompt(content):
    return f"""You are given the abstract of a research paper. Your task is to summarize it in a way that retains all key insights, findings, and contributions of the paper.

    **Key Guidelines**:
    - Summarize the abstract in 80-120 words.
    - Maintain clarity and logical flow.
    - Ensure that all important details, including key findings, research contributions, and methodologies, are included.
    - Avoid redundancy while keeping the summary informative.

    **Expected Output Format:**
    Write the summarized abstract here in 80-120 words.
    Here is the content:{content}
    """

def main_prompt_small(title, content):
    return f"""You are given a research paper module on the topic *{title}* with the content provided at the end. Your task is to *summarize the content accurately* and *generate structured PowerPoint slides* in a hybrid format (*brief explanation + bullet points*) while maintaining key technical details.

    ## *⚠ Important Rules:*  
    - *Strictly include only the summarized research content* – do NOT add any extra text (e.g., "Note:", "Summary:", "Conclusion:").  
    - *Remove unnecessary characters* like _, #, @, etc.  
    - *Use a hybrid format* – include a brief explanation followed by bullet points.  
    - *Optimize content to fit within 1-2 slides per section* (Avoid 3rd slide unless absolutely necessary).  
    - *Introduction & Conclusion slides must always be single-page summaries and only in the start and end respectively instead of anywhere in between!!*  
    - *Ensure bullet points highlight key concepts, methods, and results concisely.*  
    - *Each slide must follow the specified format and contain only research-relevant content.*  

    ---
    ## *🔹 Summarization Rules*  
    - *Keep it concise and precise* while maintaining all critical technical details.  
    - *Ensure numerical data, equations, and key findings are retained.*  
    - If the content can fit within *one slide*, do NOT generate an extra slide for minor content.  
    - If needed, *spread content across two full slides*, ensuring no incomplete slides.  
    - *Use structured bullet points* for clarity while preserving essential details.  

    ---
    ## *📌 Slide Generation Instructions:*  
    - *Slide 1:* *Title + Short 2-3 line overview of the module* (Must include #Image=True).  
    - *Slide 2:* *Main summarized content (explanation + bullet points)* (Must include #Image=False).  
    - *Slide 3 (Only if necessary):* *Additional critical details* (Only if Slide 2 exceeds limit, otherwise do NOT generate).  
    - *Conclusion Slide:* No image reference required (#Image tag not needed).  

    ---
    ## *📝 Expected Response Format (Follow Exactly)*
    ```plaintext
    #Slide: 1
    #Header: {title}
    #Image: True
    #Content: 
    [2-3 line concise overview of the module.]

    #Slide: 2
    #Header: {title}
    #Image: False
    #Content:
    [Short explanation of the content, followed by structured bullet points.]
    - Key Point 1  
    - Key Point 2  
    - Key Point 3 (Include numerical data, equations, or key technical insights)

    ---
    ## *🚀 Here is the Content to Process:*  
    {content}
    """

def call_llm_main(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-specdec",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.35,
        max_completion_tokens=1500,
        top_p=0.85,
        stream=False,
        stop=None,
    )
    return response.choices[0].message.content

def call_llm_sec(prompt):
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_completion_tokens=800,
        top_p=0.9,
        stream=False,
        stop=None,
    )
    return response.choices[0].message.content

try:
    merged_output_file = os.path.join(input_dir, "final_presentation_slides.txt")

    # Read section files from generated_slides/
    all_files = [
        f for f in os.listdir(input_dir) 
        if f.endswith(".txt") and f not in ["title_authors.txt", "abstract.txt", "final_presentation_slides.txt"]
    ]

    # Sort by numerical prefix if present
    def extract_number(filename):
        match = re.match(r"^(\d+)_", filename)  
        return int(match.group(1)) if match else float('inf')

    all_files = sorted(all_files, key=extract_number)

    # Process abstract if included
    abstract_response = ""
    if include_abstract and abstract_content:
        a_prompt = abs_prompt(abstract_content)
        abstract_response = call_llm_sec(a_prompt)

    with open(merged_output_file, "w", encoding="utf-8") as out_file:
        slide_counter = 1

        # Write title & authors
        out_file.write(f"#Slide: {slide_counter}\n")
        out_file.write(f"#Header: {title}\n")
        out_file.write(f"#Content:\n{authors}\n\n")
        slide_counter += 1

        # Write abstract slide (if included)
        if include_abstract and abstract_response:
            out_file.write(f"#Slide: {slide_counter}\n")
            out_file.write("#Header: Abstract\n")
            out_file.write(f"#Content:\n{abstract_response}\n\n")
            slide_counter += 1

        # Process each section file
        for filename in all_files:
            file_path = os.path.join(input_dir, filename)
            module_title = filename.replace(".txt", "")
            module_title = re.sub(r'^\d+_', '', module_title).replace("_", " ")  

            with open(file_path, "r", encoding="utf-8") as file:
                module_content = file.read()

            m_prompt = main_prompt_small(module_title, module_content)
            response_text = call_llm_main(m_prompt)

            for line in response_text.split("\n"):
                if line.startswith("#Slide:"):
                    out_file.write(f"#Slide: {slide_counter}\n")
                    slide_counter += 1
                else:
                    out_file.write(line + "\n")

            os.remove(file_path)  # Delete processed file
            print(f"✓ Processed {module_title}")

    print("All modules processed successfully!")
    sys.exit(0)

except Exception as e:
    print(f"Error occurred: {str(e)}", file=sys.stderr)
    sys.exit(1)
import os
import re
from groq import Groq
import sys


# Set stdout encoding to UTF-8 to handle special characters
sys.stdout.reconfigure(encoding='utf-8')

# Get the include_abstract flag from command-line arguments
include_abstract = sys.argv[1].lower() == "true"  # Convert to boolean

# Load title and authors
title = ""
authors = ""
with open("generated_slides/title_authors.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line.startswith("Title:"):
            title = line.replace("Title:", "").strip()
        elif line.startswith("Authors:"):
            authors = line.replace("Authors:", "").strip()

abstract_content = ""
if include_abstract:
    with open("generated_slides/abstract.txt", "r", encoding="utf-8") as f:
        abstract_content = f.read().strip()

# Function to generate the abstract prompt
def abs_prompt(content):
    return f"""You are given the abstract of a research paper. Your task is to summarize it in a way that retains all key insights, findings, and contributions of the paper.

*Key Guidelines*:
- Summarize the abstract in 80-120 words.
- Maintain clarity and logical flow.
- Ensure that all important details, including key findings, research contributions, and methodologies, are included.
- Avoid redundancy while keeping the summary informative.

*Expected Output Format:*
Write the summarized abstract here in 80-120 words.
Here is the content: {content}
"""

# Function to generate the content for each module
def main_prompt_small(title, content):
    return f"""You are given a research paper module on the topic {title} with the content given at the end of the prompt. Your task is to first summarize the entire content given at the end ignoring all unwanted things, without missing any details since it is content of a research paper and hence requires more accuracy and then generate structured PowerPoint slides based on that summary.
    Also make sure you remove unnecessary characters like _, #, @ etc from the content and then summarize it in a perfect manner

    ⚠ Important Constraints:  
    - Avoid unnecessary characters like _, #, @, etc.  
    - Optimize content to fit within 1-2 slides (Avoid 3rd slide unless absolutely necessary).  
    - Ensure clarity and completeness in minimal slides.
    - There should be a single slide for both introduction and the conclusion compulsorily!

    🔹 Summarization Rules  
    - Summarize accurately and concisely while maintaining key technical details.  
    - If there are formulas, numerical data, or equations, ensure they are included in a simplified manner.  
    - If possible, fit the content into one slide, unless it loses clarity.  
    - If any quantitative data, equations, or results are present, include them.
    - If the content generated can be set in one page then don't generate a new slide for just a little bit of content, make sure that generate only that much amount of content that fits in one page else generate more to occupy two full pages.

    Slide Generation Step:
    - Convert the summary into well-structured PowerPoint slides, point wise!.
    - The slides must not exceed 400 characters, but should be at least 300 characters to ensure completeness.
    - If the summary is too long to fit in one slide, break it into multiple slides (maximum 2).
    - If numerical results are included, ensure they are presented clearly and concisely.
    - Introduction & Conclusion slides must be single-page summaries.

    📌 Slide Structure:  
    - Slide 1: Title + Short 2-3 line overview of the module.  
    - Slide 2: Main summarized content (compact, covering all key points).  
    - Slide 3 (Avoid if possible): Only use for critical remaining information.

    Expected Format (Follow Exactly)

    #Slide: 1
    #Header:{title}
    #Content: [Write a short 2-3 line overview of the module.]

    #Slide: 2
    #Header: {title}
    #Content: [Summarized key details, ensuring completeness and technical clarity. Include all necessary content, like key numbers, formulas, or explanations.]

    #Slide: 3 (No need to output in case of conclusion and introduction)
    #Header: More about{title}
    #Content: If Slide 2 exceeds the limit, continue here else don't even output this slide, only give output upto slide 2.

    Here is the Content: {content}
    """
def call_llm_main(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
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

# List all .txt files except for title_authors.txt and abstract.txt
all_files = [f for f in os.listdir("generated_slides") if f.endswith(".txt") and f not in ["title_authors.txt", "abstract.txt"]]

# Sort files by numeric order
def extract_number(filename):
    match = re.match(r"^(\d+)_", filename)
    return int(match.group(1)) if match else float('inf')

all_files = sorted(all_files, key=extract_number)

# Generate abstract summary if include_abstract is True
a_prompt = abs_prompt(abstract_content) if include_abstract else ""
response_a = call_llm_sec(a_prompt) if include_abstract else ""

# Prepare merged output file
merged_output_file = "generated_slides/final_presentation_slides.txt"

with open(merged_output_file, "w", encoding="utf-8") as out_file:
    slide_counter = 1

    # Slide 1: Title and Authors
    out_file.write(f"#Slide: {slide_counter}\n")
    out_file.write(f"#Header: {title}\n")
    out_file.write(f"#Content:\n{authors}\n\n")
    slide_counter += 1

    # Slide 2: Abstract if included
    if include_abstract:
        out_file.write(f"#Slide: {slide_counter}\n")
        out_file.write("#Header: Abstract\n")
        out_file.write(f"#Content:\n{response_a}\n\n")
        slide_counter += 1

    # Process each file and create slides
    for filename in all_files:
        module_title = filename.replace(".txt", "")
        module_title = re.sub(r'^\d+', '', module_title).replace("", " ")

        with open(os.path.join("generated_slides", filename), "r", encoding="utf-8") as file:
            module_content = file.read()

        m_prompt = main_prompt_small(module_title, module_content)
        response_text = call_llm_main(m_prompt)

        for line in response_text.split("\n"):
            if line.startswith("#Slide:"):
                out_file.write(f"#Slide: {slide_counter}\n")
                slide_counter += 1
            else:
                out_file.write(line + "\n")

        os.remove(os.path.join("generated_slides", filename))  # Remove the processed file
        print(f"Processed {module_title} and deleted {filename}")

print("All modules processed successfully and merged into final_presentation_slides.txt!")
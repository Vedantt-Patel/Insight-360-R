import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize title and authors
title = ""
authors = ""

# Read the research paper PDF (handling non-UTF-8 characters with 'ignore')
with open("rp1.pdf", "r", encoding="utf-8", errors='ignore') as f:
    for line in f:
        line = line.strip()
        if line.startswith("Title:"):
            title = line.replace("Title:", "").strip()
        elif line.startswith("Authors:"):
            authors = line.replace("Authors:", "").strip()

# Function for generating the prompt for summarizing the abstract
def abs_prompt(content):
    return f"""You are given the abstract of a research paper. Your task is to summarize it while retaining all key insights, findings, and contributions of the paper.

**Key Guidelines**:
- Summarize the abstract in 400-500 words.
- Maintain clarity and logical flow.
- Ensure that all important details, including key findings, research contributions, and methodologies, are included.
- Avoid redundancy while keeping the summary informative.

**Expected Output Format:**
Write the summarized abstract here in 400-500 words.
Here is the content:{content}
"""

# Function for generating the prompt for summarizing a module
def main_prompt_large(title, content):
    return f"""You are given a research paper module on the topic {title} with the content given at the end of the prompt. Your task is to first summarize the entire content given at the end, ignoring all unwanted things, without missing any details since it is content of a research paper and requires more accuracy.

⚠️ **Important Constraints:**  
- **Avoid unnecessary characters** like `_`, `#`, `@`, etc.  
- **Ensure clarity and completeness.**
- **Summarization should be detailed (400-500 words).**
- **Ensure all numerical data, equations, or findings are retained.**

**Summarization Rules:**  
- Summarize **accurately and concisely** while maintaining key technical details.  
- If there are **formulas, numerical data, or equations**, ensure they are included in a simplified manner.  
- If any quantitative data, equations, or results are present, include them.

**Expected Format:**
- **Detailed Summary (800-1000 words).**

Here is the Content: {content}
"""

# Function to call the LLM API and generate a response for abstract
def call_llm_sec(prompt):
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_completion_tokens=1500,
        top_p=0.9,
        stream=False,
        stop=None,
    )
    return response.choices[0].message.content

# Function to call the LLM API and generate a response for modules
def call_llm_main(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.35,
        max_completion_tokens=2000,
        top_p=0.85,
        stream=False,
        stop=None,
    )
    return response.choices[0].message.content

# Get all the .txt files except 'title_authors.txt' and 'abstract.txt'
all_files = [f for f in os.listdir("generated_slides") if f.endswith(".txt") and f not in ["title_authors.txt", "abstract.txt"]]

# Sort the files by the numbers at the beginning of their names
all_files = sorted(all_files, key=lambda x: int(re.match(r"^(\d+)_", x).group(1) if re.match(r"^(\d+)_", x) else float('inf')))

# Summarize the abstract if it exists
abstract_content = ""
if os.path.exists("generated_slides/abstract.txt"):
    with open("generated_slides/abstract.txt", "r", encoding="utf-8", errors='ignore') as f:
        abstract_content = f.read().strip()

# Generate the summary for the abstract
a_prompt = abs_prompt(abstract_content)
response_a = call_llm_sec(a_prompt)

# Save the abstract summary to the respective file
if abstract_content:
    with open("generated_slides/abstract.txt", "w", encoding="utf-8") as f:
        f.write(f"Abstract Summary:\n{response_a}\n")

# Process each module file and replace content with summaries
for filename in all_files:
    with open(f"generated_slides/{filename}", "r", encoding="utf-8", errors='ignore') as file:
        module_content = file.read().strip()
    
    module_title = filename.replace(".txt", "")
    module_title = re.sub(r'^\d+_', '', module_title).replace("_", " ")

    # Generate the summary for the module
    m_prompt = main_prompt_large(module_title, module_content)
    response_text = call_llm_main(m_prompt)

    # Replace the content of the original file with the generated summary
    with open(f"generated_slides/{filename}", "w", encoding="utf-8") as file:
        file.write(f"Summary of {module_title}:\n{response_text}\n")

    print(f"✔ Processed and updated {filename}")

print("🎯 All modules processed and updated with summarized content.")

import pymupdf4llm
import sys
import os
import re
import ast
import json
from groq import Groq
import shutil
import io

# Force UTF-8 encoding
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


filename = sys.argv[1]
if not os.path.isfile(filename):
    raise FileNotFoundError(f"Error: File '{filename}' not found. Check the path and try again.")

outname = filename.replace(".pdf", ".md")
md_text = pymupdf4llm.to_markdown(os.path.abspath(filename))

def call_llm_sec(prompt):
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_completion_tokens=800,
        top_p=0.9,
        stream=False,
        stop=None,
    )
    return response.choices[0].message.content

top = md_text[:1000]

auth = f"""Extract the authors' names from the following text and return them strictly as a valid Python list.
Only return the list, nothing else. No extra text.
Text: {top}
[]"""

response_text = call_llm_sec(auth)

try:
    authors = ast.literal_eval(response_text)
    if not isinstance(authors, list):
        raise ValueError("Response is not a valid list.")
except (SyntaxError, ValueError):
    print("Error: LLM returned an invalid format. Falling back to manual extraction.")
    authors = re.findall(r"[A-Z][a-z]+(?:\s[A-Z][a-z]+)*", top)

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)[:50] 

def roman_to_int(roman):
    roman_dict = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10
    }
    return roman_dict.get(roman, 999)

def extract_roman_numeral(text):
    match = re.match(r"^(I{1,3}|IV|V?I{0,3})\b", text.strip())  
    return match.group(0) if match else None

def extract_paper_components(text, authors):
    title_pattern = r'# (.*?)\n\n'
    title_match = re.search(title_pattern, text)
    title = title_match.group(1) if title_match else ""

    abstract_pattern = r'Abstract—(.*?)Keywords'
    abstract_match = re.search(abstract_pattern, text, re.DOTALL)
    abstract = abstract_match.group(1).strip() if abstract_match else ""
    abstract = re.sub(r'\*\*', '', abstract)
    abstract = ' '.join(abstract.split())

    sections = []
    section_pattern = r'([IVX]+\..*?)\n(.*?)(?=\n[IVX]+\.|References|$)'
    section_matches = re.finditer(section_pattern, text, re.DOTALL)

    for match in section_matches:
        section_title = match.group(1).strip()
        section_content = match.group(2).strip()
        
        roman_part = extract_roman_numeral(section_title)
        if roman_part:
            integer_part = roman_to_int(roman_part)
            new_section_title = section_title.replace(roman_part, str(integer_part), 1)  
        else:
            integer_part = 999  
            new_section_title = section_title

        sections.append((integer_part, new_section_title, section_content))

    sections.sort(key=lambda x: x[0]) 
    
    return {
        'title': title,
        'authors': authors,
        'abstract': abstract,
        'sections': sections  
    }

paper_components = extract_paper_components(md_text, authors)

title = paper_components['title']
authors = ', '.join(paper_components['authors'])
abstract = paper_components['abstract']
sorted_sections = paper_components['sections']

os.makedirs("generated_slides", exist_ok=True)

# Write files with UTF-8 encoding
with open("title_authors.txt", "w", encoding="utf-8") as f:
    f.write(f"Title:{title}\n")
    f.write(f"Authors:{authors}\n\n")

with open("abstract.txt", "w", encoding="utf-8") as fi:
    fi.write(f"{abstract}\n")

shutil.move("title_authors.txt", "generated_slides/title_authors.txt")
shutil.move("abstract.txt", "generated_slides/abstract.txt")

for number, section_title, content in sorted_sections:
    filename = sanitize_filename(section_title) + ".txt"
    with open(f"generated_slides/{filename}", "w", encoding="utf-8") as f:
        module_title = filename.replace(".txt", "")
        module_title = re.sub(r'^\d+_', '', module_title).replace("_", " ")  
        f.write(f"{module_title}:\n{content}\n")

references_pattern = r'References(.*?)$'
references_match = re.search(references_pattern, md_text, re.DOTALL)
references = references_match.group(1).strip() if references_match else ""

if references:
    with open("references.txt", "w", encoding="utf-8") as f:
        f.write(references)
    shutil.move("references.txt", "generated_slides/references.txt")

print("Files have been saved successfully.")
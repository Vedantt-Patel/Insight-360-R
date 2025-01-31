import pymupdf4llm
import sys
import os
import re
import shutil

# Set the encoding for stdout to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Get file from command line argument
filename = sys.argv[1]
if not os.path.isfile(filename):
    raise FileNotFoundError(f"Error: File '{filename}' not found. Check the path and try again.")

# Convert PDF to markdown format
outname = filename.replace(".pdf", ".md")
md_text = pymupdf4llm.to_markdown(os.path.abspath(filename))

def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)[:50]

def roman_to_int(roman):
    roman_dict = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
    return roman_dict.get(roman, 999)

def extract_roman_numeral(text):
    match = re.match(r"^(I{1,3}|IV|V?I{0,3})\b", text.strip())  
    return match.group(0) if match else None

def extract_paper_components(text):
    title_pattern = r'# (.*?)\n\n'
    title_match = re.search(title_pattern, text)
    title = title_match.group(1) if title_match else ""

    author_pattern = r'## (.*?)\n\n'
    author_match = re.search(author_pattern, text)
    authors = author_match.group(1).replace('[∗]', '').replace('[‡]', '').replace('[†]', '').split(', ') if author_match else []

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

# Extract paper components
paper_components = extract_paper_components(md_text)

# Prepare for saving the files
output_folder = 'generated_slides'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Write title and authors to a text file
with open(os.path.join(output_folder, "title_authors.txt"), "w", encoding="utf-8") as f:
    f.write(f"Title: {paper_components['title']}\n")
    f.write(f"Authors: {', '.join(paper_components['authors'])}\n\n")

# Write abstract to a text file
with open(os.path.join(output_folder, "abstract.txt"), "w", encoding="utf-8") as fi:
    fi.write(f"{paper_components['abstract']}\n")

# Write each section to a separate file in the output folder
for number, section_title, content in paper_components['sections']:
    filename = sanitize_filename(section_title) + ".txt"
    with open(os.path.join(output_folder, filename), "w", encoding="utf-8") as f:
        f.write(f"{section_title}:\n{content}\n")

# Extract and save references if present
references_pattern = r'References(.*?)$'
references_match = re.search(references_pattern, md_text, re.DOTALL)
references = references_match.group(1).strip() if references_match else ""
if references:
    with open(os.path.join(output_folder, "references.txt"), "w", encoding="utf-8") as f:
        f.write(references)

print("✅ Files have been saved successfully.")

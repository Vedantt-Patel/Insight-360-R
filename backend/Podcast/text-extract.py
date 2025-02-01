import pymupdf4llm
import pathlib
import sys
import os
import re
import shutil

# Check if the file is passed as a command-line argument
filename = sys.argv[1]
if not os.path.isfile(filename):
    raise FileNotFoundError(f"Error: File '{filename}' not found. Check the path and try again.")

# Convert PDF to markdown text
outname = filename.replace(".pdf", ".md")
md_text = pymupdf4llm.to_markdown(os.path.abspath(filename))


def sanitize_filename(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)[:50] 

def roman_to_int(roman):
    """Convert Roman numerals to integer values."""
    roman_dict = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10
    }
    return roman_dict.get(roman, 999)


def extract_roman_numeral(text):
    """Extract Roman numeral at the start of a section title."""
    match = re.match(r"^(I{1,3}|IV|V?I{0,3})\b", text.strip())  
    return match.group(0) if match else None


def extract_paper_components(text):
    title_pattern = r'# (.*?)\n\n'
    title_match = re.search(title_pattern, text)
    title = title_match.group(1) if title_match else ""

    author_pattern = r'## (.*?)\n\n'
    author_match = re.search(author_pattern, text)
    authors = author_match.group(1).replace('[∗]', '').replace('[‡]', '').replace('[†]', '').split(', ') if author_match else []

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
        'sections': sections  
    }


# Extract paper components
paper_components = extract_paper_components(md_text)

title = paper_components['title']
authors = ', '.join(paper_components['authors'])
sorted_sections = paper_components['sections']

# Create the 'generated_slides' folder if it doesn't exist
os.makedirs('generated_slides', exist_ok=True)

# Save title and authors to a file inside 'generated_slides' folder
with open(os.path.join("generated_slides", "title_authors.txt"), "w", encoding="utf-8") as f:
    f.write(f"Title:{title}\n")
    f.write(f"Authors:{authors}\n\n")

# Write the sections to separate files inside 'generated_slides' folder
for number, section_title, content in sorted_sections:
    filename = sanitize_filename(section_title) + ".txt"
    with open(os.path.join("generated_slides", filename), "w", encoding="utf-8") as f:
        module_title = filename.replace(".txt", "")
        module_title = re.sub(r'^\d+_', '', module_title).replace("_", " ")  
        f.write(f"{module_title}:\n{content}\n")

# Extract and save references
references_pattern = r'References(.*?)$'
references_match = re.search(references_pattern, md_text, re.DOTALL)
references = references_match.group(1).strip() if references_match else ""
if references:
    with open(os.path.join("generated_slides", "references.txt"), "w", encoding="utf-8") as f:
        f.write(references)

print("✅ Files have been saved successfully in the 'generated_slides' folder.")
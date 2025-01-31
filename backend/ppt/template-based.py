from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_presentation(text_file, output_pptx):
    prs = Presentation()

    with open(text_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    slide_num = None
    header = ""
    content = ""
    references = []
    prev_header = ""
    bullet_points = []

    for line in lines:
        line = line.strip()

        # If we encounter a new slide
        if line.startswith("#Slide: "):
            if header and (content or bullet_points):
                slide = prs.slides.add_slide(prs.slide_layouts[1])  # Title and Content layout
                title = slide.shapes.title
                body = slide.placeholders[1]

                # Set title font style
                if header != prev_header:
                    title.text = header
                    title.text_frame.paragraphs[0].font.size = Pt(36)
                    title.text_frame.paragraphs[0].font.bold = True
                    title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)  # Dark blue
                else:
                    title.text = header
                    title.text_frame.paragraphs[0].font.size = Pt(28)
                    title.text_frame.paragraphs[0].font.bold = False
                    title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)

                # Set content font style
                if bullet_points:
                    for bullet in bullet_points:
                        p = body.text_frame.add_paragraph()
                        p.text = bullet.lstrip('*- ')  # Remove bullet notation
                        p.level = 0
                        p.font.size = Pt(16)
                        p.font.color.rgb = RGBColor(51, 51, 51)  # Dark gray
                else:
                    body.text = content
                    body.text_frame.paragraphs[0].font.size = Pt(16)
                    body.text_frame.paragraphs[0].font.color.rgb = RGBColor(51, 51, 51)  # Dark gray

                prev_header = header
                header = ""
                content = ""
                bullet_points = []

            slide_num = int(line.split(": ")[1])

        # Parse header, content, and bullet points
        elif line.startswith("#Header: "):
            header = line.replace("#Header: ", "").strip()
        elif line.startswith("#Content:"):
            content = line.replace("#Content:", "").strip()
        elif line.startswith("References:"):
            references.append(line.replace("References:", "").strip())
        elif line.startswith("*") or line.startswith("-"):
            bullet_points.append(line.lstrip('*- '))  # Handle bullets

        else:
            if bullet_points:
                bullet_points[-1] += " " + line
            else:
                content += " " + line  # Append additional content

    # Add the last slide if necessary
    if header and (content or bullet_points):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        title = slide.shapes.title
        body = slide.placeholders[1]

        if header != prev_header:
            title.text = header
            title.text_frame.paragraphs[0].font.size = Pt(36)
            title.text_frame.paragraphs[0].font.bold = True
            title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
        else:
            title.text = header
            title.text_frame.paragraphs[0].font.size = Pt(28)
            title.text_frame.paragraphs[0].font.bold = False
            title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)

        if bullet_points:
            for bullet in bullet_points:
                p = body.text_frame.add_paragraph()
                p.text = bullet.lstrip('*- ')
                p.level = 0
                p.font.size = Pt(16)
                p.font.color.rgb = RGBColor(51, 51, 51)
        else:
            body.text = content
            body.text_frame.paragraphs[0].font.size = Pt(16)
            body.text_frame.paragraphs[0].font.color.rgb = RGBColor(51, 51, 51)

    # Add References slide if necessary
    if references:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        title = slide.shapes.title
        body = slide.placeholders[1]

        title.text = "References"
        title.text_frame.paragraphs[0].font.size = Pt(32)
        title.text_frame.paragraphs[0].font.bold = True
        title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)

        body.text = "\n".join(references)
        for para in body.text_frame.paragraphs:
            para.font.size = Pt(18)
            para.font.color.rgb = RGBColor(51, 51, 51)

    # Center align the title of the first slide
    if prs.slides:
        first_slide = prs.slides[0]
        title = first_slide.shapes.title
        if title:
            title.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
            title.text_frame.paragraphs[0].vertical_anchor = PP_ALIGN.CENTER

    prs.save(output_pptx)
    print(f"Presentation saved as {output_pptx}")

# Run the function with the input and output paths
create_presentation("generated_slides/final_presentation_slides.txt", "generated_slides/output_presentation_final.pptx")
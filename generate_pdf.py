"""
Convert KNOWLEDGE_BASE_CHECKLIST.txt to professional PDF
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

def generate_pdf():
    # File paths
    input_txt = "KNOWLEDGE_BASE_CHECKLIST.txt"
    output_pdf = "KNOWLEDGE_BASE_CHECKLIST.pdf"
    
    # Check if input file exists
    if not os.path.exists(input_txt):
        print(f"Error: {input_txt} not found!")
        return
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title="MewarChat Knowledge Base Checklist"
    )
    
    # Container for PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0078D4'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#333333'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#0078D4'),
        spaceAfter=10,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        textTransform='uppercase'
    )
    
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['BodyText'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=4,
        leading=14,
        fontName='Helvetica'
    )
    
    # Title page
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("🎓 MewarChat", title_style))
    elements.append(Paragraph("Knowledge Base Information Checklist", subtitle_style))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}<br/>"
        f"<b>University:</b> Mewaru University Nigeria<br/>"
        f"<b>Purpose:</b> Comprehensive guide for building and maintaining the knowledge base",
        normal_style
    ))
    
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())
    
    # Table of Contents
    elements.append(Paragraph("Table of Contents", ParagraphStyle(
        'TOC',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.HexColor('#0078D4'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )))
    
    toc_items = [
        "1. Admissions & Enrollment",
        "2. Tuition & Fees",
        "3. Academic Calendar & Schedules",
        "4. Programs & Departments",
        "5. Student Services",
        "6. Academic Policies & Procedures",
        "7. Campus Facilities & Infrastructure",
        "8. Regulations & Conduct",
        "9. Financial Information",
        "10. Admissions Contact & Support",
        "11. Technology & Online Learning",
        "12. Graduation & Certification"
    ]
    
    for item in toc_items:
        elements.append(Paragraph(f"• {item}", normal_style))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())
    
    # Parse and add content from txt file
    with open(input_txt, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip decorative lines
        if line.startswith('=') or not line:
            i += 1
            continue
        
        # Check if it's a section header (numbered sections)
        if any(line.startswith(f"{num}.") for num in range(1, 13)):
            # Add page break before major sections (except first)
            if elements and len(elements) > 20:
                elements.append(PageBreak())
            elements.append(Paragraph(line, section_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Check for subsection headers (like "HOW TO ADD INFORMATION")
        elif line and not line.startswith('[') and len(line) > 10 and line.isupper():
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(line, section_style))
            elements.append(Spacer(1, 0.1*inch))
        
        # Checklist items
        elif line.startswith('[ ]'):
            checkbox_text = line.replace('[ ]', '☐').strip()
            elements.append(Paragraph(f"• {checkbox_text}", normal_style))
        
        # Regular text
        elif line and not line.startswith('='):
            if line.startswith('-'):
                elements.append(Paragraph(f"• {line[1:].strip()}", normal_style))
            elif ':' in line and not line.startswith('['):
                elements.append(Paragraph(f"<b>{line}</b>", normal_style))
            else:
                elements.append(Paragraph(line, normal_style))
        
        i += 1
    
    # Add footer
    elements.append(Spacer(1, 0.3*inch))
    elements.append(PageBreak())
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER,
        spaceAfter=6
    )
    
    elements.append(Paragraph("<b>About MewarChat</b>", section_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(
        "MewarChat is an AI-powered university assistant that uses Retrieval Augmented Generation (RAG) "
        "to provide accurate, grounded answers about university operations, admissions, academics, and services. "
        "The quality and comprehensiveness of responses depend on the completeness of the knowledge base.",
        normal_style
    ))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph("<b>How to Use This Checklist</b>", section_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph(
        "1. Gather all information listed in each category<br/>"
        "2. Organize information into .txt or .md files<br/>"
        "3. Upload documents via the MewarChat Streamlit sidebar<br/>"
        "4. System automatically indexes and makes content searchable<br/>"
        "5. Test with sample questions to verify coverage",
        normal_style
    ))
    
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        f"<i>Document prepared: {datetime.now().strftime('%B %d, %Y at %H:%M')} | "
        "For: Mewaru University Nigeria</i>",
        footer_style
    ))
    
    # Build PDF
    try:
        doc.build(elements)
        print(f"✅ PDF created successfully: {output_pdf}")
        print(f"📄 File size: {os.path.getsize(output_pdf) / 1024:.2f} KB")
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")

if __name__ == "__main__":
    generate_pdf()

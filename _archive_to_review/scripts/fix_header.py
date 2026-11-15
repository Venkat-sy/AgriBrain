import docx
from docx.oxml import parse_xml

doc = docx.Document(r'C:\Users\USER\OneDrive\Desktop\FinalYearProject\Project_Synopsis_Filled_v3.docx')
section = doc.sections[0]
section.different_first_page_header_footer = True

header = section.header
first_page_header = section.first_page_header

# Clear existing first page header (if any)
for child in list(first_page_header._element):
    first_page_header._element.remove(child)

# Move all children from primary header to first_page_header
for child in list(header._element):
    first_page_header._element.append(child)

# Ensure primary header has at least one empty paragraph (required by OOXML)
header._element.append(parse_xml('<w:p xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>'))

doc.save(r'C:\Users\USER\OneDrive\Desktop\FinalYearProject\Project_Synopsis_Filled_v4.docx')
print('Done!')

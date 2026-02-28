import json
from markitdown import MarkItDown




md = MarkItDown(enable_plugins=False)  # Set to True to enable plugins
# md = MarkItDown(docintel_endpoint="<document_intelligence_endpoint>")

pdf_path = "C:\\IA\\tools\\IA-TOOLS-markitdown\\z_iosu\\docs\\TestDoc\\1-Eusk-c25-16499-r.pdf"

# md = MarkItDown(docintel_endpoint="<document_intelligence_endpoint>")
result = md.convert(pdf_path)
print(result.text_content)

xlsx_path = "C:\\IA\\tools\\IA-TOOLS-markitdown\\z_iosu\\docs\\TestDoc\\2404 PLANTILLA SUASOR MODELO NORMAL -SIALA.xlsx"
result = md.convert(xlsx_path)
print(result.text_content)


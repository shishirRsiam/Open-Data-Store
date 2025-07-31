from PIL import Image
import pytesseract
from docx import Document

# Path to your image
image_path = "bangla_image.jpg"

# Set path to tesseract executable if needed (for Windows)
# Example: pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Use Bangla language ('ben')
text = pytesseract.image_to_string(Image.open(image_path), lang='ben')

# Create Word document
doc = Document()
doc.add_paragraph(text)

# Save the Word file
output_path = "bangla_output.docx"
doc.save(output_path)

print("✅ Word file saved at:", output_path)

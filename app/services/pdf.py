
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
def make_simple_pdf(content: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    textobject = c.beginText(40, height - 60)
    for line in content.splitlines():
        textobject.textLine(line[:110])
    c.drawText(textobject)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()

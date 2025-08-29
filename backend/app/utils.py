
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import csv

def text_to_pdf_bytes(title: str, lines: list) -> bytes:
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    c.setFont("Helvetica", 12)
    c.drawString(40, 750, title)
    y = 730
    for line in lines:
        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = 750
        c.drawString(40, y, line)
        y -= 14
    c.save()
    packet.seek(0)
    return packet.read()

def testcases_to_csv_bytes(testcases):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id","title","type","steps","expected_result","description"])
    for t in testcases:
        writer.writerow([t.get("id",""), t.get("title",""), t.get("type",""), t.get("steps",""), t.get("expected_result",""), t.get("description","")])
    return output.getvalue().encode("utf-8")

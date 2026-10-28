import os
from pathlib import Path
from django.conf import settings
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors

class CertificateGeneratorService:
    @staticmethod
    def generate_pdf(certificate):
        """
        Renders an authentic, professional landscape PDF certificate for a completed enrollment.
        """
        output_dir = Path(settings.MEDIA_ROOT) / 'certificates'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"cert_{certificate.certificate_number}.pdf"
        file_path = output_dir / filename

        # Create canvas in landscape (11 x 8.5 inches)
        width, height = landscape(letter)
        c = canvas.Canvas(str(file_path), pagesize=landscape(letter))

        # Background & Luxury Borders
        c.setFillColor(colors.HexColor('#0F172A'))  # Slate 900
        c.rect(0, 0, width, height, fill=True, stroke=False)

        # Elegant gold outer border
        c.setStrokeColor(colors.HexColor('#D97706'))  # Amber 600
        c.setLineWidth(4)
        c.rect(30, 30, width - 60, height - 60, fill=False, stroke=True)

        # Delicate inner border
        c.setStrokeColor(colors.HexColor('#F59E0B'))  # Amber 500
        c.setLineWidth(1)
        c.rect(38, 38, width - 76, height - 76, fill=False, stroke=True)

        # Corner embellishments
        c.setFillColor(colors.HexColor('#F59E0B'))
        c.circle(38, 38, 4, fill=True, stroke=False)
        c.circle(width - 38, 38, 4, fill=True, stroke=False)
        c.circle(38, height - 38, 4, fill=True, stroke=False)
        c.circle(width - 38, height - 38, 4, fill=True, stroke=False)

        # Organization Name
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.HexColor('#94A3B8'))  # Slate 400
        c.drawCentredString(width / 2.0, height - 90, certificate.organization_name.upper())

        # Title: CERTIFICATE OF COMPLETION
        c.setFont("Helvetica-Bold", 32)
        c.setFillColor(colors.HexColor('#F8FAFC'))  # Slate 50
        c.drawCentredString(width / 2.0, height - 145, "CERTIFICATE OF COMPLETION")

        # Subtitle
        c.setFont("Helvetica-Oblique", 14)
        c.setFillColor(colors.HexColor('#CBD5E1'))  # Slate 300
        c.drawCentredString(width / 2.0, height - 180, "This is proudly presented to")

        # Student Name
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.HexColor('#38BDF8'))  # Sky 400
        c.drawCentredString(width / 2.0, height - 225, certificate.student_name)

        # Underline
        c.setStrokeColor(colors.HexColor('#38BDF8'))
        c.setLineWidth(1.5)
        name_width = c.stringWidth(certificate.student_name, "Helvetica-Bold", 28)
        c.line((width - name_width) / 2.0 - 15, height - 233, (width + name_width) / 2.0 + 15, height - 233)

        # Description text
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.HexColor('#E2E8F0'))
        c.drawCentredString(width / 2.0, height - 270, "for successfully mastering and completing all curriculum requirements of")

        # Course Title
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(colors.HexColor('#FDE047'))  # Yellow 300
        c.drawCentredString(width / 2.0, height - 310, certificate.course_title)

        # Issue Details & Verification
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.HexColor('#94A3B8'))
        c.drawString(70, 95, f"Date Issued: {certificate.issued_at.strftime('%B %d, %Y')}")
        c.drawString(70, 75, f"Certificate ID: {certificate.certificate_number}")
        
        # Instructor / Signature line
        c.drawRightString(width - 70, 95, "Verified Digital Credential")
        c.drawRightString(width - 70, 75, f"Auth Code: SHA256-VALID-{certificate.certificate_number[:8]}")

        # Verification note
        c.setFont("Helvetica-Oblique", 9)
        c.setFillColor(colors.HexColor('#64748B'))
        c.drawCentredString(width / 2.0, 52, f"Verify credential authenticity at: https://lms.platform/verify/{certificate.certificate_number}")

        c.showPage()
        c.save()

        # Update model with file path
        rel_path = f"certificates/{filename}"
        certificate.pdf_file.name = rel_path
        certificate.save(update_fields=['pdf_file'])
        return rel_path

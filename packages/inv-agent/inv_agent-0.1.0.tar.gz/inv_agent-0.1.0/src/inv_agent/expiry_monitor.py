import os
from typing import List, Dict
from fpdf import FPDF
from inventory_tools import (
    get_expiring_medicines,
    get_expired_medicines,
    update_expiry_days,
    current_ist_time_str
)
from logger import log
from send_email_utils import send_email

class MedicinePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=False)
        self.add_page()
        self.set_font("Times", size=12)

    def header(self):
        if self.page_no() == 1:
            self.set_font("Times", 'B', 16)
            self.cell(0, 10, "Medicine Expiry Report", ln=True, align='C')
            self.ln(5)
            self.set_font("Times", '', 12)
            self.cell(0, 10, f"Generated on: {current_ist_time_str()}", ln=True, align='C')
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", 'I', 10)
        self.set_text_color(128)
        self.cell(0, 10, f"Page {self.page_no()}", align='C')

    def check_page_space(self, lines_count: int):
        line_height = 8
        buffer_space = 20
        needed_space = lines_count * line_height + buffer_space
        if self.get_y() + needed_space > self.h - self.b_margin:
            self.add_page()
            self.set_font("Times", size=12)

    def add_section(self, title: str, medicines: List[Dict]):
        if not medicines:
            return

        self.set_font("Times", 'B', 14)
        self.check_page_space(2)
        self.cell(0, 10, f"{title.upper()} - {len(medicines)} item(s)", ln=True)
        self.ln(3)
        self.set_font("Times", '', 12)

        for med in medicines:
            expiry_status = "EXPIRED" if med["expiry_days"] < 0 else f"{med['expiry_days']} days left"
            lines = [
                f"Name        : {med['name']}",
                f"Generic     : {med['genericName']}",
                f"Drug ID     : {med['drugId']}",
                f"Manufacturer: {med['manufacturer']}",
                f"Batch No    : {med['batchNumber']}",
                f"Expiry Date : {med['expiryDate']} ({expiry_status})",
                f"Quantity    : {med['quantity']} {med['unit']}",
                f"Location    : {med['location']}",
                "-" * 80
            ]

            self.check_page_space(len(lines) + 1)

            for line in lines:
                self.multi_cell(0, 8, line)
            self.ln(2)

        self.ln(5)

def generate_pdf_report(medicines_by_type: Dict[str, List[Dict]], output_path: str):
    pdf = MedicinePDF()

    # Add sections for each alert category
    pdf.add_section("Expired", medicines_by_type["expired"])
    pdf.add_section("Critical (0-3 days)", medicines_by_type["critical"])
    pdf.add_section("Warning (4-15 days)", medicines_by_type["warning"])
    pdf.add_section("Notice (16-30 days)", medicines_by_type["notice"])

    pdf.output(output_path)

def format_email_body(meds: Dict[str, List[Dict]], timestamp: str) -> str:
    return f"""MEDICINE EXPIRY ALERT
========================

🕒 Generated On: {timestamp}
📦 Total Medicines Affected: {sum(len(v) for v in meds.values())}

📊 Summary:
☠️ Expired                 : {len(meds['expired'])}
🚨 Critical (0–3 days)     : {len(meds['critical'])}
⚠️ Warning (4–15 days)     : {len(meds['warning'])}
📅 Notice (16–30 days)     : {len(meds['notice'])}

ACTION REQUIRED:
Please review the attached PDF report and take necessary actions immediately.

This is an automated alert from the 🏥 Medicine Inventory Monitoring System.
"""

def run_expiry_monitoring():
    log("Expiry Monitoring Started", "PDF report + email")

    try:
        update_expiry_days()

        expired = get_expired_medicines()
        critical = [m for m in get_expiring_medicines(3) if m["expiry_days"] >= 0]
        warning = [m for m in get_expiring_medicines(15) if m["expiry_days"] > 3]
        notice = [m for m in get_expiring_medicines(30) if m["expiry_days"] > 15]

        medicines_by_type = {
            "expired": expired,
            "critical": critical,
            "warning": warning,
            "notice": notice
        }

        total = sum(len(meds) for meds in medicines_by_type.values())
        if total == 0:
            log("Expiry Monitoring Completed", "No medicines requiring alert.")
            return

        timestamp = current_ist_time_str()
        date_slug = current_ist_time_str().split(" ")[0]
        pdf_filename = f"medicine_expiry_report_{date_slug}.pdf"
        pdf_path = os.path.join(os.getcwd(), pdf_filename)

        generate_pdf_report(medicines_by_type, pdf_path)

        body = format_email_body(medicines_by_type, timestamp)
        subject = f"🚨 EXPIRY ALERT REPORT [{date_slug}] - {total} Items"

        result = send_email(
            subject=subject,
            body=body,
            recipient_type="manager",
            attachment_path=pdf_path
        )
        log("Expiry Monitoring Completed", f"PDF generated: {pdf_filename}")
        log(f"Email status is {result}")

    except Exception as e:
        msg = f"Error: {str(e)}"
        log("Expiry Monitoring Error", msg)

if __name__ == "__main__":
    run_expiry_monitoring()
from smume.student_plan import StudentPlan
from smume.graph_builder import build_graph
import os
import re

class MEPlanDocument:
    def __init__(self, student_plan: StudentPlan, output_dir=".", filename="ME-Plan-Document"):
        self.plan = student_plan
        self.output_dir = output_dir
        self.filename = filename
        self.report = None
        self.graph = None

        os.makedirs(self.output_dir, exist_ok=True)

    def generate_report(self):
        """Generate HTML report from the student plan."""
        from smume.report import Report
        report = Report(self.plan)
        self.report = report

    def generate_graph(self):
        """Generate SVG graph from the student plan."""
        graph = build_graph(self.plan)
        raw_svg = graph.pipe(format="svg").decode('utf-8')

        # Remove hardcoded width/height from <svg ...>
        raw_svg = re.sub(r'\s(width|height)="[^"]+"', '', raw_svg)
        raw_svg = re.sub(r'<svg', '<svg style="width:100%;height:auto;"', raw_svg, count=1)

        self.graph = raw_svg

    def create_combined_document(self, styles_external=False):
        """Combine HTML report and embedded SVG graph into a single HTML string."""
        if not self.report:
            self.generate_report()
        if not self.graph:
            self.generate_graph()

        svg_content = f'<div class="graph-container">{self.graph}</div>'

        combined_html = f"""
        <html>
        <head><meta charset="utf-8"><title>Student Plan</title>
        {self.css_styles()}
        </head>
        <body>
            <div class="container">
                <h1 class="my-4">Student Plan for {self.plan.student_name}</h1>
                <div class="report-container">
                    {self.report.generate_html()}
                </div>
                <h2>3. Flowchart</h2>
                {svg_content}
            </div>
        </body>
        </html>
        """

        return combined_html
    
    def save_combined_document(self, styles_external=False):
        """Save the combined HTML document to a file."""
        combined_html = self.create_combined_document(styles_external=styles_external)
        combined_path = os.path.join(self.output_dir, f"{self.filename}.html")
        with open(combined_path, "w") as f:
            f.write(combined_html)
        return combined_path

    def css_styles(self):
        """Return CSS styles for the report."""
        high_level_styles = """
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
        <style>
            body { font-family: Palatino, serif; font-size: 10pt; }
            .graph-container { margin-top: 20px; }
            h1, h2, h3, h4 { color: #333; font-size: 10pt; font-weight: bold; margin-top: 20px; }
            h1 { font-size: 12pt; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 2px 0; }
            ul ul li { margin-left: 7px; }

            @media print {
                body {
                    # margin: 0.5in;
                }
                .graph-container {
                    page-break-inside: avoid;
                    break-inside: avoid;
                    max-width: 100%;
                }
                svg {
                    page-break-inside: avoid;
                    break-inside: avoid;
                    width: 100%;
                    height: auto;
                }
                .report-container {
                    page-break-before: avoid;
                }
            }

            @page {
                size: Letter;
                margin: .25in .25in .25in .25in;
                @bottom-right {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 10pt;
                }
            }
        </style>
        """
        return high_level_styles + self.report.css_styles()
    
    def export_combined_document_pdf(self):
        """Export the combined HTML document to PDF."""
        # Use WeasyPrint to convert HTML to PDF. Warning: This requires the WeasyPrint library to be installed. 
        print("Warning: Exporting to PDF requires WeasyPrint to be installed. See https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation.")
        from weasyprint import HTML
        combined_html = self.create_combined_document(styles_external=False)
        output_pdf_path = os.path.join(self.output_dir, f"{self.filename}.pdf")
        print(f"Exporting combined document to PDF: {output_pdf_path}")
        HTML(string=combined_html).write_pdf(output_pdf_path)
        return output_pdf_path
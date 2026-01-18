from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, 'UIDAI Data Hackathon 2026 - Digital India Readiness Index', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(2)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def reset_x(self):
        """Reset X position to left margin"""
        self.set_x(self.l_margin)

    def add_title(self, title):
        self.reset_x()
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(30, 30, 100)
        self.multi_cell(0, 10, title)
        self.ln(5)
        
    def add_section(self, title, level=2):
        self.reset_x()
        self.set_font('Helvetica', 'B', 13 if level == 2 else 11)
        if level == 2:
            self.set_text_color(30, 100, 60)
        else:
            self.set_text_color(60, 60, 120)
        self.multi_cell(0, 7, title)
        self.ln(2)
        
    def add_text(self, text):
        self.reset_x()
        self.set_font('Helvetica', '', 9)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, text.strip())
        self.ln(2)
        
    def add_bullet(self, text):
        self.reset_x()
        self.set_font('Helvetica', '', 9)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, "  * " + text.strip())
        
    def add_table(self, headers, rows):
        self.reset_x()
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(230, 230, 230)
        
        total_width = 180
        col_count = len(headers)
        col_width = total_width / col_count
        
        for h in headers:
            self.cell(col_width, 6, h[:25], border=1, align='C', fill=True)
        self.ln()
        self.reset_x()
        
        self.set_font('Helvetica', '', 8)
        for row in rows[:12]:
            for cell in row:
                self.cell(col_width, 5, str(cell)[:25], border=1, align='L')
            self.ln()
            self.reset_x()
        self.ln(3)

    def add_image_from_file(self, img_path, caption=""):
        self.reset_x()
        if os.path.exists(img_path):
            try:
                self.image(img_path, x=15, w=180)
                if caption:
                    self.set_font('Helvetica', 'I', 8)
                    self.set_text_color(100, 100, 100)
                    self.cell(0, 5, caption, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                self.ln(5)
            except Exception as e:
                print(f"Warning: Could not add image {img_path}: {e}")

def main():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title
    pdf.add_title("Digital India Readiness Index - Executive Summary")
    
    # Meta info
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, "Dataset Period: Multi-source UIDAI data across 10 datasets", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, "Total States/UTs Analyzed: 36", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, "Analyst: Meet Wadekar", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    
    # Problem Statement
    pdf.add_section("Problem Statement", 2)
    pdf.add_text("The UIDAI has deployed Aadhaar as the cornerstone of India's digital infrastructure, enabling citizen services including PDS, MGNREGS, DBT, and MSME Integration.")
    pdf.add_text("Core Challenge: Despite widespread Aadhaar enrollment (>99% nationally), significant disparities exist in utilization across states, leading to digital exclusion, inefficient subsidy delivery, and regional imbalances.")
    pdf.add_text("This analysis quantifies these disparities through a composite Digital Readiness Index.")
    
    # Hypothesis
    pdf.add_section("Hypothesis", 2)
    pdf.add_text("Primary Hypothesis: States with higher Aadhaar integration across PDS, MGNREGS, and MSME ecosystems demonstrate stronger digital readiness and more efficient welfare delivery.")
    pdf.add_text("Secondary Hypotheses:")
    pdf.add_bullet("North-Eastern states lag significantly in Aadhaar-based service delivery")
    pdf.add_bullet("States with 100% ration card seeding show high ABPS coverage")
    pdf.add_bullet("MSME density correlates positively with overall digital readiness")
    pdf.ln(3)
    
    # Key Metrics
    pdf.add_section("Key Metrics at a Glance", 2)
    pdf.add_table(
        ['Metric', 'Value'],
        [
            ['Total States/UTs Analyzed', '36'],
            ['Avg Digital Readiness Index', '70.9'],
            ['Median Digital Readiness', '78.1'],
            ['Standard Deviation', '24.3'],
        ]
    )
    
    pdf.add_table(
        ['MGNREGS ABPS Metric', 'Value'],
        [
            ['Total Active Workers', '1,496.9 Lakh'],
            ['ABPS Eligible Workers', '1,043.3 Lakh'],
            ['National ABPS Coverage', '69.7%'],
            ['Workers NOT Covered', '453.6 Lakh'],
        ]
    )
    
    # Top 10 States
    pdf.add_page()
    pdf.add_section("Top 10 States by Digital Readiness", 2)
    pdf.add_table(
        ['Rank', 'State', 'Score', 'Key Strength'],
        [
            ['1', 'Tamil Nadu', '94.5', 'Full PDS + MSME'],
            ['2', 'Andhra Pradesh', '91.1', '100% coverage'],
            ['3', 'Telangana', '91.0', 'MGNREGS'],
            ['4', 'Maharashtra', '89.3', 'MSME + PDS'],
            ['5', 'Puducherry', '86.7', 'FPS automation'],
            ['6', 'Gujarat', '86.5', 'Strong MSME'],
            ['7', 'Punjab', '86.4', 'Complete PDS'],
            ['8', 'Karnataka', '85.7', 'Balanced'],
            ['9', 'Chhattisgarh', '85.1', 'Beneficiary'],
            ['10', 'Haryana', '84.7', 'FPS automation'],
        ]
    )
    
    # Add state rankings image
    pdf.add_image_from_file('assets/state_rankings.png', 'Top 10 and Bottom 10 States')
    
    # Bottom 10 States
    pdf.add_page()
    pdf.add_section("Bottom 10 States Requiring Intervention", 2)
    pdf.add_table(
        ['Rank', 'State', 'Score', 'Primary Gap'],
        [
            ['27', 'West Bengal', '58.9', 'Low seeding'],
            ['28', 'J and K', '54.9', 'Low ABPS'],
            ['29', 'Arunachal', '51.9', '44% ration'],
            ['30', 'Manipur', '49.9', 'Low ABPS'],
            ['31', 'Mizoram', '47.8', 'Limited MSME'],
            ['32', 'Nagaland', '47.1', '57% ration'],
            ['33', 'DN Haveli', '32.9', 'Missing data'],
            ['34', 'Daman Diu', '27.4', 'Missing data'],
            ['35', 'Meghalaya', '13.9', '0% seeding'],
            ['36', 'Assam', '6.7', '0% seeding'],
        ]
    )
    
    # Critical Findings
    pdf.add_section("Top 5 Critical Findings", 2)
    
    pdf.add_section("1. PDS Digital Exclusion (HIGH)", 3)
    pdf.add_text("Issue: Assam and Meghalaya have 0% Aadhaar-ration card seeding. Impact: 40+ lakh ration cards without digital linkage. Recommendation: Emergency enrollment drives in NE states.")
    
    pdf.add_section("2. MGNREGS ABPS Gap (HIGH)", 3)
    pdf.add_text("Issue: 453.6 lakh workers NOT eligible for ABPS. Only 69.7% of active workers are ABPS-ready. Recommendation: Expedite Aadhaar seeding for remaining 30%.")
    
    pdf.add_section("3. North-Eastern States Lagging (HIGH)", 3)
    pdf.add_text("Issue: NE States avg score 40 vs national avg 70.9. Recommendation: Door-to-door enrollment programs.")
    
    # Visualizations
    pdf.add_page()
    pdf.add_section("Visualizations", 2)
    pdf.add_image_from_file('assets/ne_states_analysis.png', 'NE States Digital Gap')
    
    pdf.add_page()
    pdf.add_image_from_file('assets/heatmap_matrix.png', 'Digital Readiness Heatmap')
    
    pdf.add_page()
    pdf.add_image_from_file('assets/radar_chart.png', 'Top 3 vs Bottom 3 States')
    
    pdf.add_page()
    pdf.add_image_from_file('assets/gap_analysis.png', 'Aadhaar vs PDS Readiness')
    
    pdf.add_page()
    pdf.add_image_from_file('assets/correlation_matrix.png', 'Correlation Matrix')
    
    # Strategic Recommendations
    pdf.add_page()
    pdf.add_section("Strategic Recommendations", 2)
    
    pdf.add_section("Immediate (0-3 months)", 3)
    pdf.add_bullet("Emergency Aadhaar seeding in Assam and Meghalaya")
    pdf.add_bullet("Mobile enrollment units in remote NE areas")
    pdf.add_bullet("Fast-track ABPS integration for 453+ lakh workers")
    pdf.ln(3)
    
    pdf.add_section("Short-term (3-6 months)", 3)
    pdf.add_bullet("State-specific programs for bottom 10 states")
    pdf.add_bullet("FPS operator training in low-automation states")
    pdf.add_bullet("Vernacular awareness campaigns")
    pdf.ln(3)
    
    pdf.add_section("Medium-term (6-12 months)", 3)
    pdf.add_bullet("Target 95% ration card seeding nationally")
    pdf.add_bullet("Achieve 90% MGNREGS ABPS coverage")
    pdf.add_bullet("Reduce regional disparity to under 20 points")
    pdf.ln(3)
    
    # Methodology
    pdf.add_section("Methodology", 2)
    pdf.add_table(
        ['Dimension', 'Weight'],
        [
            ['Aadhaar Coverage', '20%'],
            ['PDS Readiness', '35%'],
            ['MGNREGS ABPS', '30%'],
            ['MSME Density', '15%'],
        ]
    )
    
    # Save PDF
    pdf.output('EXECUTIVE_SUMMARY.pdf')
    print("PDF generated successfully: EXECUTIVE_SUMMARY.pdf")

if __name__ == "__main__":
    main()

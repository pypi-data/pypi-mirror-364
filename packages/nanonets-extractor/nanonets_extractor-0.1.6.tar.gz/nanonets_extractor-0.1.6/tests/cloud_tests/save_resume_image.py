#!/usr/bin/env python3
"""
Helper script to create a test resume image for the extraction tests.
This creates a simple text-based image representation of the resume.
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_resume_image():
    """Create a test resume image based on the provided description."""
    
    # Resume content based on the description
    resume_text = """SYLVIE (XIAOTONG) HUANG
Milpitas, CA 95035
(312) 608-8011
xhuang5@luc.edu

OBJECTIVE
Enthusiastic, business-minded HR professional experienced in global mobility, recruiting, performance management, employee relations, training and development, onboarding, organizational development, HRIS/CRM systems, payroll and benefits, reporting and analytics, and HR compliance. I'm looking to further my professional career with a challenging HR position that contributes to the outstanding success of the organization.

EDUCATION
Loyola University Chicago, Quinlan School of Business, Chicago, IL
Master of Science in Human Resources, 2014-2016
Classes Taken: Compensation, Incentive Pay and Employee Benefits, Financial Accounting, Labor Relations, HR Law, Staffing, HR Development, Performance Management, Global HR.

Northeast Agricultural University, College of Humanities and Law, Harbin, Heilongjiang, China
Bachelor of Management in Human Resource Management, 2009-2013
Bachelor of Law, 2010-2013

PROFESSIONAL EXPERIENCE
HRBP/Global HR Operations
SiFive, Inc., Santa Clara, CA
July 2021-Present

• Act as the point of contact for all HR related matters globally including the US, UK, France and other EU countries, Taiwan, India, Japan. Work in collaboration with leadership and other HR team members within and outside the US.
• Work closely with cross-functional teams, including talent acquisition, finance, legal, and IT to ensure cohesion across different operational areas.
• Develop, implement, and maintain HR policies, procedures and guidelines to ensure compliance with legal and regulatory requirements.
• Serve as the escalation point for the HR Shared Services team providing day-to-day support to employees in areas including Benefits, Leaves of Absence, and general HR operations.
• Manage corporate global mobility program, including global immigration and relocation programs with focus on planning, efficiency, cost effectiveness, and compliance.
• Lead focal review process and manage performance review program for global workforce. Partner with leadership and outside counsel to review the compensation structure, complete salary benchmarking, develop communication methods, and process compensation changes.
• Own benefits administration and carrier management. Partner with management and outside counsel for benefits plan review, carrier selection and transition, and benefits renewal. Work with cross-functional teams to ensure a smooth process for plan implementation and back-end activities.
• Serve as the advisor to employees and managers for employee relations related inquiries. Work with outside counsel to resolve employment law issues and employee relation cases.
• Partner with the HRIS team for Workday implementation and testing. Responsible for data accuracy and business process setup.
• Involve in M&A activities including preparation of the M&A, employment and data transition, and employee engagement. Guide employees and management through the transition process.

HR/Account Manager
Intellipro Group Inc., Santa Clara, CA
August 2018-July 2021

HR Activities: Recruiting, Training, Performance Review, ER, Compliance, Payroll, and Benefits

• Drive talent development plan and partner with VP and HR team to support full cycle of recruiting process for multiple departments.
• Serve as the official on-boarding representative. Facilitate everything from new hire paperwork to the actual day-of orientation. Responsible for all new hire questions and concerns post orientation.
• Design and implement training program for internal stakeholders. Create training manual and provide business related sessions to facilitate new learning and change of the industry.
• Provide compliance/ER training sessions to all employees align with industry knowledge and company's business nature.
• Partner with team leaders and HR team to revise performance evaluation plan in order to support employees on performance improvement.
• Establish targets and goals for the team, including KPIs and metrics, analyze data to identify performance strengths, weaknesses, trends and forecasting."""

    # Create image
    width, height = 800, 1200
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        # Try to use a system font
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
    except:
        try:
            # Try alternative font paths
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            # Fallback to default font
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
    
    # Draw text
    lines = resume_text.split('\n')
    y_position = 50
    line_height = 20
    
    for line in lines:
        if line.strip() == "":
            y_position += line_height // 2
            continue
            
        # Check if it's a title/section header
        if line.isupper() and len(line) < 50:
            draw.text((50, y_position), line, fill='black', font=title_font)
            y_position += line_height + 5
        else:
            # Wrap long lines
            words = line.split()
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width > width - 100:  # Leave margin
                    if current_line:
                        draw.text((50, y_position), current_line, fill='black', font=font)
                        y_position += line_height
                        current_line = word
                    else:
                        # Single word is too long, draw it anyway
                        draw.text((50, y_position), word, fill='black', font=font)
                        y_position += line_height
                else:
                    current_line = test_line
            
            if current_line:
                draw.text((50, y_position), current_line, fill='black', font=font)
                y_position += line_height
        
        # Check if we've exceeded image height
        if y_position > height - 50:
            break
    
    # Save the image
    filename = "resume.jpg"
    image.save(filename, "JPEG", quality=95)
    print(f"✅ Resume image created: {filename}")
    print(f"📏 Image size: {width}x{height} pixels")
    print(f"💾 File size: {os.path.getsize(filename)} bytes")
    
    return filename


if __name__ == "__main__":
    print("🖼️ Creating test resume image...")
    create_resume_image()
    print("\n🎯 You can now run the test script:")
    print("   python test_cloud_extraction.py") 
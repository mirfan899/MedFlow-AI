from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from datetime import datetime

def generate_soap_pdf(soap_data: dict, agent2_output: dict, filename: str = './medical_soap_note.pdf'):
    """
    Generates a PDF SOAP note.
    
    Args:
        soap_data: The dictionary containing the SOAP note (S, O, A, P).
        agent2_output: The full output from Agent 2, containing recommendations and safety notices.
        filename: Output filename for the PDF.
    """
    
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            topMargin=0.5*inch, bottomMargin=0.5*inch,
                            leftMargin=0.75*inch, rightMargin=0.75*inch)

    # Container for the 'Flowable' objects
    elements = []

    # Get standard styles
    styles = getSampleStyleSheet()

    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=colors.HexColor('#2c3e50'),
        borderPadding=4,
        backColor=colors.HexColor('#ecf0f1')
    )

    subheader_style = ParagraphStyle(
        'SubHeader',
        parent=styles['Heading3'],
        fontSize=10,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=4,
        spaceBefore=6,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )

    alert_style = ParagraphStyle(
        'Alert',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#c0392b'),
        spaceAfter=6,
        fontName='Helvetica-Bold',
        backColor=colors.HexColor('#fadbd8'),
        borderWidth=1,
        borderColor=colors.HexColor('#c0392b'),
        borderPadding=6
    )

    # Title
    elements.append(Paragraph("MedFlow AI", title_style))
    elements.append(Paragraph("SOAP NOTE", ParagraphStyle('Subtitle', parent=styles['Heading2'], 
                                                           fontSize=14, alignment=TA_CENTER, 
                                                           textColor=colors.HexColor('#1a1a1a'),
                                                           fontName='Helvetica-Bold', spaceAfter=6)))
    elements.append(Spacer(1, 0.1*inch))

    # Patient Information Header
    patient_info_data = [
        ['Date:', datetime.now().strftime('%B %d, %Y')],
        ['Patient ID:', '[Patient ID]'],
        ['Provider:', '[Provider Name]']
    ]

    patient_table = Table(patient_info_data, colWidths=[1.5*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 0.2*inch))

    # ============= SUBJECTIVE =============
    elements.append(Paragraph("S — SUBJECTIVE", header_style))
    elements.append(Spacer(1, 0.1*inch))
    
    # We expect soap_data to have 'subjective', 'objective', 'assessment', 'plan' keys
    # Agent 2 output structure: {'soap_note': {'subjective': ...}, ...}
    # But here we pass soap_data which IS the 'soap_note' part of Agent 2 output
    
    subjective = soap_data.get('subjective', {})
    
    # Chief Complaint
    elements.append(Paragraph("<b>Chief Complaint:</b>", subheader_style))
    elements.append(Paragraph(subjective.get('chief_complaint', 'Missing'), body_style))

    # History of Present Illness
    elements.append(Paragraph("<b>History of Present Illness:</b>", subheader_style))
    elements.append(Paragraph(subjective.get('history_of_present_illness', 'Missing'), body_style))

    # Past Medical History
    elements.append(Paragraph("<b>Past Medical History:</b>", subheader_style))
    pmh_text = subjective.get('past_medical_history', 'Missing')
    elements.append(Paragraph(pmh_text, body_style))

    # Medications
    elements.append(Paragraph("<b>Current Medications:</b>", subheader_style))
    medications = subjective.get('medications', [])
    if medications:
        med_text = ", ".join(medications) if isinstance(medications, list) else str(medications)
        elements.append(Paragraph(med_text, body_style))
    else:
        elements.append(Paragraph("None reported", body_style))

    # Allergies
    elements.append(Paragraph("<b>Allergies:</b>", subheader_style))
    allergies = subjective.get('allergies', [])
    if allergies:
        allergy_text = ", ".join(allergies) if isinstance(allergies, list) else str(allergies)
        elements.append(Paragraph(allergy_text, body_style))
    else:
        elements.append(Paragraph("No known drug allergies (NKDA)", body_style))

    # Social History
    social_history = subjective.get('social_history', '')
    if social_history and social_history != "Missing":
        elements.append(Paragraph("<b>Social History:</b>", subheader_style))
        elements.append(Paragraph(social_history, body_style))

    # Family History
    family_history = subjective.get('family_history', '')
    if family_history and family_history != "Missing":
        elements.append(Paragraph("<b>Family History:</b>", subheader_style))
        elements.append(Paragraph(family_history, body_style))

    # Review of Systems
    ros = subjective.get('review_of_systems', '')
    if ros and ros != "Missing":
        elements.append(Paragraph("<b>Review of Systems:</b>", subheader_style))
        elements.append(Paragraph(ros, body_style))

    elements.append(Spacer(1, 0.15*inch))

    # ============= OBJECTIVE =============
    elements.append(Paragraph("O — OBJECTIVE", header_style))
    elements.append(Spacer(1, 0.1*inch))
    
    objective = soap_data.get('objective', {})

    # Vital Signs
    elements.append(Paragraph("<b>Vital Signs:</b>", subheader_style))
    vitals = objective.get('vital_signs', {})

    vital_data = []
    if vitals.get('blood_pressure') and vitals.get('blood_pressure') != "Missing":
        vital_data.append(['Blood Pressure:', vitals.get('blood_pressure')])
    if vitals.get('heart_rate') and vitals.get('heart_rate') != "Missing":
        vital_data.append(['Heart Rate:', vitals.get('heart_rate')])
    if vitals.get('respiratory_rate') and vitals.get('respiratory_rate') != "Missing":
        vital_data.append(['Respiratory Rate:', vitals.get('respiratory_rate')])
    if vitals.get('temperature') and vitals.get('temperature') != "Missing":
        vital_data.append(['Temperature:', vitals.get('temperature')])
    if vitals.get('oxygen_saturation') and vitals.get('oxygen_saturation') != "Missing":
        vital_data.append(['Oxygen Saturation:', vitals.get('oxygen_saturation')])

    if vital_data:
        vital_table = Table(vital_data, colWidths=[2*inch, 3*inch])
        vital_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        elements.append(vital_table)
        elements.append(Spacer(1, 0.1*inch))

    # Physical Examination
    physical_exam = objective.get('physical_exam', '')
    if physical_exam and physical_exam != "Missing":
        elements.append(Paragraph("<b>Physical Examination:</b>", subheader_style))
        elements.append(Paragraph(physical_exam, body_style))

    # Imaging
    imaging = objective.get('imaging', {})
    has_imaging = False
    imaging_content = []

    if imaging.get('chest_xray') and imaging.get('chest_xray') != "Missing":
        has_imaging = True
        imaging_content.append(Paragraph(f"<b>Chest X-Ray:</b> {imaging['chest_xray']}", body_style))

    other_imaging = imaging.get('other_imaging', '')
    if other_imaging and other_imaging != 'Missing':
        has_imaging = True
        imaging_content.append(Paragraph(f"<b>Other Imaging:</b> {other_imaging}", body_style))

    if has_imaging:
        elements.append(Paragraph("<b>Imaging Studies:</b>", subheader_style))
        for img in imaging_content:
            elements.append(img)

    # Laboratory Results
    lab_results = objective.get('laboratory_results', '')
    if lab_results and lab_results != "Missing":
        elements.append(Paragraph("<b>Laboratory Results:</b>", subheader_style))
        elements.append(Paragraph(lab_results, body_style))

    elements.append(Spacer(1, 0.15*inch))

    # ============= ASSESSMENT =============
    elements.append(Paragraph("A — ASSESSMENT", header_style))
    elements.append(Spacer(1, 0.1*inch))
    assessment_text = soap_data.get('assessment', 'Missing')
    if isinstance(assessment_text, dict): # Handle if it's structured
        assessment_text = json.dumps(assessment_text)
    elements.append(Paragraph(str(assessment_text), body_style))

    elements.append(Spacer(1, 0.15*inch))

    # ============= PLAN =============
    elements.append(Paragraph("P — PLAN", header_style))
    elements.append(Spacer(1, 0.1*inch))
    plan_text = soap_data.get('plan', 'Missing')
    if isinstance(plan_text, dict):
         plan_text = json.dumps(plan_text)
    elements.append(Paragraph(str(plan_text), body_style))

    # Lifestyle Recommendations
    if 'lifestyle_recommendations' in agent2_output:
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("<b>Lifestyle Recommendations:</b>", subheader_style))
        lifestyle = agent2_output['lifestyle_recommendations']
        
        if lifestyle.get('food'):
            elements.append(Paragraph(f"<b>Dietary:</b> {lifestyle['food']}", body_style))
        if lifestyle.get('exercise'):
            elements.append(Paragraph(f"<b>Exercise:</b> {lifestyle['exercise']}", body_style))
        if lifestyle.get('clothing'):
            elements.append(Paragraph(f"<b>Clothing:</b> {lifestyle['clothing']}", body_style))
        if lifestyle.get('music'):
            elements.append(Paragraph(f"<b>Stress Management:</b> {lifestyle['music']}", body_style))
        if lifestyle.get('fragrance'):
            elements.append(Paragraph(f"<b>Environmental:</b> {lifestyle['fragrance']}", body_style))

    # Additional Notes
    if agent2_output.get('additional_notes'):
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph("<b>Additional Notes:</b>", subheader_style))
        elements.append(Paragraph(agent2_output['additional_notes'], body_style))

    # Safety Notice
    elements.append(Spacer(1, 0.15*inch))
    if agent2_output.get('safety_notice'):
        elements.append(Paragraph("<b>SAFETY ALERT</b>", alert_style))
        elements.append(Paragraph(agent2_output['safety_notice'], alert_style))

    # Footer
    elements.append(Spacer(1, 0.2*inch))
    footer_text = """
    <para alignment="center" fontSize="8" textColor="#7f8c8d">
    <i>This SOAP note is for medical documentation purposes. All information should be verified and supplemented with complete clinical assessment.</i><br/>
    <i>Document generated on: {}</i>
    </para>
    """.format(datetime.now().strftime('%B %d, %Y at %H:%M'))
    elements.append(Paragraph(footer_text, body_style))

    # Build PDF
    doc.build(elements)
    print(f"PDF generated: {filename}")

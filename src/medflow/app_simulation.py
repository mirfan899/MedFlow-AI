import os
import sys

# Ensure the 'src' directory is in sys.path so 'medflow' package can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import json
import gradio as gr
from PIL import Image
from medflow.utils.pdf_generator import generate_soap_pdf

# Project root directory for storing PDFs
PROJECT_ROOT = os.path.abspath(os.path.join(src_dir, ".."))
PDF_DIR = os.path.join(PROJECT_ROOT, "pdfs")

# Ensure the 'pdfs' directory exists
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

def sanitize_filename(name):
    return "".join([c for c in name if c.isalnum() or c in (" ", "-", "_")]).strip().replace(" ", "_")

def simulate_agent1(name, pid, age, gender, symptoms, duration, severity, history, medications, bp, hr, image):
    """
    Simulates Agent 1 (SoapNoteGenerator) by structuring the input data.
    """
    import json
    symptoms_list = [s.strip() for s in symptoms.split(",")] if symptoms else []
    
    # Mock Subjective
    subjective = {
        "chief_complaint": symptoms_list[0] if symptoms_list else "Not provided",
        "history_of_present_illness": f"Patient is a {age} year old {gender} presenting with {symptoms} for {duration}. Severity is {severity}.",
        "past_medical_history": history if history else "None reported",
        "medications": [m.strip() for m in medications.split(",")] if medications else [],
        "allergies": "No known drug allergies (NKDA)",
        "social_history": "Not provided",
        "family_history": "Not provided",
        "review_of_systems": "Constitutional: Positive for fatigue. Cardiovascular: Positive for chest discomfort."
    }
    
    # Mock Objective
    objective = {
        "vital_signs": {
            "blood_pressure": bp,
            "heart_rate": hr,
            "respiratory_rate": "16 bpm",
            "temperature": "98.6 F"
        },
        "physical_exam": "General appearance: Well-developed, well-nourished. Cardiovascular: S1, S2 audible, no murmurs.",
        "imaging": {
            "chest_xray": "Normal" if not image else "Imaging provided for review",
            "other_imaging": "N/A"
        },
        "laboratory_results": "Pending"
    }
    
    # Mock Assessment
    assessment = f"Differential diagnosis includes: 1. Angina pectoris 2. GERD 3. Musculoskeletal chest pain. The presence of {symptoms} in the context of {history} requires further evaluation."
    
    soap_note_partial = {
        "patient_name": name,
        "patient_id": pid,
        "subjective": subjective,
        "objective": objective,
        "assessment": assessment,
        "missing_information": ["Complete laboratory workup", "Detail family history"],
        "safety_notice": "Seek immediate emergency care if symptoms worsen or include crushing chest pain, radiating pain, or severe diaphoresis."
    }
    
    return soap_note_partial, json.dumps(soap_note_partial)

def simulate_agent2(soap_note_partial_json, med_plan, lab_tests, follow_up, ethnicity):
    """
    Simulates Agent 2 (PlanAnalyzer) and generates the final PDF.
    """
    import json
    if not soap_note_partial_json:
        return {"error": "No assessment data found. Please run Step 1 first."}, None
        
    try:
        soap_note_partial = json.loads(soap_note_partial_json)
        name = soap_note_partial.get("patient_name", "Unknown")
        pid = soap_note_partial.get("patient_id", "Unknown")
        
        meds_list = [m.strip() for m in med_plan.split(",")] if med_plan else []
        labs_list = [l.strip() for l in lab_tests.split(",")] if lab_tests else []
        
        # Build Final Soap Note with Plan
        final_soap_note = soap_note_partial.copy()
        final_soap_note["plan"] = {
            "medications": meds_list,
            "lab_tests": labs_list,
            "follow_up": follow_up
        }
        
        # Mock Agent 2 Analysis Output
        final_output = {
            "soap_note": final_soap_note,
            "medication_review": {
                "confidence_score": 95,
                "rationale": "Medications align well with the suspected GERD/Cardiovascular differential."
            },
            "test_validation": [
                {"test": t, "relevance_score": 90, "rationale": "Essential for rule-out process."} for t in labs_list
            ],
            "lifestyle_recommendations": {
                "food": "Avoid spicy food and caffeine. Focus on small, frequent meals.",
                "exercise": "Gentle walking allowed. Avoid strenuous activity until cardiac clearance.",
                "clothing": "Loose-fitting clothing to avoid abdominal pressure.",
                "music": "Relaxing classical music to manage stress.",
                "fragrance": "Lavender for calming environment."
            },
            "additional_notes": f"Patient ethnicity: {ethnicity}. Tailor dietary advice accordingly.",
            "safety_notice": soap_note_partial.get("safety_notice", "Consult your physician immediately.")
        }
        
        # Generate PDF with unique name
        clean_name = sanitize_filename(name)
        clean_pid = sanitize_filename(pid)
        pdf_name = f"soap_note_{clean_name}_{clean_pid}.pdf"
        pdf_filename = os.path.join(PDF_DIR, pdf_name)
        
        generate_soap_pdf(final_soap_note, final_output, filename=pdf_filename, 
                          patient_name=name, patient_id=pid)
        
        return final_output, pdf_filename
    except Exception as e:
        return {"error": f"Error in simulation: {e}"}, None

# UI Definition
with gr.Blocks(title="MedFlow AI - Clinical Assistant (Demo Mode)") as demo:
    gr.Markdown("# 🏥 MedFlow AI")
    gr.Markdown("An AI-powered clinical assistant for generating and analyzing SOAP notes (Demo Mode).")
    
    with gr.Tab("Step 1: Patient Assessment"):
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    patient_name = gr.Textbox(label="Patient Name", value="John Doe")
                    p_id = gr.Textbox(label="Patient ID", value="P-12345")
                age = gr.Number(label="Age", value=45)
                gender = gr.Dropdown(label="Gender", choices=["Male", "Female", "Other"], value="Male")
                symptoms = gr.Textbox(label="Symptoms (comma separated)", placeholder="Chest discomfort, Fatigue", value="Chest discomfort, Shortness of breath during exertion, Fatigue")
                duration = gr.Textbox(label="Duration", value="2 weeks")
                severity = gr.Dropdown(label="Severity", choices=["Mild", "Moderate", "Severe"], value="Moderate")
                history = gr.Textbox(label="Medical History (comma separated)", value="Hypertension")
                meds = gr.Textbox(label="Current Medications (comma separated)", value="")
                bp = gr.Textbox(label="Blood Pressure", value="145/90")
                hr = gr.Textbox(label="Heart Rate", value="92 bpm")
                input_image = gr.Image(type="pil", label="Medical Scan (Optional)")
                
                generate_draft_btn = gr.Button("📝 Generate Draft SOAP", variant="primary")
            
            with gr.Column():
                draft_output_json = gr.JSON(label="Structured Assessment (Simulated Agent 1 Output)")
                draft_output_raw = gr.Textbox(label="Hidden Draft JSON (for Step 2)", visible=False)
                
        generate_draft_btn.click(
            simulate_agent1, 
            inputs=[patient_name, p_id, age, gender, symptoms, duration, severity, history, meds, bp, hr, input_image],
            outputs=[draft_output_json, draft_output_raw]
        )

    with gr.Tab("Step 2: Doctor's Plan & Finalization"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### Input Doctor's Plan")
                plan_meds = gr.Textbox(label="Prescribed Medications (comma separated)", value="Omeprazole 20mg once daily")
                plan_labs = gr.Textbox(label="Lab Tests (comma separated)", value="H. pylori test, CBC")
                plan_followup = gr.Textbox(label="Follow-up", value="2 weeks")
                ethnicity = gr.Textbox(label="Patient Ethnicity", value="South Asian")
                
                finalize_btn = gr.Button("✅ Finalize & Generate PDF", variant="primary")
            
            with gr.Column():
                final_output_json = gr.JSON(label="Final Analysis (Simulated Agent 2 Output)")
                pdf_download = gr.File(label="Download Final SOAP Note PDF")

        finalize_btn.click(
            simulate_agent2,
            inputs=[draft_output_raw, plan_meds, plan_labs, plan_followup, ethnicity],
            outputs=[final_output_json, pdf_download]
        )

    gr.Examples(
        examples=[
            ["John Doe", "P-12345", 45, "Male", "Chest discomfort, Fatigue", "2 weeks", "Moderate", "Hypertension", "", "145/90", "92 bpm", None],
            ["Jane Smith", "P-67890", 30, "Female", "Sore throat, Fever", "3 days", "Mild", "None", "Vitamins", "120/80", "72 bpm", None]
        ],
        inputs=[patient_name, p_id, age, gender, symptoms, duration, severity, history, meds, bp, hr, input_image]
    )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())

import os
import sys

# Ensure the 'src' directory is in sys.path so 'medflow' package can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, ".."))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

import json
import torch
import gradio as gr
from PIL import Image
from transformers import pipeline
from huggingface_hub import login
from medflow.agents.agent1 import SoapNoteGenerator
from medflow.agents.agent2 import PlanAnalyzer
from medflow.utils.pdf_generator import generate_soap_pdf

# Setup organized PDF storage
PROJECT_ROOT = os.path.abspath(os.path.join(src_dir, ".."))
PDF_DIR = os.path.join(PROJECT_ROOT, "pdfs")
if not os.path.exists(PDF_DIR):
    os.makedirs(PDF_DIR)

# Initialize Model & Agents
print("Initializing MedFlow AI Production Pipeline...")
hf_token = os.getenv("HF_TOKEN")
if hf_token:
    login(token=hf_token)

try:
    pipe = pipeline(
        "image-text-to-text",
        model="google/medgemma-4b-it",
        torch_dtype=torch.bfloat16,
        device="cuda" if torch.cuda.is_available() else "cpu",
    )
    generator = SoapNoteGenerator(pipe)
    analyzer = PlanAnalyzer(pipe)
except Exception as e:
    print(f"Error loading model: {e}")
    # Fallback to demo mode or error UI if needed, but here we assume user wants the real thing
    generator = None
    analyzer = None

def sanitize_filename(name):
    return "".join([c for c in name if c.isalnum() or c in (" ", "-", "_")]).strip().replace(" ", "_")

def run_step1(name, pid, age, gender, symptoms, duration, severity, history, medications, bp, hr, image):
    if not generator:
        return {"error": "Model failed to load. Please check logs and HF_TOKEN."}, ""
    
    patient_info = {
        "patient_name": name,
        "patient_id": pid,
        "age": age,
        "gender": gender,
        "symptoms": [s.strip() for s in symptoms.split(",")] if symptoms else [],
        "duration": duration,
        "severity": severity,
        "medical_history": [h.strip() for h in history.split(",")] if history else [],
        "medications": [m.strip() for m in medications.split(",")] if medications else [],
        "vitals": {
            "blood_pressure": bp,
            "heart_rate": hr
        }
    }
    
    images = [image] if image else None
    
    try:
        soap_note_partial = generator.generate(patient_info, images=images)
        # Add patient details to the structure for Step 2
        soap_note_partial["patient_name"] = name
        soap_note_partial["patient_id"] = pid
        return soap_note_partial, json.dumps(soap_note_partial)
    except Exception as e:
        return {"error": f"Agent 1 Error: {e}"}, ""

def run_step2(soap_note_partial_json, med_plan, lab_tests, follow_up, ethnicity):
    if not analyzer:
        return {"error": "Model failed to load."}, None
    
    if not soap_note_partial_json:
        return {"error": "No assessment data found. Please run Step 1 first."}, None
        
    try:
        soap_note_partial = json.loads(soap_note_partial_json)
        doctor_plan = {
            "medications": [m.strip() for m in med_plan.split(",")] if med_plan else [],
            "lab_tests": [l.strip() for l in lab_tests.split(",")] if lab_tests else [],
            "follow_up": follow_up
        }
        
        final_output = analyzer.analyze(soap_note_partial, doctor_plan, ethnicity)
        
        # Extract name/id for filename
        name = soap_note_partial.get("patient_name", "Unknown")
        pid = soap_note_partial.get("patient_id", "Unknown")
        
        # Generate PDF
        clean_name = sanitize_filename(name)
        clean_pid = sanitize_filename(pid)
        pdf_name = f"soap_note_{clean_name}_{clean_pid}.pdf"
        pdf_filename = os.path.join(PDF_DIR, pdf_name)
        
        # Agent 2 output usually contains the final soap_note
        final_soap_note = final_output.get("soap_note", soap_note_partial)
        
        generate_soap_pdf(final_soap_note, final_output, filename=pdf_filename, 
                          patient_name=name, patient_id=pid)
        
        return final_output, pdf_filename
    except Exception as e:
        return {"error": f"Agent 2 Error: {e}"}, None

# UI Definition
with gr.Blocks(title="MedFlow AI - Clinical Assistant (PRO)") as demo:
    gr.Markdown("# 🏥 MedFlow AI (Production Mode)")
    gr.Markdown("Powered by Google MedGemma. Real-time clinical assessment and plan analysis.")
    
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
                
                generate_draft_btn = gr.Button("📝 Run AI Assessment", variant="primary")
            
            with gr.Column():
                draft_output_json = gr.JSON(label="Structured Assessment (Agent 1 Output)")
                draft_output_raw = gr.Textbox(label="Hidden Draft JSON (for Step 2)", visible=False)
                
        generate_draft_btn.click(
            run_step1, 
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
                
                finalize_btn = gr.Button("✅ Finalize & Analyze Plan", variant="primary")
            
            with gr.Column():
                final_output_json = gr.JSON(label="Final Analysis (Agent 2 Output)")
                pdf_download = gr.File(label="Download Final SOAP Note PDF")

        finalize_btn.click(
            run_step2,
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
    # In production, we typically don't share=True unless needed, but we keep it modular
    demo.launch(theme=gr.themes.Soft())

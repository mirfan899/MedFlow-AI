import os
import json
import torch
from transformers import pipeline
from medflow.agents.agent1 import SoapNoteGenerator
from medflow.agents.agent2 import PlanAnalyzer
from medflow.utils.pdf_generator import generate_soap_pdf
from huggingface_hub import login
from PIL import Image
import requests

def main():
    print("Initializing MedFlow AI...")
    
    # 1. Setup Environment
    # Ensure HF_TOKEN is in environment or user is already logged in
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
    else:
        print("Warning: HF_TOKEN not found in environment variables. Assuming already logged in.")

    # 2. Initialize Model
    print("Loading MedGemma model (this may take a while)...")
    try:
        pipe = pipeline(
            "image-text-to-text",
            model="google/medgemma-4b-it",
            torch_dtype=torch.bfloat16,
            device="cuda" if torch.cuda.is_available() else "cpu",
        )
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    # 3. Instantiate Agents
    agent1 = SoapNoteGenerator(pipe)
    agent2 = PlanAnalyzer(pipe)

    # 4. Mock Input Data (Example)
    print("Running with example data...")
    
    # Example Patient Data
    patient_input = {
        "age": 45,
        "gender": "Male",
        "symptoms": [
            "Chest discomfort",
            "Shortness of breath during exertion",
            "Fatigue"
        ],
        "duration": "2 weeks",
        "severity": "Moderate",
        "medical_history": ["Hypertension"],
        "medications": [],
        "vitals": {
            "blood_pressure": "145/90",
            "heart_rate": "92 bpm"
        }
    }
    
    # Example Image (Optional)
    image_url = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Chest_Xray_PA_3-8-2010.png"
    try:
        image = Image.open(requests.get(image_url, headers={"User-Agent": "medflow"}, stream=True).raw)
        images = [image]
    except Exception as e:
        print(f"Could not load example image: {e}")
        images = None

    # Run Agent 1
    print("Agent 1: Generating SOAP Note (S/O/A)...")
    soap_note_partial = agent1.generate(patient_input, images=images)
    print("Subjective/Objective/Assessment Generated.")

    # Doctor Input (Simulated)
    print("Simulating Doctor Input...")
    doctor_plan = {
        "medications": ["Omeprazole 20mg once daily"],
        "lab_tests": ["H. pylori test", "CBC"],
        "follow_up": "2 weeks"
    }
    ethnicity = "South Asian"

    # Run Agent 2
    print("Agent 2: Analyzing Plan and Finalizing SOAP Note...")
    final_output = agent2.analyze(soap_note_partial, doctor_plan, ethnicity)
    
    # 5. Generate PDF
    print("Generating PDF...")
    final_soap_note = final_output.get("soap_note", {})
    if not final_soap_note:
        print("Error: meaningful SOAP note not found in Agent 2 output.")
        # Fallback if structure is different
        final_soap_note = soap_note_partial
        final_soap_note['plan'] = str(doctor_plan)

    pdf_filename = "medical_soap_note.pdf"
    generate_soap_pdf(final_soap_note, final_output, filename=pdf_filename)
    print(f"Done! PDF saved to {pdf_filename}")

if __name__ == "__main__":
    main()

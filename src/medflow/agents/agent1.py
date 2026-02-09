import json
import re

class SoapNoteGenerator:
    def __init__(self, pipeline):
        self.pipe = pipeline

    def generate(self, patient_info: dict, images: list = None):
        """
        Generates Subjective, Objective, Assessment only from patient info and optional images.
        Returns a dict with keys: subjective, objective, assessment, missing_information, safety_notice
        """
        
        # Build MedGemma chat messages
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": 
                             """You are Agent 1 in the MedFlow AI system.

Your role is to collect, validate, clean, and structure raw user input before it is passed to downstream agents.

Responsibilities:
- Accept raw input text or extracted content from speech or documents
- Detect missing, unclear, or conflicting information
- Normalize language, spelling, and formatting
- Extract key medical or domain-relevant entities
- Convert unstructured input into clean, structured JSON
- Add flags for ambiguity or low-confidence data
- Do NOT make diagnoses or recommendations

Rules:
- Stay strictly within data processing and structuring
- Do not infer beyond the provided input
- If information is missing, explicitly flag it
- Preserve the original meaning of the input

Output:
- Return only valid JSON
- Include structured data, flags, and confidence score
"""
                            }]
            },
            {
                "role": "user",
                "content": [{"type": "text", "text": (
                    "Generate a structured SOAP note in JSON format containing ONLY "
                    "Subjective (S), Objective (O), and Assessment (A). "
                    "Do NOT include Plan, Diagnosis, or Medications. "
                    "Use neutral clinical language. "
                    "If any information is missing, list it under 'missing_information'. "
                    "Add a 'safety_notice' field with precautions.\n\n"
                    f"Patient data:\n{json.dumps(patient_info, indent=2)}"
                )}]
            }
        ]
        
        # Attach images if provided
        if images:
            for img in images:
                messages[1]["content"].append({"type": "image", "image": img})
        
        # Generate output
        output = self.pipe(text=messages, max_new_tokens=800)
        assistant_text = output[-1]["generated_text"]

        # Remove markdown ```json if present
        # Handle cases where content is a list or string
        content = assistant_text[-1]["content"]
        if isinstance(content, list):
             # It should be a string in standard simple generation, but let's be safe if it's a list
             # The notebook accessed it as assistant_text[-1]["content"] which implies it's a string or list of dicts?
             # Wait, notebook code: assistant_text[-1]["content"]
             # output is list of dicts. assistant_text is likely the message dict.
             # Actually `pipe` output structure depends on the pipeline type.
             # The notebook code:
             # output = pipe(text=messages, max_new_tokens=800)
             # assistant_text = output[-1]["generated_text"]
             # json_text = re.sub(r"```json|```", "", assistant_text[-1]["content"]).strip()
             pass

        # The notebook code assumes assistant_text is a list where the last item is the response?
        # Let's check notebook code again.
        # output = pipe(...) -> returns list of generated sequences (usually just 1 if not num_return_sequences > 1)
        # Actually for 'image-text-to-text' or 'text-generation' with chat template?
        # Notebook says: assistant_text = output[-1]["generated_text"]
        # then assumes assistant_text is a list of messages? 
        # "assistant_text[-1]["content"]"
        # This implies output[-1]["generated_text"] returns the WHOLE conversation history including the new response?
        # Yes, usually pipeline returns the fulll history if using chat templates.
        
        json_text = re.sub(r"```json|```", "", assistant_text[-1]["content"]).strip()
        
        # Parse JSON safely
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError:
            data = {
                "subjective": "",
                "objective": "",
                "assessment": "",
                "missing_information": ["Patient vitals or history may be incomplete."],
                "safety_notice": "Unable to generate full SOAP note. Please verify patient data."
            }
        
        # Standardize keys
        return {
            "subjective": data.get("S", data.get("subjective", "")),
            "objective": data.get("O", data.get("objective", "")),
            "assessment": data.get("A", data.get("assessment", "")),
            "missing_information": data.get("missing_information", []),
            "safety_notice": data.get("safety_notice", "")
        }

import sys
import os
import json
import argparse

# Add src to sys.path to ensure medflow can be imported
sys.path.append(os.path.abspath("src"))

from medflow.utils.visualization import save_visualization_html

def main():
    parser = argparse.ArgumentParser(description="Generate clinical data visualization using JSON Crack.")
    parser.add_argument("--input", type=str, help="Path to JSON input file. If not provided, example data will be used.")
    parser.add_argument("--output", type=str, default="output_graph.html", help="Path to save the output HTML file. Default: output_graph.html")
    parser.add_argument("--soap-only", action="store_true", help="Only visualize the SOAP note part of the data.")
    
    args = parser.parse_args()

    if args.input:
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' not found.")
            return
        with open(args.input, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: Failed to parse JSON in '{args.input}': {e}")
                return
    else:
        # Default Example Data (Matches output_graph.html content)
        print("No input file provided. Using example data...")
        data = {
            "soap_note": {
                "subjective": {
                    "chief_complaint": "Chest discomfort, shortness of breath during exertion, and fatigue.",
                    "history_of_present_illness": "Patient reports experiencing chest discomfort, shortness of breath during exertion, and fatigue for the past 2 weeks. The symptoms are described as moderate in severity.",
                    "past_medical_history": "Patient has a history of hypertension.",
                    "medications": [],
                    "allergies": [],
                    "social_history": "Missing",
                    "family_history": "Missing",
                    "review_of_systems": "Missing",
                    "missing_information": [
                        "Social history",
                        "Family history",
                        "Review of systems",
                        "Detailed description of chest discomfort (location, character, radiation)",
                        "Details about shortness of breath (onset, triggers, relieving factors)"
                    ]
                },
                "objective": {
                    "vital_signs": {
                        "blood_pressure": "145/90 mmHg",
                        "heart_rate": "92 bpm",
                        "respiratory_rate": "Missing",
                        "temperature": "Missing",
                        "oxygen_saturation": "Missing"
                    },
                    "physical_exam": "Missing",
                    "imaging": {
                        "chest_xray": "Attached image of chest X-ray. Analysis pending.",
                        "other_imaging": "Missing"
                    },
                    "laboratory_results": "Missing",
                    "missing_information": [
                        "Respiratory rate",
                        "Temperature",
                        "Oxygen saturation",
                        "Physical exam findings",
                        "Details of chest X-ray findings"
                    ]
                },
                "assessment": "Patient presents with symptoms suggestive of possible cardiac or pulmonary etiology.",
                "plan": "Medications: Omeprazole 20mg once daily. Labs: H. pylori test, CBC. Follow-up in 2 weeks."
            },
            "medication_review": {
                "alignment_score": 85,
                "rationale": "Omeprazole is a PPI used to reduce stomach acid."
            },
            "test_validation": {
                "h_pylori_test": {
                    "relevance_score": 70,
                    "rationale": "Symptoms could be related to GERD."
                }
            }
        }

    # Filter data if soap_only is set
    if args.soap_only:
        if "soap_note" in data:
            data = data["soap_note"]
            print("Filtering data to show only 'soap_note'...")
        else:
            print("Warning: 'soap_note' key not found in data. Visualizing full structure.")

    # Generate the visualization
    output_path = save_visualization_html(data, args.output)
    print(f"Success! Graph generated at: {output_path}")

if __name__ == "__main__":
    main()

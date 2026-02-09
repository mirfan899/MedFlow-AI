import json
import os

def save_visualization_html(json_data: dict, output_file: str = "visualization.html"):
    """
    Saves an HTML file that embeds the JSON Crack widget and sends data via postMessage.
    Includes retries and a manual button to ensure data loading.
    """
    json_str = json.dumps(json_data)
    widget_url = "https://jsoncrack.com/widget"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MedFlow AI - JSON Visualization</title>
        <style>
            body, html {{ margin: 0; padding: 0; height: 100%; overflow: hidden; font-family: sans-serif; }}
            iframe {{ width: 100%; height: 100%; border: none; }}
            #controls {{
                position: absolute;
                top: 10px;
                right: 10px;
                background: white;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                z-index: 100;
            }}
            button {{
                padding: 8px 16px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }}
            button:hover {{ background-color: #0056b3; }}
        </style>
    </head>
    <body>
        <div id="controls">
            <button onclick="sendData()">Reload Graph Data</button>
        </div>
        <iframe id="jsoncrackEmbed" src="{widget_url}"></iframe>
        <script>
            const jsonData = {json_str};
            const iframe = document.getElementById("jsoncrackEmbed");
            
            const sendData = () => {{
                console.log("Sending data to JSON Crack...");
                iframe.contentWindow.postMessage({{
                    json: JSON.stringify(jsonData),
                    options: {{
                        theme: "light",
                        direction: "RIGHT"
                    }}
                }}, "*");
            }};

            // Retry mechanism
            let attempts = 0;
            const maxAttempts = 10;
            
            const attemptSend = () => {{
                if (attempts < maxAttempts) {{
                    sendData();
                    attempts++;
                    setTimeout(attemptSend, 1000); // Retry every 1s
                }}
            }};

            iframe.onload = () => {{
                console.log("Iframe loaded, starting send attempts...");
                attemptSend();
            }};
            
        </script>
    </body>
    </html>
    """
    
    with open(output_file, "w") as f:
        f.write(html_content)
    
    print(f"Visualization saved to {os.path.abspath(output_file)}")
    return os.path.abspath(output_file)

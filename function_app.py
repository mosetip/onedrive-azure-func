import logging
import os
import subprocess
import requests
import tempfile
import azure.functions as func

app = func.FunctionApp()  # Create an instance of FunctionApp

@app.route(route="process", methods=["POST"])  # Decorate the main function with the route
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request...')

    try:
        # Parse the incoming webhook request
        data = req.get_json()
        logging.info(f"Webhook data received: {data}")

        # Check if the webhook event indicates a file upload
        if 'value' in data and any('resourceData' in item and 'id' in item['resourceData'] for item in data['value']):
            logging.info("File upload event detected in OneDrive.")

            # URL of the GitHub raw script
            github_url = "https://raw.githubusercontent.com/mosetip/onedrive-gcs-autotransfer-script/main/main3.py"

            # Fetch the script from GitHub
            response = requests.get(github_url)
            response.raise_for_status()

            # Save the script to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp_file:
                tmp_file.write(response.content)
                script_path = tmp_file.name

            # Execute the script
            result = subprocess.run(["python3", script_path], capture_output=True, text=True)
            logging.info(result.stdout)
            logging.error(result.stderr)

            return func.HttpResponse("Script executed successfully.", status_code=200)

        return func.HttpResponse("No action taken for this webhook event.", status_code=200)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)

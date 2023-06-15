# AUTHOR: VIBHA PATIL
# THIS IS MY CODE TO PARSE IMAGE/PDF TO JSON FORMAT
# note: I used processor version: pretrained-invoice-v1.2-2022-02-18
#       I think it worked better on doing trial and error
# THINGS TO DO: 
# 1) process json file into csv with the entities required
# THOUGHTS:
# 1) is it possible to improve json output when storing the extracted entities?      
# 2) change processor version if required

import os
import json
from google.cloud import documentai_v1 as documentai
from google.cloud.documentai_v1 import types
from google.cloud import storage

def parser(file_path):
    # Read the input file
    with open(file_path, "rb") as file:
        image_content = file.read()

    # Set up your Google Cloud project credentials and configuration
    project_id = "<Your google project id>"  #google project id
    location = "us"  # e.g., "us" or "eu", default setting is 'us' when creating processor
    processor_id = "<processor_id>"   # id of created processor
    processor_version_id = 'pretrained-invoice-v1.2-2022-02-18'   #v1.2 works better imo- Vibha
    # The full resource name of the processor version
    processor_name = f"projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}"
    field_mask = "text,entities"  # Optional. The fields to return in the Document object.
    

    # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types
    # Determine the file type based on the file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        mime_type = "application/pdf"
    elif file_extension in [".jpeg", ".jpg", ".png"]:
        mime_type = "image/jpeg"  # Change the mime type for image files as per Document AI requirements
    else:
        print("Unsupported file format.")
        return


    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)
    # Configure the process request
    request = documentai.ProcessRequest(
        name=processor_name, raw_document=raw_document, field_mask=field_mask
    )

    result = client.process_document(request=request)

    # For a full list of Document object attributes, please reference this page:
    # https://cloud.google.com/python/docs/reference/documentai/latest/google.cloud.documentai_v1.types.Document
    document = result.document
    entities = document.entities
    text = document.text

    # Store the extracted entities and text in a dictionary
    extracted_data = {
        "entities": [],
        "text": text,
    }

    for entity in entities:
        extracted_data["entities"].append(
            {
                "type": entity.type_,
                "mention_text": entity.mention_text,
                "confidence": round(entity.confidence, 4),
            }
        )   
    # Store the extracted entities in a JSON file
    output_file = "output.json"
    with open(output_file, "w") as file:
        json.dump(extracted_data, file, indent=4)
    print(f"Extracted entities stored in {output_file}")


#authorizing client credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=r"<your api key>.json"   #api key

client = documentai.DocumentProcessorServiceClient()

file_path = r"<folder path>\<file name>"
parser(file_path)

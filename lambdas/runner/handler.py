# import subprocess
from os import makedirs, path
from pyQuARC import ARC
import json
import base64


def convert_data_str_to_dict(data_str) -> dict:
    collection_data = data_str.split('\n')
    data_dict = {}
    for index in range(len(collection_data)):
        if "WebKitFormBoundary" in collection_data[index]:
            continue
        if "name=" in collection_data[index] and not "file" in collection_data[index]:
            key = collection_data[index][collection_data[index].find('name="')+ 6:].rstrip('"\r')
            data_dict[key] = collection_data[index + 2].rstrip('\r')
        if "name=" in collection_data[index] and "file" in collection_data[index]:
            filename = collection_data[index][collection_data[index].find('filename"="')+ 11:].rstrip('"\r')
            data_dict["file"] = collection_data[index + 3].rstrip('\r')
            data_dict["filename"] = filename
    return data_dict

def handler(event, context):
    request_body_base64 = event.get("body", "{}")
    request_body_bytes = base64.b64decode(request_body_base64)
    base64_message_str = request_body_bytes.decode("utf-8")

    data_dict = convert_data_str_to_dict(base64_message_str)

    file_content = data_dict.get("file", "")
    filename = data_dict.get("filename", "")
    concept_id = data_dict.get("concept_id", "")
    format = data_dict.get("format", "")

    print(format)
    print(data_dict)
    print(file_content)
    print(concept_id)

    response = {
    "isBase64Encoded": False,
    "statusCode": 200,
    "headers": {},
    "body": ""
    }

    # XNOR operator
    if not(bool(filename) ^ bool(concept_id)):
        response['statusCode'] = 500     # think of some statuscode here
        response["body"] = "Please pass either concept id or file"
    else:
        print("run the project")

        #Avoid try here
        try:
            tmp_dir = "/tmp"
            if not path.exists(tmp_dir):
                makedirs(tmp_dir)
            filepath = path.join(tmp_dir, filename)
            if file_content:
                with open(filepath, "w") as filepointer:
                    filepointer.write(data_dict.get("file"))
        except:
            pass
        print(filepath)
        with open(filepath, "r") as f:
            print(f.read().encode())

        try:
            arc = ARC(
                input_concept_ids = concept_id,
                metadata_format = format,
                file_path = filepath
            )
            results = arc.validate()
            response['body'] = json.dumps(results)
        except Exception as e:
            response['statusCode'] = 500
            response['body'] = str(e)
    return response
        


if __name__=='__main__':
    sample_event = {
        "body": json.dumps({
            "concept_id": "C1214470488-ASF",
            "format": "echo10"
        })
    }

    print(handler(sample_event, None))

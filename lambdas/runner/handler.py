import base64
import json
from os import makedirs, path

from pyQuARC import ARC
from requests_toolbelt import MultipartDecoder

RESPONSE = {
    "isBase64Encoded": False,
    "statusCode": 200,
    "headers": {},
    "body": ""
}

def parse_content_disposition(content_disposition):
    unparsed_properties = [property.strip() for property in content_disposition.split(";")][1:]
    parsed_properties = {}
    for unparsed_property in unparsed_properties:
        attr, value = unparsed_property.split("=")
        parsed_properties[attr] = value.strip('"')
    return parsed_properties

def decode_parts(request_parts):
    parsed_result = {}
    for part in request_parts:
        content = part.content.decode("utf-8")
        parsed_properties = parse_content_disposition(part.headers[b"Content-Disposition"].decode("utf-8"))
        parsed_result = { **parsed_result, parsed_properties.pop("name"): content, **parsed_properties }
    return parsed_result

def handler(event, context):
    request_body_base64 = event.get("body", "{}")
    request_body_bytes = base64.b64decode(request_body_base64)
    decoder = MultipartDecoder(request_body_bytes, event["headers"]["content-type"])
    data_dict = decode_parts(decoder.parts)

    file_content = data_dict.get("file", "")
    filename = data_dict.get("filename", "")
    concept_ids = data_dict.get("concept_id", "")
    format = data_dict.get("format", "")


    response = RESPONSE

    if file_content:
        tmp_dir = "/tmp"
        if not path.exists(tmp_dir):
            makedirs(tmp_dir)
        filepath = path.join(tmp_dir, filename)
        with open(filepath, "w") as filepointer:
            filepointer.write(data_dict.get("file"))

    try:
        if file_content:
            arc = ARC(
                metadata_format = format,
                file_path = filepath
            )
        else:
            arc = ARC(
                metadata_format = format,
                input_concept_ids = concept_ids
            )
        results = arc.validate()
        response["body"] = json.dumps(results)
    except Exception as e:
        response["statusCode"] = 500
        response["body"] = str(e)
    return response


if __name__ == "__main__":
    sample_event = {"body": json.dumps({"concept_id": "C1214470488-ASF", "format": "echo10"})}

    print(handler(sample_event, None))

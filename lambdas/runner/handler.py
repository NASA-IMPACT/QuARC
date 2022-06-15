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
def results_parser(detailed_data):
    """ This function accepts metadata assessment results obtained
    from pyquarc and parse the results to obtain consolidated total errors, 
    total valid and error fields.
    """

    meta_info = {
        "total_errors": 0,
        "total_valid": 0,
        "error_fields": []   
    }
    for field_name,field_details in detailed_data[0]["errors"].items():
        if not field_name=="result" and field_details:
            for _,check_messages in field_details.items():
                if check_messages["valid"] == False:
                    info = check_messages["message"][0].split(":")[0]
                    if info in ["Info", "Warning", "Error"]:
                        meta_info["total_errors"] += 1
                        meta_info["error_fields"].append(field_name)
                else:
                    meta_info["total_valid"] += 1
    return meta_info


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
    final_output = {}

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
                input_concept_ids = [concept_ids]
            )
        results = arc.validate()
        
        final_output["details"] = results
        final_output["meta"] = results_parser(results)
        final_output["params"] = data_dict
        response['body'] = json.dumps(final_output)

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

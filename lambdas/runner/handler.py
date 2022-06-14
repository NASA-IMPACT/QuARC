from pyQuARC import ARC
import json

RESPONSE = {
    "is_base64_encoded": False,
    "status_code": 200,
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


def handler(event, context):
    print(event.get("body", "{}"))
    request_body = json.loads(event.get("body", "{}"))
    response = RESPONSE
    final_output = {}

    try:
        arc = ARC(
            input_concept_ids=[request_body.get('concept_id')],
            metadata_format=request_body.get('format', 'echo10'),
        )
        results = arc.validate()
        
        final_output["details"] = results
        final_output["meta"] = results_parser(results)
        final_output["params"] = {
            "concept_ids" : [request_body.get('concept_id')],
            "metadata_format" : request_body.get('format', 'echo10')
        }
        response['body'] = json.dumps(final_output)

    except Exception as e:
        response['status_code'] = 500
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

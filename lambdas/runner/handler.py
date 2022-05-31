from pyQuARC import ARC
import json

RESPONSE = {
    "isBase64Encoded": False,
    "statusCode": 200,
    "headers": {},
    "body": ""
}
def results_parser(data):
    meta = {}

    data = data[0]
    total_errors = 0
    total_valid = 0
    error_fields = []
    for k,v in data["errors"].items():
        if not k=="result" and v:
            for _,value in v.items():
                if value["valid"] == False:
                    info = value["message"][0].split(":")[0]
                    if info == "Info" or info == "Warning" or info == "Error":
                        total_errors += 1
                        error_fields.append(k)
                else:
                    total_valid += 1
    meta["total_errors"] = total_errors
    meta["total_valid"] = total_valid
    meta["error_fields"] = error_fields
    return meta

def handler(event, context):
    request_body = json.loads(event.get("body", "{}"))
    response = RESPONSE

    try:
        arc = ARC(
            input_concept_ids=[request_body.get('concept_id')],
            metadata_format=request_body.get('format', 'echo10'),
        )
        results = arc.validate()
        final_output = {}
        final_output["details"] = results
        final_output["meta"] = results_parser(results)
        final_output["params"] = {
            "concept_ids" : [request_body.get('concept_id')],
            "metadata_format" : request_body.get('format', 'echo10')
        }
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

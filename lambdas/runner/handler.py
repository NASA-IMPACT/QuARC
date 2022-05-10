from pyQuARC import ARC
import json


def handler(event, context):
    request_body = json.loads(event.get("body", "{}"))

    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "body": ""
    }
    try:
        arc = ARC(
            input_concept_ids=[request_body.get('concept_id')],
            metadata_format=request_body.get('format', 'echo10'),
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

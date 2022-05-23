from pyQuARC import ARC
import json


def handler(event, context):
    request_body = json.loads(event.get("body", "{}"))

    RESPONSE = {
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
        RESPONSE['body'] = json.dumps(results)
    except Exception as e:
        RESPONSE['statusCode'] = 500
        RESPONSE['body'] = str(e)
    return RESPONSE        


if __name__=='__main__':
    sample_event = {
        "body": json.dumps({
            "concept_id": "C1214470488-ASF",
            "format": "echo10"
        })
    }

    print(handler(sample_event, None))

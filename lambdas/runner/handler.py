import base64
import json
from os import makedirs, path

from pyQuARC import ARC
from request_validator.fields import CharField
from request_validator.serializers import Serializer
from requests_toolbelt import MultipartDecoder


TMP_DIR = "/tmp"


class SampleSerializer(Serializer):
    format = CharField(
        source="format",
        choices=["echo10", "dif10", "echo-c", "echo-g", "umm-c", "umm-g"],
        required=True,
        allow_blank=False,
    )
    concept_id = CharField(source="concept_id")
    file = CharField(source="file")
    filename = CharField(source="filename")

    def _validate(self, initial_data):
        if not (bool(initial_data.get("concept_id")) ^ bool(initial_data.get("file"))):
            self._all_fields_valid = False
            self.add_error("concept_id/file", "Please pass either concept_id or file")

        return super()._validate(initial_data)


def results_parser(detailed_data):
    """This function accepts metadata assessment results obtained
    from pyquarc and parse the results to obtain consolidated total errors,
    total valid and error fields.
    """

    result = []
    for data in detailed_data:
        error_fields = []
        for field_name, field_details in data.get("errors").items():
            for check_messages in field_details.values():
                if not check_messages.get("valid"):
                    error_fields.append(field_name)
                    break
        result.append(
            {
                "concept_id": data.get("concept_id"),
                "total_errors": len(error_fields),
                "total_valid": len(data.get("errors")) - len(error_fields),
                "error_fields": error_fields,
            }
        )
    return result


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
        parsed_properties = parse_content_disposition(
            part.headers[b"Content-Disposition"].decode("utf-8")
        )
        parsed_result = {
            **parsed_result,
            parsed_properties.pop("name"): content,
            **parsed_properties,
        }
    return parsed_result


def handler(event, context):
    response = {"isBase64Encoded": False, "statusCode": 200, "headers": {}, "body": ""}
    request_body_base64 = event.get("body", "{}")
    request_body_bytes = base64.b64decode(request_body_base64)
    # Dictionary is case sensitive, we have observed that "content-type" can be camel case or lower case
    content_type = event["headers"].get("Content-Type") or event["headers"].get("content-type")
    decoder = MultipartDecoder(request_body_bytes, content_type)
    data_dict = decode_parts(decoder.parts)

    validator = SampleSerializer(data=data_dict)
    if validator.is_valid():
        validated_data = validator.validate_data()

        file_content = validated_data.get("file")
        filename = validated_data.get("filename")
        concept_ids = validated_data.get("concept_id")
        format = validated_data.get("format")

        final_output = {}

        if file_content:
            if not path.exists(TMP_DIR):
                makedirs(TMP_DIR)
            filepath = path.join(TMP_DIR, filename)
            with open(filepath, "w") as filepointer:
                filepointer.write(validated_data.get("file"))

        try:
            if file_content:
                arc = ARC(metadata_format=format, file_path=filepath)
            else:
                arc = ARC(metadata_format=format, input_concept_ids=concept_ids.split(","))
            results = arc.validate()

            final_output["details"] = results
            final_output["meta"] = results_parser(results)
            final_output["params"] = validated_data
            response["body"] = json.dumps(final_output)

        except Exception as e:
            response["statusCode"] = 500
            response["body"] = str(e)
    else:
        response["statusCode"] = 500
        response["body"] = str(validator.get_errors())

    return response


if __name__ == "__main__":
    sample_event = {"body": json.dumps({"concept_id": "C1214470488-ASF", "format": "echo10"})}

    print(handler(sample_event, None))

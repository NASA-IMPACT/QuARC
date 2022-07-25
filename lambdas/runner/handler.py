import base64
import json
from os import path
from pathlib import Path

from pyQuARC import ARC
from request_validator.fields import CharField
from request_validator.serializers import Serializer
from requests_toolbelt import MultipartDecoder

TMP_DIR = "/tmp"


class SampleSerializer(Serializer):
    format = CharField(
        source="format",
        choices=["dif10", "echo-c", "echo-g", "umm-c", "umm-g"],
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


def compute_summary(collection_data):
    """
    This function accepts metadata assessment collection data that parse the results to
    compute the count of errros, infos and warning for non valid metadata.

    Args:
        collection_data (dict): assessed output of single concept ids generated by pyquarc

    Returns:
        (dict): consolidated summary for a single collection data
    """
    data_summary = {
        "concept_id": collection_data.get("concept_id"),
        "Info": 0,
        "Error": 0,
        "Warning": 0,
        "error_fields": [],
    }

    for field_name, field_details in collection_data.get("errors", {}).items():
        for check_messages in field_details.values():
            if not check_messages.get("valid"):
                message_info = check_messages.get("message")
                type_of_message = message_info[0].split(":")[0]
                try:
                    data_summary[type_of_message] += 1
                except KeyError as e:
                    print(str(e))  # log the error as new Error type has been found
                data_summary["error_fields"].append(field_name)
    return data_summary


def results_parser(combined_collections):
    """
    This function accepts metadata assessment results obtained
    from pyquarc and parse the results to obtain total errors,total info,
    total warnings,total valid and list of error fields that contains non valid metadata for each concept ids.

    Args:
        combined_collections (list): assessed output of multiple concept ids generated by pyquarc

    Returns:
        (dict): consolidated info of the collections data
    """

    result = []
    for each_collection_data in combined_collections:

        data_summary = compute_summary(each_collection_data)

        result.append(
            {
                **data_summary,
                "total_valid": len(each_collection_data.get("errors"))
                - len(data_summary["error_fields"]),
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


def wrap_inputs(validated_data):
    file_content = validated_data.get("file")
    filename = validated_data.get("filename")
    concept_ids = validated_data.get("concept_id")
    format = validated_data.get("format")

    wrapped_inputs = {"metadata_format": format}

    if file_content:
        Path(TMP_DIR).mkdir(exist_ok=True)
        filepath = path.join(TMP_DIR, filename)
        with open(filepath, "w") as filepointer:
            filepointer.write(validated_data.get("file"))

        wrapped_inputs["file_path"] = filepath
    else:
        wrapped_inputs["input_concept_ids"] = concept_ids.split(",")

    return wrapped_inputs


def handler(event, context):
    response = {"isBase64Encoded": False, "statusCode": 200, "headers": {}, "body": ""}
    request_body_base64 = event.get("body", "{}")
    request_body_bytes = base64.b64decode(request_body_base64)

    # Dictionary is case sensitive, we have observed that "content-type" can be camel case or lower case
    content_type = event["headers"].get("Content-Type") or event["headers"].get("content-type")
    if content_type == "application/json":
        data_dict = json.loads(request_body_bytes)
    else:
        decoder = MultipartDecoder(request_body_bytes, content_type)
        data_dict = decode_parts(decoder.parts)

    validator = SampleSerializer(data=data_dict)
    if validator.is_valid():
        validated_data = validator.validate_data()
        wrapped_inputs = wrap_inputs(validated_data)
        final_output = {}

        try:
            arc = ARC(**wrapped_inputs)
            results = arc.validate()
            # Replace /tmp/ from the filename
            if results[0].get("file"):
                results[0]["file"] = results[0]["file"][5:]
            final_output["details"] = results
            final_output["meta"] = results_parser(results)
            final_output["params"] = validated_data
            response["body"] = json.dumps(final_output)

        except Exception as e:
            response["statusCode"] = 500
            response["body"] = str(e)
    else:
        response["statusCode"] = 400
        response["body"] = str(validator.get_errors())

    return response


if __name__ == "__main__":
    sample_event = {"body": json.dumps({"concept_id": "C1214470488-ASF", "format": "echo10"})}

    print(handler(sample_event, None))

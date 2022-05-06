from pyQuARC import ARC


def handler(event, context):
    arc = ARC(
        input_concept_ids=[event.get('concept_id')],
        metadata_format=event.get('format', 'echo10'),
    )
    results = arc.validate()
    return results


if __name__=='__main__':
    sample_event = {
        "concept_id": "C1214470488-ASF",
        "format": "echo10",
    }

    print(handler(sample_event, None))

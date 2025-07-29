from mongodb_controller import COLLECTION_CONFIGURATION

def get_latest_date_ref_in_configuration():
    pipeline = [
        {
            '$sort': {'date_ref': -1}
        },
        {
            '$limit': 1
        },
    ]
    cursor = COLLECTION_CONFIGURATION.aggregate(pipeline=pipeline)
    data = list(cursor)
    return data[0]['date_ref']
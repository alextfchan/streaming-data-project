import json
from datetime import datetime
from input_tool.put_record_util import put_record


def user_input_tool():
    """
    Asks user for search terms, date and reference.
    Then writes a single data record into the Amazon Kinesis data input stream.

    Parameters
    ----------
    None

    Raises
    ------
    ValueError
        If the date format is invalid.

    Returns
    -------
    None
    """

    search_terms = input(
        "Enter your search terms: "
    ).strip() or "machine learning"

    while True:
        date_from = input(
            "Enter the date to search from (YYYY-MM-DD): "
        ).strip() or "2021-01-01"
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            break
        except ValueError:
            print("Invalid date format. Please enter a date in the format YYYY-MM-DD.")  # noqa E501

    reference = input(
        "Enter a reference for this search: "
    ).strip() or "guardian_content"

    record = {"search_term": search_terms,
              "date_from": date_from,
              "reference": reference}

    print("Data to be added to the stream: %s", record)

    data = json.dumps(record).encode("utf-8")

    put_record(data)

    print("Data successfully written to the Amazon Kinesis data stream.")

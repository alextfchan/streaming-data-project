from transformation_lambda.get_api_utils import get_api_link

api_key = "test"


class TestGetApiLink:
    def test_normal_search(self):
        normal_search = {"search_term": "machine%20learning", "date_from": "2023-01-01", "reference": "Guardian_content"}  # noqa: E501
        input = get_api_link(api_key, normal_search)
        print(get_api_link(api_key, normal_search))
        result = "https://content.guardianapis.com/search?q=machine%20learning&from-date=2023-01-01&api-key=test" # noqa 501
        assert input == result

    def test_bad_reference(self):
        bad_reference = {"search_term": "artificial%20intelligence", "date_from": "2023-01-01", "reference": "bad_reference"}  # noqa: E501
        input = get_api_link(api_key, bad_reference)
        result = "https://content.guardianapis.com/search?q=artificial%20intelligence&from-date=2023-01-01&api-key=test" # noqa 501
        print(get_api_link(api_key, bad_reference))
        assert input == result

    def test_future_date(self):
        future_date = {"search_term": "computers", "date_from": "2999-01-01", "reference": "Guardian_content"}  # noqa: E501
        input = get_api_link(api_key, future_date)
        result = "https://content.guardianapis.com/search?q=computers&from-date=2999-01-01&api-key=test" # noqa 501
        assert input == result

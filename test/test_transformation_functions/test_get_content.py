import pytest
import requests
from transformation_lambda.get_content import get_content, get_content_preview

class TestGetContent:
    def test_get_content(self):
        api_link = "https://content.guardianapis.com/search?q=machine%20learning&from-date=2023-01-01&api-key=test" # noqa 501
        api_key = "test"
        input = get_content(api_link, api_key)

        check_extract = input['content'][1]
        result = {'webPublicationDate': '2023-11-21T11:11:31Z', 'webTitle': 'Who said what: using machine learning to correctly attribute quotes', 'webUrl': 'https://www.theguardian.com/info/2023/nov/21/who-said-what-using-machine-learning-to-correctly-attribute-quotes', 'content_preview': '<h2><strong>Michel, Anna, Alice – The Guardian</strong></h2> <p><strong>Why do we care so much about quotes?</strong></p> <p>As we discussed in <a href="https://www.theguardian.com/info/2021/nov/25/talking-sense-using-machine-learning-to-understand-quotes">Talking sense: using machine learning to understand quotes</a>, there are many good reasons for identifying quotes. Quotes enable direct transmission of information from a source, capturing precisely the intended sentiment and meaning. They are not only a vital piece of accurate reporting but can also bring a story to life. The information extracted from them can be used for fact checking and allow us to gain insights into public views. For instance, accurately attributed quotes can be used for tracking shifting opinions on the same subject over time, or to explore those opinions as a function of identity, e.g. gender or race. Having a comprehensive set of quotes and their sources is thus a rich data asset that can be used to explore'} # noqa 501

        assert check_extract == result


class TestGetContentPreview:
    def test_get_content_preview(self):
        testUrl = "https://content.guardianapis.com/info/2023/nov/21/who-said-what-using-machine-learning-to-correctly-attribute-quotes?show-elements=all&show-fields=body&api-key=test" # noqa 501

        input = get_content_preview(testUrl)[:50]
        result = "<h2><strong>Michel, Anna, Alice – The Guardian</st"
        assert input == result
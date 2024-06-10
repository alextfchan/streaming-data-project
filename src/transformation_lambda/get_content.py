import requests


def get_content(api_link: str, api_key: str) -> dict:
    """
    This function retrieves the top 10 articles from the provided search terms.

    Parameters
    ----------
    api_link : str (required)
        The API link for the Guardian API.
        Function get_api_link will provide the correct link.

    Returns
    -------
    dict
        With keys:
            webPublicationDate : str
            webTitle : str
            webUrl : str
            content_preview : str
    """
    response = requests.get(api_link, timeout=90)
    response_json = response.json()
    results = response_json["response"]["results"]
    data = {}
    for i, result in enumerate(results):
        data[i+1] = (
            {
                "webPublicationDate": result["webPublicationDate"],
                "webTitle": result["webTitle"],
                "webUrl": result["webUrl"],
                "content_preview": get_content_preview(f"{result['apiUrl']}?show-elements=all&show-fields=body&api-key={api_key}") # noqa E501
            }
        )
    return {"content": data}

def get_content_preview(webUrl: str) -> str:
    """
    This function retrieves the first 1000 characters of the article.

    Parameters
    ----------
    webUrl : str (required)
        The apiURL of the article.
        Function get_content will provide the correct URL.
    """
    response = requests.get(webUrl)
    response_json = response.json()
    content = response_json["response"]["content"]["fields"]["body"]
    return str(content[:1000])

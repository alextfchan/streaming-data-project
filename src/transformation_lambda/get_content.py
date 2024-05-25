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
    response = requests.get(api_link)
    response_json = response.json()
    results = response_json["response"]["results"]
    data = {}
    for i, result in enumerate(results):
        data[i+1] = (
            {
                "webPublicationDate": result["webPublicationDate"],
                "webTitle": result["webTitle"],
                "webUrl": result["webUrl"],
                "content_preview": get_content_preview(f"{result['apiUrl']}?show-elements=all&show-fields=body&api-key={api_key}")
            }
        )
    return {"content": data}

# webUrl: "https://content.guardianapis.com/search?q=debate&tag=politics/politics&from-date=2014-01-01&api-key=test"

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


# print(get_content_preview("https://content.guardianapis.com/search?q=debate&tag=politics/politics&from-date=2014-01-01&api-key=test"))


# def change_to_json(data: dict) -> None:
#     """
#     Not to be added into final code.

#     This function just to check for the correct JSON format/ output.
#     """
#     with open("data.json", "w") as outfile:
#         json.dump(data, outfile, indent=4)






api_link1 = 'https://content.guardianapis.com/search?q=machine%20learning&from_date=2023-01-01&api-key=1b515b86-d09b-4dee-8d07-64563b4552de'


# api_link2 = "https://content.guardianapis.com/search?q=artificial%20intelligence&from_date=2023-01-01&api-key=test"


# api_link2 = "https://content.guardianapis.com/search?q=computers&from_date=2999-01-01&api-key=test"



# print(get_content(api_link1, '1b515b86-d09b-4dee-8d07-64563b4552de'))
# print(change_to_json(get_content(api_link1, '1b515b86-d09b-4dee-8d07-64563b4552de')))





# pprint.pp(get_content_preview("https://www.theguardian.com/info/2023/nov/21/who-said-what-using-machine-learning-to-correctly-attribute-quotes"))
# pprint.pp(get_content_preview("https://www.theguardian.com/education/2024/mar/10/early-learning-needs-parental-engagement"))
# pprint.pp(get_content_preview("https://www.theguardian.com/australia-news/2023/oct/09/chatgpt-ai-chatbots-in-schools-australia-measures-benefits-impacts"))

# print(get_content_preview("https://content.guardianapis.com/info/2023/nov/21/who-said-what-using-machine-learning-to-correctly-attribute-quotes?show-elements=all&show-fields=body&api-key=test"))

import demjson

from BiquPavilionAPI import HttpUtil


def get(api_url: str, params: dict = None) -> [str, dict]:
    response = HttpUtil.get(api_url, params)
    if response is not None:
        return demjson.decode(str(response.text))
    else:
        print('[ERROR] response is None, api_url:', api_url)


class Book:

    @staticmethod
    def novel_info(novel_id: str):
        response = get("https://infosxs.pigqq.com/BookFiles/Html/{}/info.html".format(novel_id))
        if response is not None and response.get('info') == 'success':
            return response.get('data')

    @staticmethod
    def catalogue(novel_id: str):
        response = get("https://infosxs.pigqq.com/BookFiles/Html/{}/index.html".format(novel_id))
        if response is not None and response.get('info') == 'success':
            return response.get('data').get('list')

    @staticmethod
    def search(book_name: str, page: int = 1):
        params = {"key": book_name, "page": page, "siteid": "app2"}
        response = get("https://souxs.pigqq.com/search.aspx", params=params)
        if response is not None and response.get('info') == 'success':
            return response.get('data')


class Chapter:
    @staticmethod
    def content(book_id: str, chapter_id: str):
        response = get("https://contentxs.pigqq.com/BookFiles/Html/{}/{}.html".format(book_id, chapter_id))
        if response is not None and response.get('info') == 'success':
            return response.get('data')


class Cover:
    @staticmethod
    def download_cover(url: str, params: dict = None) -> bytes:
        response = HttpUtil.get(url, params=params)
        if response is not None:
            return response.content

import requests
from submodules.utils.logger import Logger

logger = Logger()


class NetworkHelper:

    def do_post_with_json(self, url, json, headers=None):
        try:
            result = requests.post(url, json=json, headers=headers)
            logger.info(f"请求{url}返回: {result.text}")
            return result.json()
        except Exception as ex:
            logger.exception(str(ex))
            return None

    def do_post_with_data(self, url, data, headers=None):
        try:
            result = requests.post(url, data=data, headers=headers)
            logger.info(f"请求{url}返回: {result.text}")
            return result.json()
        except Exception as ex:
            logger.exception(str(ex))
            return None

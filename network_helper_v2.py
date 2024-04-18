import json

import aiohttp
from submodules.utils.logger import Logger

logger = Logger()


class NetworkHelper:

    async def do_post_with_json(self, url, data, headers=None):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data,
                                        headers=headers) as response:
                    text_response = await response.text()
                    result = None
                    try:
                        result = await response.json()
                    except:
                        result = json.loads(text_response)
                    logger.info(f"do_post_with_data: {url} {result}")
                    return result
        except Exception as ex:
            logger.error(str(ex))
            return None

    async def do_post_with_data(self, url, data, headers=None):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data,
                                        headers=headers) as response:

                    text_response = await response.text()
                    result = None
                    try:
                        result = await response.json()
                    except:
                        result = json.loads(text_response)
                    logger.info(f"do_post_with_data: {url} {result}")
                    return result
        except Exception as ex:
            logger.error(str(ex))
            return None

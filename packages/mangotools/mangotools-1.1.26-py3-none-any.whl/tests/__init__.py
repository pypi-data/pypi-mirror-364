# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2024-09-07 23:25
# @Author : 毛鹏
import asyncio
import json

import aiohttp

url = "https://zdtooltest.zalldigital.cn/api/z-tool-app/pgykolautoorder/detail/cancel/663"
payload = json.dumps({"id": 663})
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Authorization': 'Bearer 5eb01670-0af6-4c64-9cde-7f95f7858043',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'tenant_id': '14',
    'Cookie': 'Hm_lvt_f93cf7bc34efb4e4c5074b754dec8a6b=1746516236; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22...'
}


async def cancel_order():
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers) as response:
            result = await response.text()
            print(result)


async def main():
    _index = 0
    while _index < 10:
        asyncio.create_task(cancel_order())
        _index += 1
    await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())

import json
import httpx
from fastmcp import FastMCP
from pydantic import Field
from typing import Annotated


mcp = FastMCP("Image Generation")


@mcp.tool()
async def image_generation(image_prompt: Annotated[str, Field(description="图片描述，需要是英文。")]) -> str:
    """
    根据英文提示词生成图片

    Args:
        image_prompt:图片描述，需要是英文。

    Returns:
        图片的url地址
    """
    async with httpx.AsyncClient() as client:
        data = {'data': [image_prompt, 0, True, 512, 512, 3]}

        # 创建生成图片任务
        response1 = await client.post(
            'https://black-forest-labs-flux-1-schnell.hf.space/call/infer',
            json=data,
            headers={"Content-Type": "application/json"}
        )

        # 解析响应获取事件 ID
        response_data = response1.json()
        event_id = response_data.get('event_id')

        if not event_id:
            return '无法获取事件 ID'

        # 通过流式的方式拿到返回数据
        url = f'https://black-forest-labs-flux-1-schnell.hf.space/call/infer/{event_id}'
        full_response = ''
        async with client.stream('GET', url) as response2:
            async for chunk in response2.aiter_text():
                full_response += chunk

        return json.loads(full_response.split('data: ')[-1])[0]['url']


if __name__ == '__main__':
    mcp.run(transport='stdio')

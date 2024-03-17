import aiohttp
import asyncio

async def download_pdf_async(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                pdf_path = f"/tmp/pdf/{filename}"
                with open(pdf_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                return pdf_path
            else:
                raise Exception(f"Failed to download PDF, status code: {response.status}")


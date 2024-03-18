import aiohttp
import fitz

async def download_pdf_async(url: str, filename: str):
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


def read_pdf_sync(pdf_path: str):
    contents = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            contents.append(page.get_text())
    return contents

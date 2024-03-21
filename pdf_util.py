from asyncio import current_task
import aiohttp
import fitz
import PyPDF2
from fitz.mupdf import pdf_new_uri_from_path_and_named_dest
from pypdf import PdfReader

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
    curContent = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            curContent += page.get_text()
            if len(curContent) >= 2000:
                contents.append(curContent)
                curContent = ""
    return contents

def read_pdf_sync_v2(pdf_path: str):
    content = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            content += page.extract_text()
    return content

def read_pdf_sync_v3(pdf_path: str):
    reader = PdfReader(pdf_path)
    contents = []
    curContent = ""
    for index, page in enumerate(reader.pages):
        curContent += page.extract_text()
        if len(curContent) >= 2000:
            contents.append(curContent)
            curContent = ""
    return contents

def read_pdf_sync_v4(pdf_path: str):
    reader = PdfReader(pdf_path)
    content = ""
    for page in reader.pages:
        content += page.extract_text()
    return content


if __name__ == "__main__":
    import asyncio
    async def main():
        url = "https://utfs.io/f/c6ed7fde-e0bf-4d7a-a327-09c5f8483423-125zs.pdf"
        filename = "test"
        filepath = await download_pdf_async(url, filename)
        contents = read_pdf_sync_v3(filepath)
        __import__('pdb').set_trace()
        print(123)

    server = main()
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()

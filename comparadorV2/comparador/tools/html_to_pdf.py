import asyncio
from playwright.async_api import async_playwright
#codigo de ejemplo ( funcion implementada en app.py )

async def url_to_pdf(url, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        await page.pdf(path=output_path)
        await browser.close()

# Ejemplo de uso
#url = 'http://127.0.0.1:5500/index.html'
url = r"C:\Users\CECHEVARRIAMENDOZA\OneDrive - Brunswick Corporation\Documents\Proyectos_Python\PyQT_proyects\index_flexa.html"
output_path = 'html-to-pdf-output.pdf'

asyncio.run(url_to_pdf(url, output_path))
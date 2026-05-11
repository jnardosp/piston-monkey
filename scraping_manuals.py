import os
import time
from dotenv import load_dotenv
load_dotenv() # carga
from playwright.sync_api import sync_playwright

# Download folder
download_folder = "./manuals_downloaded"
os.makedirs(download_folder, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.todomecanica.com/iniciar-sesion.html")
    page.locator("div.popup.open i.fa.fa-close").wait_for(state="visible")
    page.locator("div.popup.open i.fa.fa.fa-close").click()

    page.get_by_placeholder("Email o nombre de usuario *").fill("jnardosp@gmail.com")
    page.locator("input[placeholder='Contraseña *'][type='password']").fill(os.getenv('PASSWORD'))
    page.get_by_role("button", name="Entrar").click()

    page.goto("https://www.todomecanica.com/categorias-manuales/taller/moto.html")

    # Get all matching elements as a list
    links = page.locator("div.mancat div.item.c2.rc5-10.pd15 a").all()

    print(f"Found {len(links)} brand links:")

    for link in links:
        href = link.get_attribute("href")
        text = link.inner_text()
        print(f"  - {text}: {href}")
        
        link.click()
        page.wait_for_load_state("networkidle")

        # ✅ Fixed selector: classes must be chained with dots, no spaces
        # This targets the SECOND div.items inside div.c7.rc10.pd15
        all_items = page.locator("div.c7.rc10.pd15 div.items").nth(1).locator("article.item a").all()

        print(f"    Found {len(all_items)} manuals:")
        for item in all_items:
            item_href = item.get_attribute("href")
            item_text = item.inner_text()
            print(f"      - {item_text.strip()}: {item_href}")

            # Navigate to the manual page
            item.click()
            page.wait_for_load_state("networkidle")

            # Click the download button and save the file
            download_btn = page.locator("div.descarga.pd10-0 a.btn.btn1.btn-grande")
            if download_btn.is_visible():
                print(f"        Downloading: {item_text.strip()}")
                
                with page.expect_download() as download_info:
                    download_btn.click()
                
                download = download_info.value
                # Save with a clean filename
                file_name = download.suggested_filename
                download.save_as(os.path.join(download_folder, file_name))
                print(f"        ✅ Saved: {file_name}")

                page.go_back()
                page.wait_for_load_state("networkidle")
            else:
                print(f"        ⚠️ Download button not found, skipping...")
                page.go_back()
                page.wait_for_load_state("networkidle")

    print(page.title())

    browser.close()

from playwright.sync_api import Playwright, sync_playwright, expect
import time
import re
import config

class ProtheusBot:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()
        # Use Edge (channel="msedge")
        self.browser = self.playwright.chromium.launch(
            headless=self.headless, 
            channel="msedge"
        )
        self.context = self.browser.new_context()
        
        # CLEAR CACHE/COOKIES EXPLICITLY
        print("Clearing cookies and storage for fresh session...")
        self.context.clear_cookies()
        self.context.clear_permissions()
        
        self.page = self.context.new_page()

    def stop(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def login(self):
        print(f"Navigating to {config.LOGIN_URL}...")
        try:
            self.page.goto(config.LOGIN_URL)
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
            
            # CHECK: Are we already logged in?
            try:
                if self.page.get_by_text(re.compile(r"Atualizações.*")).is_visible(timeout=5000):
                    print("Already logged in! Skipping login sequence.")
                    return
            except:
                pass

            # 1. Handle Welcome/Cookie popup
            try:
                if self.page.get_by_role("button", name="Ok").is_visible(timeout=5000):
                    print("Clicking 'Ok' button...")
                    time.sleep(4) 
                    self.page.get_by_role("button", name="Ok").click()
            except Exception as e:
                print(f"Popup check ignored: {e}")

            # 2. Login Form (Inside Iframe)
            print("Waiting for login iframe...")
            self.page.screenshot(path="debug_login_check.png")
            
            if not self.page.locator("iframe").count():
                if self.page.get_by_text(re.compile(r"Atualizações.*")).is_visible():
                     print("Main menu found (late load). Skipping login.")
                     return
            
            self.page.wait_for_selector("iframe", state="attached", timeout=60000)
            frame = self.page.frame_locator("iframe").first
            
            print("Entering credentials...")
            
            # User input
            frame.get_by_role("textbox", name="Insira seu usuário").click()
            frame.get_by_role("textbox", name="Insira seu usuário").fill(config.USERNAME)
            
            # Password input
            frame.get_by_role("textbox", name="Insira sua senha").click()
            frame.get_by_role("textbox", name="Insira sua senha").fill(config.PASSWORD)
            
            # Submit
            frame.get_by_role("button", name="Entrar").click()
            
            # Wait for Branch Selection
            print("Selecting Branch...")
            frame.locator("pro-branch-lookup").wait_for(timeout=20000)
            
            frame.locator("pro-branch-lookup").get_by_role("button", name="Pesquisar").click()
            # Select first available branch (Generic behavior)
            # frame.get_by_role("row", name="FILIAL EXAMPLE").get_by_role("radio").check()
            frame.get_by_role("row").first.get_by_role("radio").check() 
            frame.get_by_role("button", name="Selecionar").click()
            
            # Module Selection
            print("Selecting Module...")
            frame.locator("pro-system-module-lookup").get_by_role("button", name="Pesquisar").click()
            frame.get_by_role("row", name="SIGACOM Compras").get_by_label("", exact=True).check()
            frame.get_by_role("button", name="Selecionar").click()
            
            # Final Enter
            frame.get_by_role("button", name="Entrar").click()
            
            # Wait for main page to load
            print("Login complete. Waiting for main menu...")
            self.page.wait_for_selector("text=Atualizações", timeout=60000)
            
        except Exception as e:
            print(f"Login failed: {e}")
            self.page.screenshot(path="error_login.png")
            with open("page_dump.html", "w", encoding="utf-8") as f:
                f.write(self.page.content())
            raise e

    def navigate_to_products(self):
        print("Navigating to Products...")
        self.page.wait_for_load_state("domcontentloaded")
        time.sleep(2) 

        print("Clicking 'Atualizações'...")
        self.page.get_by_text(re.compile(r"Atualizações.*")).first.click()
        time.sleep(1) 

        print("Clicking 'Cadastros'...")
        self.page.get_by_text(re.compile(r"Cadastros.*")).first.click()
        time.sleep(1) 

        print("Clicking 'Produtos'...")
        self.page.get_by_title("Produtos", exact=True).click()
        
        print("Handling 'Confirmar' popup...")
        try:
           self.page.get_by_role("button", name="Confirmar").wait_for(timeout=10000)
           time.sleep(2) 
           self.page.get_by_role("button", name="Confirmar").click()
        except Exception as e:
           print(f"'Confirmar' button not found or skipped: {e}")

        print("Handling 'close' icon...")
        try:
              self.page.get_by_role("button", name="close", exact=True).wait_for(timeout=10000)
              self.page.get_by_role("button", name="close", exact=True).click()
        except:
            pass

        print("Handling 'Fechar' button...")
        try:
             time.sleep(2) 
             self.page.get_by_role("button", name="Fechar").wait_for(timeout=10000)
             self.page.get_by_role("button", name="Fechar").click()
        except Exception as e:
             pass

        print("Waiting for Product Grid...")
        self.page.get_by_role("button", name="Alterar").wait_for(timeout=30000)
        print("Product Screen Loaded!")

    def search_product(self, product_code):
        print(f"Searching for {product_code}...")
        try:
             # 1. Attempt Search Filter
             try:
                 # page.get_by_role("textbox", name="Pesquisar").click()
                 search_box = self.page.get_by_role("textbox", name="Pesquisar")
                 search_box.click()
                 # User requested click twice or emphasis on clicking
                 search_box.click()
                 search_box.fill(product_code)
                 
                 # page.locator("#COMP4535 > button").dblclick()
                 print("Double-clicking search button (#COMP4535)...")
                 self.page.locator("#COMP4535 > button").dblclick()
                 
                 print("Waiting for search results to load...")
                 time.sleep(10) # Give it time to filter
                 
             except Exception as e:
                 print(f"Search filter interaction failed (will try scroll): {e}")

             # 2. Check if product is visible, if not SCROLL
             print(f"Looking for row with text '{product_code}'...")
             found = False
             max_scrolls = 20
             
             for i in range(max_scrolls):
                # Check current view
                # Strategy: Look for a div or cell with the text. 
                # Protheus grids are often divs or table cells.
                # Use a specific locator to avoid false positives in header/searchbox
                # We target the specific row selector, usually text is enough if unique
                target_row = self.page.get_by_role("row", name=product_code).first
                # Or generic text match in grid area (tbody)
                if not target_row.is_visible():
                     target_row = self.page.locator(f"tbody tr:has-text('{product_code}')").first
                
                if target_row.is_visible():
                    print(f"Found product '{product_code}'!")
                    target_row.click()
                    found = True
                    break
                else:
                    if i < max_scrolls - 1:
                        print(f"Product not visible, scrolling down ({i+1}/{max_scrolls})...")
                        # Scroll via keyboard on the grid
                        # First click/focus the grid if possible, or just page body
                        # Try focusing the table header or just page
                        self.page.keyboard.press("PageDown")
                        time.sleep(2) # Wait for load
            
             if not found:
                 print(f"WARNING: Product '{product_code}' not found after search and scroll!")
                 # Capture state
                 self.page.screenshot(path=f"not_found_{product_code}.png")
                 # As a fallback, try selecting the FIRST row if search *might* have worked but our selector failed?
                 # No, unsafe. Let's error.
                 raise Exception(f"Product {product_code} not found in grid.")
              
        except Exception as e:
             print(f"Search sequence failed: {e}")
             self.page.screenshot(path="debug_search_fail.png")
             raise e
        
        self.page.screenshot(path="debug_search_result.png")

    def update_tax_group(self, new_group, ncm_value=""):
        print(f"Updating B1_GRTRIB to {new_group} and NCM to {ncm_value}...")
        
        try:
            # 1. Click Alterar
            print("Clicking 'Alterar'...")
            self.page.get_by_role("button", name="Alterar").click()
            
            print("Waiting for modal to open (checking for 'Impostos')...")
            # Wait for "Impostos" to be visible to confirm modal loaded
            # We use a broad text selector first to be safe, then specific
            try:
                self.page.wait_for_selector("text=Impostos", timeout=20000)
                time.sleep(2) # Extra stability
            except:
                print("WARNING: Modal might not have opened! Retrying 'Alterar' click...")
                self.page.get_by_role("button", name="Alterar").click()
                time.sleep(3)

            # 2. Click Impostos
            print("Clicking 'Impostos'...")
            # Try multiple selectors
            try:
                # 1. Try generic button (standard)
                self.page.get_by_role("button", name="Impostos").click(timeout=3000)
            except:
                print("Button 'Impostos' failed, trying 'tab' role...")
                try:
                    # 2. Try tab role
                    self.page.get_by_role("tab", name="Impostos").click(timeout=3000)
                except:
                    print("Tab 'Impostos' failed, trying exact text...")
                    # 3. Try Exact Text (avoiding "Impostos Variáveis")
                    self.page.get_by_text("Impostos", exact=True).click()
                
            time.sleep(3) # USER REQUEST: 3s delay
            
            # 3. Click Textbox - "Grupo de Tributacao"
            print("Clicking 'Grupo de Tributacao' textbox...")
            self.page.get_by_title("Grupo de Tributacao").get_by_role("textbox").click()
            time.sleep(3) # USER REQUEST: 3s delay
            
            # CLEAR field: Backspace 10 times to be safe
            print("Clearing field (Backspace)...")
            for _ in range(10):
                self.page.keyboard.press("Backspace")
                time.sleep(0.1)

            # Type value
            print(f"Typing '{new_group}'...")
            self.page.keyboard.type(new_group)
            time.sleep(2) 
            
            # Press ENTER to validate and move focus
            print("Pressing Enter...")
            self.page.keyboard.press("Enter")
            time.sleep(3) # Wait for focus move
            
            # 4. Handle "Pos.IPI/NCM" (Focus should be here now)
            if ncm_value:
                 print(f"Handling NCM: {ncm_value}...")
                 # Assuming Enter moved focus to next field (NCM)
                 
                 # Clear NCM just in case
                 for _ in range(10):
                    self.page.keyboard.press("Backspace")
                 
                 self.page.keyboard.type(ncm_value)
                 self.page.keyboard.press("Tab") # Commit NCM
                 time.sleep(2)
            
            # 5. Click Confirmar
            print("Clicking 'Confirmar'...")
            self.page.get_by_role("button", name="Confirmar").click()
            
            # 6. Wait for Fechar modal (#COMP7511)
            print("Waiting for 'Fechar' modal (#COMP7511)...")
            close_modal = self.page.locator("#COMP7511").get_by_role("button", name="Fechar")
            close_modal.wait_for(state="visible", timeout=20000)
            time.sleep(3) # USER REQUEST: 3s delay
            close_modal.click()
            
            print("Update cycle complete.")
            time.sleep(2) 
            
        except Exception as e:
            print(f"Update sequence failed: {e}")
            self.page.screenshot(path="debug_update_fail.png")
            raise e

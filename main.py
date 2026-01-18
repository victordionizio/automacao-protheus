import os
import time
from protheus_bot import ProtheusBot
import csv_processor
from tqdm import tqdm

SIMPLE_CSV_PATH = "data.csv"

def main():
    print("Starting Protheus Automation...")
    
    # 1. Load Data
    # For MVP, create a dummy file if not exists
    if not os.path.exists(SIMPLE_CSV_PATH):
        print(f"Creating sample file {SIMPLE_CSV_PATH}...")
        with open(SIMPLE_CSV_PATH, 'w') as f:
            f.write("codigo_produto;novo_grtrib;Pos.IPI/NCM\nPROD001;001;1234.56.78")
    
    items = csv_processor.load_csv(SIMPLE_CSV_PATH)
    print(f"Loaded {len(items)} items to process.")
    
    if not items:
        return

    # 2. Init Bot
    bot = ProtheusBot(headless=False)
    
    try:
        bot.start()
        bot.login()
        bot.navigate_to_products()
        
        # 3. Process Loop
        for item in tqdm(items):
            code = item.get('codigo_produto')
            group = item.get('novo_grtrib')
            ncm = item.get('Pos.IPI/NCM', '') # Handle new column, default empty if missing
            
            print(f"Processing: {code} -> Group: {group}, NCM: {ncm}")
            
            try:
                bot.search_product(code)
                bot.update_tax_group(group, ncm)
                print(f"Success: {code}")
            except Exception as e:
                error_msg = f"Error processing {code}: {str(e)}"
                print(error_msg)
                
                # Log to file
                with open("erros.txt", "a", encoding="utf-8") as err_file:
                    err_file.write(f"{code};{str(e)}\n")
                
                # Basic Recovery: Try to reload or close modals to reset state for next item
                # Capture screenshot of error state
                try:
                    bot.page.screenshot(path=f"error_{code}.png")
                    # Try to close any open modals "Fechar" or just reload page
                    # Reloading is safest but slow. Let's try to reload to be sure.
                    print("Attempting to recover state (reloading page)...")
                    bot.page.reload()
                    bot.page.wait_for_load_state("domcontentloaded")
                    # Check if we need to navigate back to products?
                    # Reload might take us to home or keep us on same page.
                    # Protheus usually keeps page.
                    # Let's verify we are on Product page or navigate again
                    time.sleep(5)
                    bot.navigate_to_products()
                except Exception as recovery_error:
                    print(f"Recovery failed: {recovery_error}")
            
            time.sleep(1) # Safety wait
            
    except Exception as e:
        print(f"Critical Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Closing bot...")
        # bot.stop() # Keep open for debugging for now

if __name__ == "__main__":
    main()

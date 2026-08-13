import time
import requests
from escpos.printer import Network, Win32Raw

API_URL = "https://scuberanni.pythonanywhere.com/api/fetch-print/"

# നിങ്ങളുടെ പ്രിൻ്ററുകളുടെ വിവരങ്ങൾ
KOT_PRINTER_IP = "192.168.1.251"

# 🟢 കമ്പ്യൂട്ടറിൽ (Settings -> Printers & scanners) കൊടുത്തിട്ടുള്ള അതേ പേര് ഇവിടെ കൊടുക്കുക
MAIN_PRINTER_NAME = "TVSE RP3200 Lite" 

print("Starting Scube Printer Service...")
print("Waiting for KOT & Main Bills...")

while True:
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            
            if data.get('has_print'):
                print_type = data.get('print_type')
                print_text = data.get('print_data')
                
                # 1. KOT പ്രിൻ്റിംഗ് (Kitchen LAN Printer)
                if print_type == 'KOT':
                    print("\n--- NEW KOT RECEIVED ---")
                    try:
                        kitchen_printer = Network(KOT_PRINTER_IP)
                        kitchen_printer.set(align='left')
                        kitchen_printer.text(print_text + "\n\n\n\n")
                        kitchen_printer.cut()
                        kitchen_printer.close()
                        print("KOT Printed successfully.")
                    except Exception as e:
                        print(f"KOT Printer Error: {e}")
                        
                # 2. MAIN BILL പ്രിൻ്റിംഗ് (Counter USB Printer)
                elif print_type == 'MAIN':
                    print("\n--- NEW MAIN BILL RECEIVED ---")
                    try:
                        # വിൻഡോസ് USB സിസ്റ്റം വഴി നേരിട്ട് Raw Text പ്രിൻ്റ് ചെയ്യുന്നു
                        main_printer = Win32Raw(MAIN_PRINTER_NAME)
                        main_printer.set(align='left')
                        main_printer.text(print_text + "\n\n\n\n")
                        main_printer.cut()
                        main_printer.close()
                        print("Main Bill Printed successfully.")
                    except Exception as e:
                        print(f"Main Printer Error: {e}")
                        print(f"കമ്പ്യൂട്ടറിലെ പ്രിന്ററിന്റെ പേര് '{MAIN_PRINTER_NAME}' എന്ന് തന്നെയാണോ എന്ന് പരിശോധിക്കുക.")
                        
    except requests.exceptions.RequestException:
        pass 
    except Exception as e:
        print("Server check error:", e)
        
    time.sleep(3)
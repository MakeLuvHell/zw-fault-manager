import pandas as pd
import sys
import os

files = [
    "UML/202511百色易问工单清单1.xls",
    "UML/202511百色易问工单清单2.xls"
]

for f in files:
    print(f"--- File: {f} ---")
    try:
        # Open the file to get sheet names first
        xls = pd.ExcelFile(f, engine='xlrd')
        sheet_names = xls.sheet_names
        print(f"All Sheet Names: {sheet_names}")

        # Indices for 2nd and 3rd sheets (index 1 and 2)
        target_indices = [1, 2]
        
        for idx in target_indices:
            if idx < len(sheet_names):
                sheet_name = sheet_names[idx]
                print(f"
  >>> Reading Sheet #{idx+1}: '{sheet_name}'")
                try:
                    df = pd.read_excel(f, sheet_name=sheet_name, engine='xlrd')
                    print(f"  Columns ({len(df.columns)}): {df.columns.tolist()}")
                    print(f"  Row count: {len(df)}")
                    if not df.empty:
                        print("  First 3 rows:")
                        try:
                             print(df.head(3).to_markdown(index=False))
                        except ImportError:
                             print(df.head(3).to_string(index=False))
                        except AttributeError:
                             print(df.head(3).to_string(index=False))
                except Exception as e:
                    print(f"  Error reading sheet '{sheet_name}': {e}")
            else:
                print(f"
  >>> Sheet #{idx+1} does not exist.")
                
    except Exception as e:
        print(f"Error opening file {f}: {e}")
    print("
" + "="*50 + "
")

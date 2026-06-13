import pandas as pd
import pyreadstat

# Read the .sav file
df, meta = pyreadstat.read_sav('HN24_24RC.sav')

# Save to CSV
df.to_csv('HN24_24RC.csv', index=False)

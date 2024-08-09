import fnmatch
from datetime import datetime

# Create the filename pattern
file_name_pattern = "DOM-%s-*.csv" % datetime.now().strftime("%Y-%m-%d")
# Example filenames
filenames = [
    "DOM-2024-05-14-73743824.csv"
]

# Check if the filenames match the pattern
for filename in filenames:
    if fnmatch.fnmatch(filename, file_name_pattern):
        print(f"{filename} matches the pattern {file_name_pattern}")
    else:
        print(f"{filename} does not match the pattern {file_name_pattern}")

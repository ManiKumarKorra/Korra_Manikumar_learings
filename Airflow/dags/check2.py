import datetime

# Construct the pattern\
new = 'Data/WEB-SALES-2024-05-18.csv'

current_date = datetime.datetime.now().strftime("%Y-%m-%d")
pattern = 'Data/WEB-SALES-{}-*.csv'.format(current_date)
print(pattern)

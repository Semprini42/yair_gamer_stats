import pygsheets
from datetime import datetime

def current_date():
    return (datetime.date(datetime.now()))


gsheet = pygsheets.authorize(service_file='lofty-feat-297322-b5d75b9c09bb.json')
#open the google spreadsheet
sheets = gsheet.open('Gamer Stats')
#select the first sheet 
table = sheets[0]

gamerDB = table.get_as_df()
DBtoday = gamerDB[gamerDB['date'] == str(current_date())]
print(DBtoday.head())
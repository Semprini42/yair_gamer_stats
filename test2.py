import pygsheets

gsheet = pygsheets.authorize(service_file='lofty-feat-297322-b5d75b9c09bb.json')
#open the google spreadsheet
sheets = gsheet.open('Gamer Stats')
#select the first sheet 
table = sheets[0]

df = table.get_as_df()
print(df)
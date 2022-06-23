import time, re
import cv2, pytesseract, pygsheets
from datetime import datetime
import numpy as np
from PIL import ImageGrab
import pandas as pd

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
config = ('-l eng --oem 1 --psm 3')

# scrennshots yair's profile and extract text from it
def get_gamer_status():
    status_img = np.array(ImageGrab.grab(bbox=(1675, 260, 1810, 280))) #x, y, w, h
    status_img = cv2.cvtColor(status_img, cv2.COLOR_BGR2GRAY)
    status_img = cv2.bitwise_not(status_img) 
    
    status = pytesseract.image_to_string(status_img, config=config)
    status = re.sub('[^A-Za-z0-9 ]+', '', status)
    return(status)


# Connect to yair's table on gsheet and returns the sheet
def table_connect():
    #authorization
    gsheet = pygsheets.authorize(service_file='lofty-feat-297322-b5d75b9c09bb.json')
    #open the google spreadsheet
    sheets = gsheet.open('Gamer Stats')
    #select the first sheet 
    return(sheets[0])


# Uploads entry to DB 
def upload_entry(yair_table, status):  
    gamerDB = yair_table.get_as_df()
    DBtoday = gamerDB[gamerDB['date'] == str(current_date())]
    if (status in DBtoday['status'].values):
        updatetime = gamerDB[(gamerDB['date'] == str(current_date())) &
                            (gamerDB['status'] == status)]['updated_at'].values[0]
        updatetime = datetime.fromisoformat(updatetime)
        duration = (datetime.now() - updatetime).seconds/60

        # gets current duration of current status
        current_duration = gamerDB[(gamerDB['date'] == str(current_date())) & (gamerDB['status'] == status)]['duration'].values[0]
        
        print(current_duration + duration)
        # updates duration of status
        gamerDB.loc[(gamerDB['date'] == str(current_date())) & (gamerDB['status'] == status), 'duration'] = current_duration + duration
        # updates updated_at of each status
        gamerDB.loc[(gamerDB['date'] == str(current_date())), 'updated_at'] = datetime.now()
        
        # uploades data to gsheets
        yair_table.set_dataframe(gamerDB,(1,1))

    else:
        data = pd.DataFrame({'date': [current_date()],
                            'status': status,
                            'duration': 0,
                            'updated_at': datetime.now()})
    
        gamerDB = pd.concat([gamerDB, data], ignore_index=True)

        # uploading new DF to table
        yair_table.set_dataframe(gamerDB,(1,1))


# Returns corrent date
def current_date():
    return (datetime.date(datetime.now()))


if __name__ == "__main__":
    print(get_gamer_status())
    while True:
        status = get_gamer_status()
        yair_table = table_connect()
        upload_entry(yair_table, status)
        time.sleep(300)
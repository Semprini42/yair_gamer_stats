import os, time, re
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
def upload_entry(yair_table, status, previous_status, status_start_time):  
    gamerDB = yair_table.get_as_df()
    DBtoday = gamerDB[gamerDB['date'] == str(current_date())]
    if (status in DBtoday['status']):
        duration = (time.time() - status_start_time)/60
        print(duration)

        gamerDB['duration'][gamerDB['date'] == str(current_date()) and gamerDB['status'] == status] = duration

        # filter = {'date': str(current_date())}  
        # newvalues = { "$set": {status: duration}}
        # yair_collection.update_one(filter, newvalues)

        duration = (time.time() - status_start_time)/60
        filter = {'date': str(current_date())} 

        newvalues = { "$set": {previous_status: duration}}
        yair_collection.update_one(filter, newvalues)

        newvalues = { "$set": {status: 0}}
        yair_collection.update_one(filter, newvalues)
        status_start_time = time.time()
        previous_status = status
        pass

    else:
        data = pd.DataFrame({'date': [current_date()],
                            'status': status,
                            'duration': 0})
        
        status_start_time = time.time()
        previous_status = status
        gamerDB = pd.concat([gamerDB, data], ignore_index=True)

        # uploading new DF to table
        yair_table.set_dataframe(gamerDB,(1,1))
    return (previous_status, status_start_time)


# Returns corrent date
def current_date():
    return (datetime.date(datetime.now()))


if __name__ == "__main__":
    print(get_gamer_status())
    status_start_time = time.time()
    previous_status = get_gamer_status()
    # for i in range(15):
    status = get_gamer_status()
    yair_table = table_connect()
    previous_status, status_start_time = upload_entry(yair_table, status,previous_status, status_start_time)
        # time.sleep(5)
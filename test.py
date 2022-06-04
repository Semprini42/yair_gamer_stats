import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
import pyautogui, cv2, pytesseract

PATH = 'profile.jpg'
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Yan\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
config = ('-l eng --oem 1 --psm 3')


# scrennshots yair's profile and extract text from it
def get_gamer_status():
    window = pyautogui.getWindowsWithTitle('Battle.net Profile')[0]
    x1, y1, width, height = window.box
    x2 = x1 + width
    y2 = y1 + height

    im = pyautogui.screenshot(PATH).crop((x1, y1, x2, y2))
    im.save(PATH)

    profile_img = cv2.imread(PATH)
    profile_text = pytesseract.image_to_string(profile_img, config=config)
    profile_text = profile_text.split('\n')
    profile_text = list(filter(None, profile_text))
    try:
        status_index = profile_text.index('RYTY #21494') + 1
        status = profile_text[status_index]
        return(status)
    except:
        return(0)



# Connect to yair's collection on mongo and returns it
def Collection_connect():
    load_dotenv(find_dotenv())
    password = os.environ.get('MONGODB_PWD')
    conn_str = f'mongodb+srv://yanu:{password}@gamerstats.bf81v.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(conn_str)
    return (client['GamerStats']['Yair'])



# Uploads entry to DB 
def upload_entry(yair_collection, status):
    time_of_upload = datetime.now()

    day_entry = yair_collection.find_one({'date': str(current_date())})

    if day_entry:

        # TODO: call the get_gamer_status function here and run it in a loop and just timer the time each status is on

        time_diff = int((time_of_upload - day_entry[status]['start_time']).total_seconds()/60)
        filter = {'date': str(current_date())}  
        newvalues = { "$set": {status: {'duration': time_diff, 'start_time': day_entry[status]['start_time']}}}
        yair_collection.update_one(filter, newvalues)

    else:
        data = {
            'date': str(current_date()),
            status: {'duration': 0, 'start_time': datetime.now()}
        }
        yair_collection.insert_one(data)


# Returns corrent date
def current_date():
    return (datetime.date(datetime.now()))




if __name__ == "__main__":
    yair_collection = Collection_connect()
    status = get_gamer_status()
    if status:
        upload_entry(yair_collection, 'test')
    else:
        print('Could not find status in screenshot.\nCheck if correct screenshot was taken')

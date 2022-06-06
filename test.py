import os, time, re
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
        status_index = profile_text.index('RYTY') + 1
        status = profile_text[status_index]
        status = re.sub('[^A-Za-z0-9 ]+', '', status)
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
def upload_entry(yair_collection, status, previous_status, status_start_time):  
    print(status)
    day_entry = yair_collection.find_one({'date': str(current_date())})
    if (day_entry):
        if (status in day_entry.keys()):
            duration = (time.time() - status_start_time)/60
            print(duration)
            filter = {'date': str(current_date())}  
            newvalues = { "$set": {status: duration}}
            yair_collection.update_one(filter, newvalues)
        else:
            duration = (time.time() - status_start_time)/60
            filter = {'date': str(current_date())} 

            newvalues = { "$set": {previous_status: duration}}
            yair_collection.update_one(filter, newvalues)

            newvalues = { "$set": {status: 0}}
            yair_collection.update_one(filter, newvalues)
            status_start_time = time.time()
            previous_status = status

    else:
        data = {
            'date': str(current_date()),
            status: 0
        }
        
        status_start_time = time.time()
        previous_status = status
        yair_collection.insert_one(data)
    return (previous_status, status_start_time)


# Returns corrent date
def current_date():
    return (datetime.date(datetime.now()))


if __name__ == "__main__":
    status_start_time = time.time()
    previous_status = get_gamer_status()
    for i in range(15):
        status = get_gamer_status()
        yair_collection = Collection_connect()
        previous_status, status_start_time = upload_entry(yair_collection, status,previous_status, status_start_time)
        time.sleep(5)
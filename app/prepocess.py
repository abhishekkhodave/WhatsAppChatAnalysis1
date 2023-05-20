from datetime import *
import re
import emoji
import pandas as pd
import regex

dataset_file = 'media/dataset/WhatsAppChat.txt'


def startsWithDateAndTime(s):    
    pattern = '^([0-9]{1,2})(/)([0-9]{1,2})(/)([0-9]{1,2}), ([0-9]{1,2}):([0-9]{1,2})'    
    result = re.match(pattern, s)
    if result:       
        return True
    return False


def FindAuthor(s):
    patterns = [
        '([\w]+):',
        '([\w]+[\s]+[\w]+):',
        '([\w]+[\s]+[\w]+).:',
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',
        '([\w]+[\s]+[\w]+[\s]+[\w]+[\s]+[\w]+):',
        '([+]\d{2} \d{5} \d{5}):',
        '([\w]+)[\u263a-\U0001f999]+:',
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False


def getDataPoint(line):
    splitLine = line.split(' - ')
    dateTime = splitLine[0]
    date, time = dateTime.split(', ')
    message = ' '.join(splitLine[1:])
    if FindAuthor(message):
        splitMessage = message.split(': ')
        author = splitMessage[0]
        message = ' '.join(splitMessage[1:])

    else:
        author = None
    return date, time, author, message


def load_data():
    parsedData = []
    conversationPath = dataset_file
    with open(conversationPath, encoding="utf-8") as fp:
        fp.readline()
        messageBuffer = []
        date, time, author = None, None, None
        while True:
            line = fp.readline()
            if not line:
                break
            line = line.strip()
            if startsWithDateAndTime(line):
                if len(messageBuffer) > 0:
                    parsedData.append([date, time, author, ' '.join(messageBuffer)])
                messageBuffer.clear()
                date, time, author, message = getDataPoint(line)
                messageBuffer.append(message)
            else:
                messageBuffer.append(line)
    df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message'])
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def preProcess():
    df = load_data()
    df = df.dropna()
    df = df.reset_index(drop=True)
    weeks = {
        0: 'Monday',
        1: 'Tuesday',
        2: 'Wednesday',
        3: 'Thrusday',
        4: 'Friday',
        5: 'Saturday',
        6: 'Sunday'
    }
    df['Day'] = df['Date'].dt.weekday.map(weeks)
    df = df[['Date', 'Day', 'Time', 'Author', 'Message']]
    df['Day'] = df['Day'].astype('category')
    df['Letters'] = df['Message'].apply(lambda s: len(s))
    df['Words'] = df['Message'].apply(lambda s: len(s.split(' ')))
    URLPATTERN = r'(https?://\S+)'
    df['Url_Count'] = df.Message.apply(lambda x: re.findall(URLPATTERN, x)).str.len()
    MEDIAPATTERN = r'<Media omitted>'
    df['Media_Count'] = df.Message.apply(lambda x: re.findall(MEDIAPATTERN, x)).str.len()

    def get_emojis(text):
        emoji_list = []
        data = regex.findall(r'\X', text)
        for word in data:
            if any(char in emoji.EMOJI_DATA for char in word):
                emoji_list.append(word)
        return emoji_list

    df["Emoji"] = df["Message"].apply(get_emojis)
    df['Year'] = df['Date'].dt.year
    df['Mon'] = df['Date'].dt.month
    months = {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec'
    }
    df['Month'] = df['Mon'].map(months)
    df.drop('Mon', axis=1, inplace=True)
    df['Month_Year'] = df['Month'] + "_" + df['Year'].astype(str)
    lst = []
    for i in df['Time']:
        out_time = datetime.strftime(datetime.strptime(i, "%I:%M %p"), "%H:%M")
        lst.append(out_time)
    df['24H_Time'] = lst
    df['Hours'] = df['24H_Time'].apply(lambda x: x.split(':')[0])
    return df

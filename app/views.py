import matplotlib.pyplot as plt
import nltk
import numpy as np
import seaborn as sns
from django.shortcuts import render, redirect
from matplotlib.ticker import MaxNLocator
from nltk import *
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS

import app.admin
from app.prepocess import *

nltk.data.path.append("D:\\nltk_data")
stop_words = stopwords.words('english')
porter = WordNetLemmatizer()


def home(request):
    try:
        if request.method == 'POST':
            username = str(request.POST.get("username")).strip()
            password = str(request.POST.get("password")).strip()
            if username == app.admin.username and password == app.admin.password:
                request.session['login'] = True
                return redirect(uploadataset)
            else:
                message = 'Invalid username or password'
                return render(request, 'app/home.html', {'message': message})
        else:
            request.session['login'] = False
            return render(request, 'app/home.html')
    except Exception as ex:
        request.session['login'] = False
        return render(request, 'app/home.html', {'message': ex})


def uploadataset(request):
    try:
        if request.method == 'POST' and request.FILES:
            text_file = request.FILES['dataset_file']
            with open(dataset_file, 'wb') as fw:
                fw.write(text_file.read())
            status = 1
            return render(request, 'app/uploaddataset.html', {'status': status})
        else:
            if 'login' in request.session and request.session['login']:
                return render(request, 'app/uploaddataset.html')
            else:
                return redirect(home)
    except Exception as ex:
        status = 0
        return render(request, 'app/uploaddataset.html', {'status': status, 'message': ex})


def viewdataset(request):
    try:
        if 'login' in request.session and request.session['login']:
            with open('media/dataset/WhatsAppChat.txt', 'r', encoding='utf8') as fh:
                WhatsAppChat = fh.read()
            return render(request, 'app/viewdataset.html', {'WhatsAppChat': WhatsAppChat})
        else:
            return redirect(home)
    except Exception as ex:
        return render(request, 'app/viewdataset.html', {'message': ex})


def groupstat(request):
    try:
        if 'login' in request.session and request.session['login']:
            df = preProcess()
            df_ = df.copy()
            user = ""
            if request.method == "POST":
                user = request.POST.get("user")
                df = df[df["Author"] == user]
            total_messages = df.shape[0]
            media_messages = df[df['Message'] == '<Media omitted>'].shape[0]
            links = np.sum(df.Url_Count)
            emojis = sum(df['Emoji'].str.len())
            if total_messages > 0:
                df['Text'] = df['Message'].apply(clean_text)
                df['Text'] = df['Text'].apply(remove_stopwords)
                df['Text'] = df['Text'].apply(stemmer)
                df['Polarity'] = df['Text'].apply(getPolarity)
                x = df['Text']
                y = df['Polarity'].apply(getAnalysis)
                vec = CountVectorizer(stop_words='english')
                x = vec.fit_transform(x).toarray()
                model = MultinomialNB()
                model.fit(x, y)

                def get_prediction(text):
                    return model.predict(vec.transform([text]))[0]

                df['Temp'] = df['Text'].apply(get_prediction)
                df.drop(['Temp'], axis=1)
                sentiments = []
                for idx, name in enumerate(df['Temp'].value_counts().index.tolist()):
                    sentiments.append({name: df['Temp'].value_counts()[idx]})
                chatstat = {
                    'total_messages': total_messages,
                    'media_messages': media_messages,
                    'links': links,
                    'emojis': emojis,
                    'sentiments': re.sub(r'[^A-Za-z0-9 :]+', '', str(sentiments)),
                    'user': user,
                    'users': sorted(set(df_["Author"]), reverse=True)
                }
            else:
                chatstat = None

            return render(request, 'app/groupstat.html', chatstat)
        else:
            return redirect(home)
    except Exception as ex:
        return render(request, 'app/groupstat.html', {'message': ex})


def activemembers(request):
    try:
        if 'login' in request.session and request.session['login']:
            plt.switch_backend('agg')
            pid = datetime.now().strftime('%d%m%y%I%M%S')
            df = preProcess()
            plt.figure(figsize=(11, 9))
            mostly_active = df['Author'].value_counts()
            m_a = mostly_active.head(10)
            bars = m_a.index.tolist()
            x_pos = np.arange(len(bars))
            m_a.plot.bar()
            plt.xlabel('Members', fontdict={'fontsize': 14, 'fontweight': 10}, )
            plt.ylabel('No. of messages', fontdict={'fontsize': 14, 'fontweight': 10})
            plt.title('Mostly active member of Group', fontdict={'fontsize': 20, 'fontweight': 8})
            plt.xticks(x_pos, bars)
            plt.savefig('media/data_plot/' + pid + '.jpg')
            return render(request, 'app/activemembers.html', {'pid': pid})
        else:
            return redirect(home)
    except Exception as ex:
        return render(request, 'app/activemembers.html', {'message': ex})


def activemonths(request):
    try:
        if 'login' in request.session and request.session['login']:
            plt.switch_backend('agg')
            pid = datetime.now().strftime('%d%m%y%I%M%S')
            df = preProcess()
            z = df['Month_Year'].value_counts()
            z1 = z.to_dict()
            df['Msg_count_monthly'] = df['Month_Year'].map(z1)
            plt.figure(figsize=(18, 9))
            sns.set_style("darkgrid")
            sns.lineplot(data=df, x='Month_Year', y='Msg_count_monthly', markers=True, marker='o')
            plt.xlabel('Month', fontdict={'fontsize': 14, 'fontweight': 10})
            plt.ylabel('No. of messages', fontdict={'fontsize': 14, 'fontweight': 10})
            plt.title('Analysis of mostly active month using line plot.', fontdict={'fontsize': 20, 'fontweight': 8})
            plt.savefig('media/data_plot/' + pid + '.jpg')
            return render(request, 'app/activemonths.html', {'pid': pid})
        else:
            return redirect(home)
    except Exception as ex:
        return render(request, 'app/activemonths.html', {'message': ex})


def activedays(request):
    try:
        if 'login' in request.session and request.session['login']:
            plt.switch_backend('agg')
            pid = datetime.now().strftime('%d%m%y%I%M%S')
            df = preProcess()
            plt.figure(figsize=(11, 9))
            active_day = df['Day'].value_counts()
            a_d = active_day.head(10)
            a_d.plot.bar()
            plt.xlabel('Day', fontdict={'fontsize': 12, 'fontweight': 10})
            plt.ylabel('No. of messages', fontdict={'fontsize': 12, 'fontweight': 10})
            plt.title('Mostly active day of Week in the Group', fontdict={'fontsize': 18, 'fontweight': 8})
            plt.savefig('media/data_plot/' + pid + '.jpg')
            return render(request, 'app/activedays.html', {'pid': pid})
        else:
            return redirect(home)
    except Exception as ex:
        return render(request, 'app/activedays.html', {'message': ex})


def activetimes(request):
    try:
        if 'login' in request.session and request.session['login']:
            plt.switch_backend('agg')
            pid = datetime.now().strftime('%d%m%y%I%M%S')
            df = preProcess()
            plt.figure(figsize=(8, 5))
            t = df['Hours'].value_counts().head(20)
            tx = t.plot.bar()
            tx.yaxis.set_major_locator(MaxNLocator(integer=True))  # Converting y axis data to integer
            plt.xlabel('Time (24 Hours)', fontdict={'fontsize': 12, 'fontweight': 10})
            plt.ylabel('No. of messages', fontdict={'fontsize': 12, 'fontweight': 10})
            plt.title('Analysis of time when Group was highly active.', fontdict={'fontsize': 18, 'fontweight': 8})
            plt.savefig('media/data_plot/' + pid + '.jpg')
            return render(request, 'app/activetimes.html', {'pid': pid})
        else:
            return redirect(home)
    except Exception as ex:
        return render(request, 'app/activetimes.html', {'message': ex})


def wordcloud(request):
    try:
        if 'login' in request.session and request.session['login']:
            plt.switch_backend('agg')
            pid = datetime.now().strftime('%d%m%y%I%M%S')
            df = preProcess()
            text = " ".join(review for review in df.Message)
            wordcloud = WordCloud(stopwords=STOPWORDS, background_color="white").generate(text)
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.savefig('media/data_plot/' + pid + '.jpg')
            return render(request, 'app/wordcloud.html', {'pid': pid})
        else:
            return redirect(home)
    except Exception as ex:
        return render(request, 'app/wordcloud.html', {'message': ex})


def clean_text(words):
    words = re.sub("[^a-zA-Z]", " ", words)
    text = words.lower().split()
    return " ".join(text)


def remove_stopwords(text):
    text = [word.lower() for word in text.split() if word.lower() not in stop_words]
    return " ".join(text)


def stemmer(stem_text):
    stem_text = [porter.lemmatize(word) for word in stem_text.split()]
    return " ".join(stem_text)


def getPolarity(text):
    return TextBlob(text).sentiment.polarity


def getAnalysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'

import matplotlib.pyplot as plt
from datetime import datetime as dt
import numpy as np
import pandas as pd
import re

### opening swears dictionary and log dataset
swears = open('dataset/swear.txt', 'r', encoding="utf-8")
swears = swears.read()
swears = swears.split('\n')

f = open('dataset/log.txt', 'r', encoding="utf-8")
f = f.read()
f = f.replace('\n', ' ')

### initializing global variables
swears_dict = {}
words_dict = {}


def swear_count(string):
	### function returns the number of swear words found in input string
	string = string.lower()
	count = 0
	for word in swears:
		count += string.count(word)		
	return count

def swears_collect(string):
	### function for adding swear words to global swear_dict dictionary from input string
	string = string.lower().split()
	for word in string:
		for swear in swears:
			if swear in word:
				if word in swears_dict:
					swears_dict[word] += 1
				else:
					swears_dict[word] = 1
	
def to_dict(string):
	### fucntion for adding all words from input string to global words_dict dictionary
	string = string.lower()
	if (string[0] != '<' and string[-1] != '>'):
		string = string.split()
		for word in string:	
			if word in words_dict:
				words_dict[word] += 1
			else:
				words_dict[word] = 1


##### Parcing the raw dataset, cleaning it.
pattern = re.compile(r'(?P<timestamp>\d\d.\d\d.\d\d\d\d, \d\d:\d\d) - (?P<author>.*?): (?P<text>.*?)(?=( \d\d.\d\d.\d\d\d\d, \d\d:\d\d| $))')
match = re.findall(pattern, f)

df = pd.DataFrame.from_dict(match)
df = df.iloc[1:, 0:3]
df.columns=['timestamp', 'author', 'text']
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d.%m.%Y, %H:%M')
df.set_index('timestamp', inplace=True)


##### First of all we will squeeze out some additional columns with insights from the current dataset

#### ADDING COLUMNS

### adding column with swears number in each message
df['swears_num'] = df['text'].map(swear_count)
# df.sort_values('swears_num', inplace=True)

### adding column with boolean whether the message is just a meme or video
df['media'] = df['text'].map(lambda x: 'Media' if (x[0] == '<' and x[-1] == '>') else 'Text')

### adding 'hour' column for further grouping
df['hour'] = df.index.hour


#### building dics and collecting info

### printing the number of messages
print('Overall number of messages: {}'.format(df.shape[0]))

### building the list of authors, printing it
authors = df['author'].unique().tolist()
print('There are {} authors in chat: {}'.format(len(authors), authors))

### printing first message, last message, chat age
print('First message date: {}'.format(min(df.index)))
print('Last message date: {}'.format(max(df.index)))
days = int((max(df.index) - min(df.index)).days)
years = days / 365
print('Chat age in days: {}\nChat age in years: {:.2f}'.format(days, years))
avg_msg_hour = df.groupby(['hour']).count()['text'] / days

### buildig a dict (words_dict) with words from chat (text column). Not adding a column, but collecting data
df['text'].map(to_dict)
words_dict = sorted(words_dict.items(), key=lambda x: x[1], reverse=True)

### building a dict of swears usage (swears_dict) from words_dict. Not adding a column, but collecting data
df['text'].map(swears_collect)
swears_dict = sorted(swears_dict.items(), key=lambda x: x[1], reverse=True)

### calculating overall authors messages number
authors_count = df.groupby(['author']).count()['text']
authors_count.plot(kind='bar', title='Authors messages count', alpha=0.75, rot=0)
plt.show()

### calculating weekly messages number for alltime
msg_weekly = df.resample('W').count()['text']

##### PLOTTING PART
### plots media/text percentage
medias = df.groupby(['media']).count()['text']
print(medias)

msg_weekly.plot(kind='line', title='Messages history', alpha=0.75)
plt.show()

medias.plot(kind='bar', title='Images/Videos/Funny shit percentage')
plt.show()

avg_msg_hour.plot(kind='bar', title='Average number of messages per hour', alpha=0.75)
plt.show()

print(words_dict[:20])
print('\n')
print(swears_dict[:20])

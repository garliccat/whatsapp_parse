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
plt.style.use('ggplot')


def words_count(string):
	### function returns the number of words in string
	if (string[0] != '<' and string[-1] != '>'):
		return len(string.split())

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
			if (word in words_dict and len(word) > 3):
				words_dict[word] += 1
			else:
				words_dict[word] = 1


##### Parcing the raw dataset, cleaning it.
##### ATTENTION: Parsing only authors with names, talking telephone numbers are excluding.
pattern = re.compile(r'(?P<timestamp>\d\d.\d\d.\d\d\d\d, \d\d:\d\d) - (?!\u200e)(?P<author>(?!\+\d \d\d\d).*?): (?P<text>.*?)(?=( \d\d.\d\d.\d\d\d\d, \d\d:\d\d| $))')
match = re.findall(pattern, f)

df = pd.DataFrame.from_dict(match)
df = df.iloc[0:, 0:3]
df.columns=['timestamp', 'author', 'text']
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d.%m.%Y, %H:%M')
df.set_index('timestamp', inplace=True)

print(df.head())

##### First of all we will squeeze out some additional columns with insights from the current dataset

#### ADDING COLUMNS

### adding column with swears number in each message
df['swears_num'] = df['text'].map(swear_count)
# df.sort_values('swears_num', inplace=True)

### adding column with all words in message number
df['words_num'] = df['text'].map(words_count)

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
avg_msg_hour = df.groupby('hour').count()['text'] / days

### buildig a dict (words_dict) with words from chat (text column). Not adding a column, but collecting data
df['text'].map(to_dict)
words_dict = sorted(words_dict.items(), key=lambda x: x[1], reverse=True)

### building a dict of swears usage (swears_dict) from words_dict. Not adding a column, but collecting data
df['text'].map(swears_collect)
swears_dict = sorted(swears_dict.items(), key=lambda x: x[1], reverse=True)

### calculating weekly messages number for alltime
msg_weekly = df.resample('W').count()['text']

### calculating swear words usage for each author
words_swears_users = df.groupby('author').sum()[['words_num', 'swears_num']]
print(words_swears_users)
words_swears_users['percent'] = (words_swears_users['swears_num'] / words_swears_users['words_num']) * 100
words_swears_users.sort_values(by='percent', ascending=False)
print('\nWords vs. swears percent per author:')
print(words_swears_users['percent'])
print('\n')


##### PLOTTING PART
### plots media/text percentage

### calculating and plotting overall authors messages number
authors_count = df.groupby(['author']).count()['text']
ax = authors_count.plot(kind='bar', title='Authors messages count', alpha=0.75)
for i in ax.patches:
	ax.text(i.get_x(), i.get_height(), str(i.get_height()))
plt.show()

### calculating media/text ratio per author and plotting it
medias_per_capita = df.groupby(['author', 'media']).count()['text']
medias_per_capita = medias_per_capita.unstack(level=1)
print(medias_per_capita.head())

ax = medias_per_capita.plot(kind='bar', title='Text / Media per author', alpha=0.75)
ax.set_ylabel('Number of messages')
for i in ax.patches:
	ax.text(i.get_x(), i.get_height(), str(i.get_height()))
plt.show()

### plotting overall media/text rario
medias = df.groupby(['media']).count()['text']
print(medias)

msg_weekly.plot(kind='line', title='Messages history', alpha=0.75)
plt.show()

medias.plot(kind='bar', title='Images/Videos/Funny shit percentage')
plt.show()

avg_msg_hour.plot(kind='bar', title='Average number of messages per hour', alpha=0.75)
plt.show()

print('Top 20 chart of words used in chat, longer then 3 characters: \n', words_dict[:20])
print('\n')
print('Top 20 chart of swear words: \n', swears_dict[:20])

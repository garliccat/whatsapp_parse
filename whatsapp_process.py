import matplotlib.pyplot as plt
from datetime import datetime as dt
import numpy as np
import pandas as pd
import re
import glob
import string
import markovify

### opening swears dictionary and log dataset
swears = open('dataset/swears.txt', 'r', encoding="utf-8")
swears = swears.read()
swears = swears.split('\n')

f = open(glob.glob('dataset/*WhatsApp*.txt')[0], 'r', encoding="utf-8")
f = f.read()
f = f.replace('\n', ' ')

### initializing global variables
swears_dict = {}
words_dict = {}
plt.style.use('ggplot')


def words_count(input_string):
	### function returns the number of words in input_string
	if (input_string[0] != '<' and input_string[-1] != '>'):
		return len(input_string.split())

def swear_count(input_string):
	### function returns the number of swear words found in input input_string
	input_string = input_string.lower()
	count = 0
	for word in swears:
		count += input_string.count(word)		
	return count

def swears_collect(input_string):
	### function for adding swear words to global swear_dict dictionary from input input_string
	input_string = input_string.lower().split()
	for word in input_string:
		word = word.translate(str.maketrans('', '', string.punctuation))
		for swear in swears:
			if swear in word:
				if word in swears_dict:
					swears_dict[word] += 1
				else:
					swears_dict[word] = 1
	
def to_dict(input_string):
	### fucntion for adding all words from input input_string to global words_dict dictionary
	input_string = input_string.lower()
	if (input_string[0] != '<' and input_string[-1] != '>'):
		input_string = input_string.split()
		for word in input_string:
			word = word.translate(str.maketrans('', '', string.punctuation))
			if (word in words_dict and len(word) > 3):
				words_dict[word] += 1
			else:
				words_dict[word] = 1


##### Parcing the raw dataset, cleaning it.
pattern = re.compile(r'(?P<timestamp>\d\d.\d\d.\d\d\d\d, \d\d:\d\d) - (?!\u200e)(?P<author>.*?): (?P<text>.*?)(?=( \d\d.\d\d.\d\d\d\d, \d\d:\d\d| $))')
match = re.findall(pattern, f)

df = pd.DataFrame.from_dict(match)
df = df.iloc[1:, 0:3]
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
authors_num = df.shape[0]
print('Overall number of messages: {}'.format(authors_num))

### building the list of authors, printing it
authors = df['author'].unique().tolist()
print('There are {} authors in chat: {}'.format(len(authors), authors))

### printing first message, last message, chat age
print('First message date: {}'.format(min(df.index)))
print('Last message date: {}'.format(max(df.index)))
days = int((max(df.index) - min(df.index)).days)
print('Chat age in days: {}\nChat age in years: {:.2f}'.format(days, days / 365))
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
print(words_swears_users.head())
words_swears_users['percent'] = (words_swears_users['swears_num'] / words_swears_users['words_num']) * 100
words_swears_users = words_swears_users.sort_values(by='percent', ascending=False)
print('\nWords vs. swears percent per author:')
print(words_swears_users['percent'].head())
print('\n')

### calculating the pearsons correlation matrix for each pair of authors, fetching the best of them
corr_matrix = df.groupby(['hour', 'author']).count()['text']
print('\n')
corr_matrix = corr_matrix.unstack(level=-1, fill_value=0)
corr_matrix = corr_matrix.corr()
corr_matrix.replace(to_replace=1, value=0, inplace=True)
corr_matrix = corr_matrix.stack().sort_values(ascending=False).drop_duplicates()
print('Top authors with messages timing correlation:')
print(corr_matrix.head())


##### PLOTTING PART
### plots media/text percentage

### calculating and plotting overall authors messages number
authors_count = df.groupby(['author']).count()['text']
authors_count = authors_count.sort_values(ascending=False)
if authors_num > 10:
	title = 'Top 10 authors mesages count'
	authors_count = authors_count.iloc[:10]
else:
	title = 'Authors messages count'
ax = authors_count.plot(kind='bar', title=title, alpha=0.75)
ax.set_ylabel('Number of messages')
ax.set_xlabel('Authors')
for i in ax.patches:
	ax.text(i.get_x(), i.get_height(), str(int(i.get_height())))
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right') # rotating long xticks and make them confy to read
plt.tight_layout()
plt.show()

### calculating media/text ratio per author and plotting it
medias_per_capita = df.groupby(['author', 'media']).count()['text']
medias_per_capita = medias_per_capita.unstack(level=1)
medias_per_capita = medias_per_capita.sort_values(by='Text', ascending=False)
if authors_num > 10:
	medias_per_capita = medias_per_capita.iloc[:10, :]
	title = 'Top 10 text / media per author'
else:
	title = 'Text / Media per author'	

print(medias_per_capita.head())

ax = medias_per_capita.plot(kind='bar', title=title, alpha=0.75)
ax.set_ylabel('Number of messages')
ax.set_xlabel('Authors')
for i in ax.patches:
	ax.text(i.get_x(), i.get_height(), str(int(i.get_height())))
plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right') # rotating long xticks and make them confy to read
plt.tight_layout()
plt.show()

### plotting overall messages history
msg_weekly.plot(kind='line', title='Messages history', alpha=0.75)
plt.xlabel('Date')
plt.ylabel('Number of messages')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

medias = df.groupby(['media']).count()['text']
print(medias)
medias.plot(kind='bar', title='Images/Videos/Funny shit percentage', width=0.20)
plt.xlabel('Date')
plt.ylabel('Number of messages')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

avg_msg_hour.plot(kind='bar', title='Average number of messages per hour', alpha=0.75, )
plt.xlabel('Hour')
plt.ylabel('Number of messages')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()

print('Top 20 chart of words used in chat, longer then 3 characters: \n', words_dict[:20])
print('\n')
print('Top 20 chart of swear words: \n', swears_dict[:20])


### Markov's chain message generator
authors = df['author'].unique().tolist()
author_index = 0

print('\nАвтор: ', authors[author_index])

messages = df.loc[(df['author'] == authors[author_index]) & (df['text'].str.contains('<') == False)]['text']
messages ='\n'.join(messages.tolist())
text_model = markovify.NewlineText(messages, well_formed=False)

number_of_lines = 20
count = 0

while True:	### Skiping None values
	output = text_model.make_sentence()
	if output != None:
		print(output)
		if count == number_of_lines:
			break
		else:
			count += 1
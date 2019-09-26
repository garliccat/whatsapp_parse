import matplotlib.pyplot as plt
from datetime import datetime as dt
import pandas as pd
import re

swears = open('dataset/swear.txt', 'r', encoding="utf-8")
swears = swears.read()
swears = swears.split('\n')

f = open('dataset/log.txt', 'r', encoding="utf-8")
f = f.read()
f = f.replace('\n', ' ')

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
	### function for buildng ductionary with swear words
	string = string.lower().split()
	for word in string:
		for swear in swears:
			if swear in word:
				if word in swears_dict:
					swears_dict[word] += 1
				else:
					swears_dict[word] = 1
	

def to_dict(string):
	### fucntion for collecting the dictionary of words
	string = string.lower().split()
	for word in string:
		if word in words_dict:
			words_dict[word] += 1
		else:
			words_dict[word] = 1


pattern = re.compile(r'(?P<timestamp>\d\d.\d\d.\d\d\d\d, \d\d:\d\d) - (?P<author>.*?): (?P<text>.*?)(?=( \d\d.\d\d.\d\d\d\d, \d\d:\d\d| $))')
match = re.findall(pattern, f)

print(len(match))

df = pd.DataFrame.from_dict(match)
df = df.iloc[1:, 0:3]
df.columns=['timestamp', 'author', 'text']
df['timestamp'] = pd.to_datetime(df['timestamp'], format='%d.%m.%Y, %H:%M')
df.set_index('timestamp', inplace=True)

print(df['author'].unique().tolist())

df['swears_num'] = df['text'].map(swear_count)
# df.sort_values('swears_num', inplace=True)

### buildig a dict (words_dict) with words from chat (text column)
df['text'].map(to_dict)
words_dict = sorted(words_dict.items(), key=lambda x: x[1], reverse=True)

### building a dict of swears usage (swears_dict) from words_dict
df['text'].map(swears_collect)
swears_dict = sorted(swears_dict.items(), key=lambda x: x[1], reverse=True)

### calculating overall authors messages number
authors_count = df.groupby(['author']).count()['text']
authors_count.plot(kind='bar', title='Authors messages count', alpha=0.75, rot=0)
plt.show()

### adding column with boolean whether the message is just a meme or video
df['media'] = df['text'].map(lambda x: 'Media' if (x[0] == '<' and x[-1] == '>') else 'Text')

### plots media/text percentage
medias = df.groupby(['media']).count()['text']
print(medias)
medias.plot(kind='bar', title='Images/Videos/Funny shit percentage')
plt.show()

print(df.shape)
print(df.describe())
print(words_dict[:50])
print('\n')
print(swears_dict[:50])
# print(df.head())
# print(df.tail())
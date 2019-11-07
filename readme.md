# WhatsApp chat analyzer
[!][/images/whatsapp.png]

Scans the chat and shows dependencies.   
Analyze the chat for swear words and its usage.   
The way to export data from app:

## Dataset must be exported from WhatsApp mobile app (android version was used)

1. Menu in chat (or group) main screen (three dots in the upper-right corner)
2. Tap "More"
3. Tap "Export chat"
4. Without media.

Then put the exported file into `/dataset` folder.   
`swears.txt` file - swear words dictionary. Feel free to add your own words.   
`stopwords-ru.txt stopwards-en.txt` files are stopwords collections.

Prints out the basic stats of chat. History stats, correlations, builds dictionaries of words, etc.   
And just for fun it generates some sentenses of most active user with Markov chains model.

To be done:   
- Add NLP text processing for behavioral analysis (moods, abusing, threats)   
- Collector of names, places and events using Natasha library,   
- Per user messaging time tracking in order to calculate the daily life and habits,   
- Some more weird stuff to analyze people.

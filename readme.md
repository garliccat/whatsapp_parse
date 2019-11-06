## WhatsApp chat analyzer
### Dataset must be exported from WhatsApp mobile app (android version was used)

Scans the chat and shows dependencies.   
Analyze the chat for swear words and its usage.   
The way to export data from app:

1. Menu in chat (or group) main screen (three dots in the upper-right corner)
2. Tap "More"
3. Tap "Export chat"
4. Without media.

Then put the exported file into `/dataset` folder.   
swears.txt file - swear words dictionary. Feel free to add your own words.   

Prints out the basic stats on chat. History stats, correlations, builds dict of words, etc.   
And just for fun it generates some sentenses of most active user with Markov chains model.
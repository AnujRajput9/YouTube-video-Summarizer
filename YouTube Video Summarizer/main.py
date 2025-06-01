import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from youtube_transcript_api import YouTubeTranscriptApi as yta
from string import punctuation

# Download necessary NLTK data (only runs once)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')  # Add this line to fix the error

# Step 1: Get transcript from URL
url = "https://www.youtube.com/watch?v=Ok7Q2LGvQPI"
match = re.search(r"v=([a-zA-Z0-9_-]+)", url)
video_id = match.group(1)

transcripts = yta.list_transcripts(video_id)
transcript = transcripts.find_transcript([t.language_code for t in transcripts]).fetch()

full_text = " ".join([entry["text"] for entry in transcript])

# Step 2: Tokenize into sentences and words
stop_words = set(stopwords.words('english'))
words = word_tokenize(full_text.lower())

# Build frequency table
freq_table = {}
for word in words:
    if word not in stop_words and word not in punctuation:
        freq_table[word] = freq_table.get(word, 0) + 1

# Score each sentence
sentences = sent_tokenize(full_text)
sentence_score = {}

for sentence in sentences:
    for word in word_tokenize(sentence.lower()):
        if word in freq_table:
            sentence_score[sentence] = sentence_score.get(sentence, 0) + freq_table[word]

# Step 3: Get top N sentences as summary
import heapq
summary_sentences = heapq.nlargest(5, sentence_score, key=sentence_score.get)
summary = " ".join(summary_sentences)

print("\n=== Summary ===\n")
print(summary)

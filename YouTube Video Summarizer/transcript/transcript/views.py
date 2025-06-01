from django.shortcuts import render , redirect
from youtube_transcript_api import YouTubeTranscriptApi as yta
import re




def youtube_transcript(request):
    error_message = None

    if request.method == "POST":
        url = request.POST.get('youtube_url')
        lang = request.POST.get('language', 'en')  # Default to English
        match = re.search(r"v=([a-zA-Z0-9_-]+)", url)

        if match:
            video_id = match.group(1)
            try:
                transcripts = yta.list_transcripts(video_id)

                # Try to get transcript in the selected language
                if lang in [t.language_code for t in transcripts]:
                    transcript = transcripts.find_transcript([lang]).fetch()
                else:
                    transcript = transcripts.find_transcript([t.language_code for t in transcripts]).fetch()

                full_text = " ".join([entry["text"] for entry in transcript])
                transcript_content = summarize_text(full_text, sentence_count=40)  # or tweak sentence_count


                request.session['transcript'] = transcript_content
                return redirect('transcript_summary')

            except Exception as e:
                error_message = f"Error fetching transcript: {str(e)}"
        else:
            error_message = "Invalid YouTube URL format"
    print(error_message)
    return render(request, 'youtube_transcript.html', {
        'error_message': error_message
    })

    

from gtts import gTTS
import os
from django.conf import settings

def transcript_summary_view(request):
    transcript = request.session.get('transcript', None)
    audio_url = None

    if transcript:
        # Ensure media folder exists
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        # Generate audio file
        tts = gTTS(text=transcript[:1500], lang='en')
        audio_path = os.path.join(settings.MEDIA_ROOT, "transcript.mp3")
        tts.save(audio_path)

        # Audio URL for HTML
        audio_url = os.path.join(settings.MEDIA_URL, "transcript.mp3")

    return render(request, 'transcript.html', {
        'transcript': transcript,
        'audio_url': audio_url,
    })


  

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def summarize_text(text, sentence_count=10):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)


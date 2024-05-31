from google.cloud import language_v1
from google.cloud import texttospeech

def analyze_sentiment(text):
    # Instantiate a client
    client = language_v1.LanguageServiceClient()
    
    # The text to analyze
    document = language_v1.Document(content=text, type_=language_v1.Document.Type.PLAIN_TEXT)
    
    # Detects the sentiment of the text
    response = client.analyze_sentiment(request={"document": document})
    sentiment = response.document_sentiment
    
    print(f"Overall Text Sentiment: {text}")
    print(f"Sentiment score: {sentiment.score}, Sentiment magnitude: {sentiment.magnitude}")
    print("\nDetailed Sentence-level Analysis:\n")
    
    sentence_sentiments = []
    for sentence in response.sentences:
        sentence_text = sentence.text.content
        sentence_score = sentence.sentiment.score
        sentence_magnitude = sentence.sentiment.magnitude
        sentence_sentiments.append((sentence_text, sentence_score, sentence_magnitude))
        
        print(f"Sentence: {sentence_text}")
        print(f"  Sentiment score: {sentence_score}, Magnitude: {sentence_magnitude}\n")
    
    return sentence_sentiments

def text_to_speech(sentences, filename='output.mp3'):
    # Instantiate a client
    client = texttospeech.TextToSpeechClient()

    # Build the SSML text input with varied emotional tones
    ssml_text = "<speak>"
    for sentence, score, _ in sentences:
        if score > 0.5:
            prosody = 'rate="medium" pitch="high"'
        elif score < -0.5:
            prosody = 'rate="slow" pitch="low"'
        else:
            prosody = 'rate="medium" pitch="medium"'
        
        ssml_text += f'<prosody {prosody}>{sentence}</prosody> '
    ssml_text += "</speak>"

    # Set the SSML input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    # Build the voice request, select the language code ("en-US") and the ssml voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",name="en-US-Wavenet-B" ,ssml_gender=texttospeech.SsmlVoiceGender.MALE)

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected voice parameters and audio file type
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    # Write the response to the output file
    with open(filename, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{filename}"')

if __name__ == "__main__":
    # Input your text here
    text = """
    Once upon a time, in a quiet village, there lived a young girl named Lily. She loved to explore the forest near her home. One sunny morning, Lily found a beautiful, shiny stone by the river. She was overjoyed and couldn't wait to show it to her friends.

    When she returned to the village, she showed the stone to her best friend, Tom. Tom was amazed and felt a sense of wonder. "This stone is magical," he said. They decided to keep it safe and explore its secrets together.

    However, as the days passed, strange things began to happen. The weather turned gloomy, and the villagers felt uneasy. Lily and Tom realized that the stone was causing these changes. They felt scared and worried about what to do.

    One night, they decided to return the stone to the river. As they placed it back in the water, the sky cleared, and the village returned to normal. They felt relieved and happy that they had restored peace.

    Lily and Tom learned that some things are best left undisturbed. They felt grateful for their adventure and the lesson they learned.
    """
    
    # Analyze sentiment
    sentences = analyze_sentiment(text)
    
    # Convert to speech with emotional tone
    text_to_speech(sentences)

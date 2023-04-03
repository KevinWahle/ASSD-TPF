import sounddevice as sd
import numpy as np
from resemblyzer import preprocess_wav, VoiceEncoder
from demo_utils import *
from pathlib import Path


# Load the voice encoder model
encoder = VoiceEncoder("cpu")
print(f"Loaded the voice encoder model on {encoder.device}.")


# Define the audio callback function for recording audio in real-time
def process_chunk(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    # Preprocess the audio
    preprocessed_audio = preprocess_wav(indata, encoder.sampling_rate)
    # Get the continuous embedding of the audio chunk
    _, cont_embeds, _ = encoder.embed_utterance(preprocessed_audio, return_partials=True, rate=16)
    # Get the similarity score between the continuous embedding and the speaker embeddings
    similarity_dict = {name: cont_embeds @ speaker_embed for name, speaker_embed in zip(speaker_names, speaker_embeds)}
    # Update the diarization plot with the current chunk
    update_diarization(similarity_dict)


# Get reference audios
# Load the interview audio from disk
# Source for the interview: https://www.youtube.com/watch?v=X2zqiX6yL3I
wav_fpath = Path("audio_data", "grab1.wav")
wav = preprocess_wav(wav_fpath)

# Cut some segments from single speakers as reference audio
segments = [[0, 4.5], [5, 9.5]]
speaker_names = ["Kevin", "Cindy"]
speaker_wavs = [wav[int(s[0] * encoder.sampling_rate):int(s[1] * encoder.sampling_rate)] for s in segments]

# Get the speaker embeddings
speaker_embeds = [encoder.embed_utterance(speaker_wav) for speaker_wav in speaker_wavs]

# Run the interactive diarization
with sd.InputStream(callback=process_chunk):
    print("Recording audio...")
    input()  # Press enter to stop recording

from resemblyzer import preprocess_wav, VoiceEncoder
from demo_utils import *
from pathlib import Path


# DEMO 02: we'll show how this similarity measure can be used to perform speaker diarization
# (telling who is speaking when in a recording).


## Get reference audios
# Load the interview audio from disk
# Source for the interview: https://www.youtube.com/watch?v=X2zqiX6yL3I
wav_fpath = Path("audio_data", "X2zqiX6yL3I.wav")
wav = preprocess_wav(wav_fpath)

# Cut some segments from single speakers as reference audio
segments = [[0, 5.5], [6.5, 12], [17, 25]]
speaker_names = ["Kyle Gass", "Sean Evans", "Jack Black"]
speaker_wavs = [wav[int(s[0] * sampling_rate):int(s[1] * sampling_rate)] for s in segments]
  
    
## Compare speaker embeds to the continuous embedding of the interview
# Derive a continuous embedding of the interview. We put a rate of 16, meaning that an 
# embedding is generated every 0.0625 seconds. It is good to have a higher rate for speaker 
# diarization, but it is not so useful for when you only need a summary embedding of the 
# entire utterance. A rate of 2 would have been enough, but 16 is nice for the sake of the 
# demonstration. 
# We'll exceptionally force to run this on CPU, because it uses a lot of RAM and most GPUs 
# won't have enough. There's a speed drawback, but it remains reasonable.
encoder = VoiceEncoder("cpu")
print("Running the continuous embedding on cpu, this might take a while...")
_, cont_embeds, wav_splits = encoder.embed_utterance(wav, return_partials=True, rate=16) 

# Aca iría speech 2 text

#print(cont_embeds[158])
#print(wav_splits)

# Get the continuous similarity for every speaker. It amounts to a dot product between the 
# embedding of the speaker and the continuous embedding of the interview
speaker_embeds = [encoder.embed_utterance(speaker_wav) for speaker_wav in speaker_wavs]
similarity_dict = {name: cont_embeds @ speaker_embed for name, speaker_embed in 
                   zip(speaker_names, speaker_embeds)}

talk_names =[]
MIN_PROB = 65/100
for i in range(len(similarity_dict[speaker_names[0]])):     # Create an array with speaker predominance in each sample
    prev = 0
    for names in speaker_names:
        prev= max(similarity_dict[names][i], prev)
        if(prev==similarity_dict[names][i]): name = names
    if prev<MIN_PROB: name = None
    talk_names.append(name)

# Si tuve 1 valor de 5 diferente, corregilo
for i in range(len(talk_names)):                            # Soft change matrix 
    if 1<i<len(talk_names)-3 and talk_names[i-1]==talk_names[i-2]==talk_names[i+1]==talk_names[i+2]:
        talk_names[i]=talk_names[i-1]

# Crea arreglo con tiempos y nombres [[start,end,speaker]]
name=talk_names[0]
speakers_time = []
prev_name=0
io=0
for i in range(len(talk_names)):
    name=talk_names[i]
    if name!=prev_name:
        if prev_name!=None:
            speakers_time.append([io,i,prev_name,""])
        io=i+1
    prev_name=name

#print(speakers_time)

# Si el delta_tiempo es menor a MIN_TIME, sacamelo
# Si son tempos cercanos (menor a MIN_TIME), hace merge
MIN_TIME = 4
time_processed=[]
for i in range(len(speakers_time)):
    #Do merge
    if len(time_processed) and speakers_time[i][2]==time_processed[-1:][0][2] and (speakers_time[i][0]-time_processed[-1:][0][1])<=MIN_TIME:
        temp = time_processed[-1:][0][0]            # Guardo de la iteración anterior 
        time_processed.pop()                        # Saco el tiempo viejo
        time_processed.append([temp, speakers_time[i][1], speakers_time[i][2], ""]) # Agrego el merge
    #Delete time
    elif (speakers_time[i][1]-speakers_time[i][0])>MIN_TIME:
        if len(time_processed) and time_processed[-1:][0][1]-time_processed[-1:][0][0]<=MIN_TIME:
            time_processed.pop()                    # Si el de la iteración anteior era menor, lo saco
        time_processed.append(speakers_time[i])     # Agrego el tiempo si es mayor a mintime
    #Append and check in next iteration
    elif i<len(speakers_time)-1:
        if len(time_processed) and time_processed[-1:][0][1]-time_processed[-1:][0][0]<=MIN_TIME:
            time_processed.pop()                    # Si el de la iteración anteior era menor, lo saco
        time_processed.append(speakers_time[i])

print(time_processed)


## Run the interactive demo
#interactive_diarization(similarity_dict, wav, wav_splits)

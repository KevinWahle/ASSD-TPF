import torchaudio
from speechbrain.pretrained import SpeakerRecognition

#ECAPA-TDNN Model
verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir="pretrained_models/spkrec-ecapa-voxceleb")

fs_norm = 16000     # Frecuencia de sampleo necesaria para hacer la comparacion
TH = 0.5            # Limite donde se consideran iguales
verify = lambda x, y: verification.verify_batch(x, y, threshold=TH)

# Carga de archivo y normalizacion
def loadFile(filePath):
    signal, fs = torchaudio.load(filePath)

    # Conversion a mono
    if len(signal.shape) > 1:
        signal = signal.mean(axis=0)
    signal.reshape(-1)

    # Si es necesario se realiza resampleo
    if fs != fs_norm:
        signal = torchaudio.transforms.Resample(fs, fs_norm)(signal)

    return signal


import os
audios= [ file for file in os.scandir('audio_samples')  if file.path.endswith('.wav') and  '-' in file.name]


print("Same speaker:\n")


for i in range(len(audios)):
    name, num = audios[i].name.split('-')
    num = int(num.split('.')[0])
    for j in range(i+1, len(audios)):
        name2, num2 = audios[j].name.split('-')
        num2 = int(num2.split('.')[0])
        if name == name2:
            print("\t", name, num, ' vs ', name2, num2)
            batch1,_ = torchaudio.load(audios[i].path)
            batch2,_ = torchaudio.load(audios[j].path)
            score, prediction = verify(batch1, batch2)
            print(score, prediction, '<---------------- FALSO NEGATIVO' if not prediction else '')
            print()

# print("\t Kevin")
# score, prediction = verification.verify_files("audio_samples\Kevin-1.wav", "audio_samples\Kevin-2.wav") # Same Speaker
# print(score, prediction)
# print("\t Sergio")
# score, prediction = verification.verify_files("audio_samples\Sergio-1.wav", "audio_samples\Sergio-2.wav") # Same Speaker
# print(score, prediction)
# print("\t Bautista")
# score, prediction = verification.verify_files("audio_samples\Bauti-1.wav", "audio_samples\Bauti-2.wav") # Same Speaker
# print(score, prediction)
# print("\t Basili")
# score, prediction = verification.verify_files("audio_samples\Basili-1.wav", "audio_samples\Basili-2.wav") # Same Speaker
# print(score, prediction)

print()

print("Different speaker:\n")

for i in range(len(audios)):
    name, num = audios[i].name.split('-')
    num = int(num.split('.')[0])
    for j in range(i+1, len(audios)):
        name2, num2 = audios[j].name.split('-')
        num2 = int(num2.split('.')[0])
        if name != name2:
            print("\t", name, num, ' vs ', name2, num2)
            batch1,_ = torchaudio.load(audios[i].path)
            batch2,_ = torchaudio.load(audios[j].path)
            score, prediction = verify(batch1, batch2)
            print(score, prediction, '<++++++++++++++++ FALSO POSITIVO' if prediction else '')
    print()

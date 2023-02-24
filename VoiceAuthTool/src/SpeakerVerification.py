
import torchaudio
from speechbrain.pretrained import SpeakerRecognition

# Carga de archivo y normalizacion
def loadFile(filePath):
    fs_norm = 16000     # Frecuencia de sampleo necesaria para hacer la comparacion
    
    signal, fs = torchaudio.load(filePath)

    # Conversion a mono
    if len(signal.shape) > 1:
        signal = signal.mean(axis=0)

    # Si es necesario se realiza resampleo
    # Utiliza un filtro FIR de orden 6 con ventana de Hann
    if fs != fs_norm:
        signal = torchaudio.transforms.Resample(fs, fs_norm)(signal)

    return signal

# Comparacion de audios para determinar si son de la misma persona
def verifySpeaker(audio1, audio2):

    #ECAPA-TDNN Model
    verification = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",
                                            savedir="pretrained_models/spkrec-ecapa-voxceleb")

    TH = 0.5            # Limite donde se consideran iguales
    
    verify = lambda x, y: verification.verify_batch(x, y, threshold=TH)

    score, prediction = verify(audio1, audio2)
    
    score = score.item()
    prediction = prediction.item()

    return score, prediction



    
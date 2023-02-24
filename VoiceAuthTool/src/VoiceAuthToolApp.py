from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QAudioOutput, QAudioFormat, QAudioDeviceInfo, QAudioBuffer, QAudioRecorder, QAudio, QAudioEncoderSettings, QMultimedia, QMediaRecorder

import os

from src.Audio import Audio
from src.PDF import PDF
from src.SpeakerVerification import loadFile, verifySpeaker
from src.PDF_encryptor.PDF_encryptor import encrypt_pdf, decrypt_pdf 
from src.ui.windows.Speaker_recognition_encryption_Windows import Ui_MainWindow

class VoiceAuthToolApp(QMainWindow, Ui_MainWindow):
    

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #self.horizontalWidget_32.setVisible(False)      #TODO: o 3?
        #self.horizontalWidget_9.setVisible(False)
        
        self.final_text_label.setText("")

        self.open_file_btn.clicked.connect(self.addPDFFile)
        self.delete_file_btn.clicked.connect(self.removeFile)
        self.record_audio_btn.clicked.connect(self.recordAudio)
        self.delete_audio_btn.clicked.connect(self.removeAudio)
        self.encrypt_btn.clicked.connect(self.encrypt)
        self.decrypt_btn.clicked.connect(self.decrypt)

        self.player = QMediaPlayer()
        self.player.setNotifyInterval(100)

        
        self.player.positionChanged.connect(self.selection_slider.setValue)
        
        self.player.durationChanged.connect(self.selection_slider.setMaximum)

        self.player.stateChanged.connect(self.playerStateChange)

        self.selection_slider.sliderMoved.connect(self.player.setPosition)    # Solo se modifican cuando el usuario
                                                                                # mueve el slider (para evitar loop con el player)

        self.selection_btn.clicked.connect(self.playPause)

        self.playIcon = [QIcon("res/play.png"), QIcon("res/pause.png")]
        self.recordIcon = [QIcon("res\icons8-add-record-100.png"), QIcon("res/recording.png")]

        self.selection = None  # Audios seleccionados para comparar

        # Formato de audio
        self.format = QAudioFormat()
        self.format.setSampleRate(16000)
        self.format.setChannelCount(1)
        self.format.setSampleSize(32)
        self.format.setCodec("audio/pcm")
        self.format.setByteOrder(QAudioFormat.LittleEndian)
        self.format.setSampleType(QAudioFormat.Float)

        self.encoder = QAudioEncoderSettings()
        self.encoder.setSampleRate(16000)
        self.encoder.setChannelCount(1)
        self.encoder.setCodec("audio/amr")
        self.encoder.setQuality(QMultimedia.HighQuality)

        self.recorder = QAudioRecorder()    # Grabador de audio

        self.recorder.stateChanged.connect(lambda state: self.record_btn.setIcon(self.recordIcon[state == QAudioRecorder.RecordingState]))

        self.isAudio=False
        self.isFile=False


    def addPDFFile(self):
        filename, _ = QFileDialog.getOpenFileName(
                        None,
                        "Select File",
                        "",
                        "PDF Files (*.pdf);;All Files (*)")
        if filename:
            try:

                name = os.path.basename(filename).split(".")[0]

                pdf = PDF(name, filename)
                
                self.addFile()

            except Exception as e:
                QMessageBox.warning(self, "Error al cargar el archivo", str(e))

    def addAudio(self, audio):
        self.horizontalWidget_32.setVisible(False)
        self.horizontalWidget_9.setVisible(False)
        #self.compare_btn.setEnabled(True) TODO: deshabilitar/habilitar el boton encrypt/decrypt

        # Carga del audio al player
        self.player.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(audio.path)))
        self.player.setVolume(100)

        self.isAudio=True


    def addFile(self, file):
        self.file_label.setText(file)
        self.mypdf=file
        self.isFile=True

    def removeAudio(self):
        self.isAudio=False
    
    def removeFile(self):
        self.isFile=False
        self.file_label.setText("")

    def encrypt(self):

        if self.isAudio and self.isFile:

            self.encrypt_btn.setEnabled(False)

            encrypt_pdf(self)

        else:
            QMessageBox.warning(self, "Encryption error", "No file or audio selected")

    def decrypt(self):
        if self.isAudio and self.isFile:

            self.compare_btn.setEnabled(False)

            #score, result = verifySpeaker(,)   # Se realiza la comparacion #TODO:

            self.similarity_number_label.setText(str(round(score, 2)))

            if result:
                self.final_text_label.setText("File orrectly decrypted")
            else:
                self.final_text_label.setText("Decryption failed. Wrong identification")
        else:
            QMessageBox.warning(self, "Decryption error", "No file or audio selected")
    
    def playerStateChange(self, state):
        if state == QMediaPlayer.PlayingState:       # Si esta reproduciendo
            self.selection_btn.setIcon(self.playIcon[1])
        else:                                       # Si esta pausado o detenido
            self.selection_btn.setIcon(self.playIcon[0])
            if state == QMediaPlayer.StoppedState:  # Si esta detenido se vuelve el slider al inicio
                self.player.setPosition(0)

    def playPause(self):
        if self.selection:
            if self.player.state() == QMediaPlayer.PlayingState:
                self.player.pause()
            else:
                self.player.play()

    def recordAudio(self):
        if self.recorder.state() == QMediaRecorder.RecordingState:
            self.recorder.stop()
            print(self.recPath)
            name = os.path.basename(self.recPath).split(".")[0]
            audio = Audio(name, loadFile(self.recPath), self.recPath)
            self.addAudio(audio)
        else:
            self.recPath,_ = QFileDialog.getSaveFileName(self, "Record Audio", "", "WAV File (*.wav)")
            if self.recPath:
                self.recorder.setAudioSettings(self.encoder)
                self.recorder.setOutputLocation(QtCore.QUrl.fromLocalFile(self.recPath))
                self.recorder.record()


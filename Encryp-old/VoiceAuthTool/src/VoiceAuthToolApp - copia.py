from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QAudioOutput, QAudioFormat, QAudioDeviceInfo, QAudioBuffer, QAudioRecorder, QAudio, QAudioEncoderSettings, QMultimedia, QMediaRecorder

import os

from src.Audio import Audio
from src.SpeakerVerification import loadFile, verifySpeaker
from src.ui.windows.Speaker_recognition_Windows import Ui_MainWindow

class VoiceAuthToolApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.main_listwidget.clear()

        self.horizontalWidget_32.setVisible(False)
        self.horizontalWidget_9.setVisible(False)

        self.selection1_listwidget.itemChanged.connect(self.audioDragged1)
        self.selection2_listwidget.itemChanged.connect(self.audioDragged2)

        self.add_btn.clicked.connect(self.addAudioFile)
        self.delete_btn.clicked.connect(self.removeAudio)
        self.record_btn.clicked.connect(self.recordAudio)
        self.compare_btn.clicked.connect(self.compare)

        self.player1 = QMediaPlayer()
        self.player1.setNotifyInterval(100)
        self.player2 = QMediaPlayer()
        self.player2.setNotifyInterval(100)
        
        self.player1.positionChanged.connect(self.selection1_slider.setValue)
        self.player2.positionChanged.connect(self.selection2_slider.setValue)
        
        self.player1.durationChanged.connect(self.selection1_slider.setMaximum)
        self.player2.durationChanged.connect(self.selection2_slider.setMaximum)

        self.player1.stateChanged.connect(self.player1StateChange)
        self.player2.stateChanged.connect(self.player2StateChange)

        self.selection1_slider.sliderMoved.connect(self.player1.setPosition)    # Solo se modifican cuando el usuario
        self.selection2_slider.sliderMoved.connect(self.player2.setPosition)    # mueve el slider (para evitar loop con el player)

        self.selection1_btn.clicked.connect(self.playPause1)
        self.selection2_btn.clicked.connect(self.playPause2)

        self.playIcon = [QIcon("res/play.png"), QIcon("res/pause.png")]
        self.recordIcon = [QIcon("res\icons8-add-record-100.png"), QIcon("res/recording.png")]

        self.selection1 = None  # Audios seleccionados para comparar
        self.selection2 = None

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


    def addAudioFile(self):
        filename, _ = QFileDialog.getOpenFileName(
                        None,
                        "Select Audio File",
                        "",
                        "Audio Files (*.mp3 *.wav *.FLAC);;All Files (*)")
        if filename:
            try:

                name = os.path.basename(filename).split(".")[0]

                audio = Audio(name, loadFile(filename), filename)
                
                self.addAudio(audio)

            except Exception as e:
                QMessageBox.warning(self, "Error al cargar el archivo", str(e))

    def addAudio(self, audio):
        self.main_listwidget.addItem(self.makeAudioItem(audio))

    def removeAudio(self):
        self.main_listwidget.takeItem(self.main_listwidget.currentRow())


    def makeAudioItem(self, audio):

        item = QListWidgetItem(audio.name)
        item.setData(QtCore.Qt.UserRole, audio)     # Guarda el objeto Audio en el item
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        item.setFont(font)
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsDropEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)

        return item

    def audioDragged1(self, item):

        self.horizontalWidget_32.setVisible(False)
        self.horizontalWidget_9.setVisible(False)
        self.compare_btn.setEnabled(True)

        if item.data(QtCore.Qt.UserRole):   # Solo si llego la data
            self.selection1 = item.data(QtCore.Qt.UserRole)   # Guardo el audio

            index = self.selection1_listwidget.indexFromItem(item).row()
            self.selection1_listwidget.takeItem(index)   # Quita el item de la lista
            self.selection1_listwidget.clear()                  # Borra toda la lista
            self.selection1_listwidget.addItem(item)           # Solo agrego este item

            # Carga del audio al player
            self.player1.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(self.selection1.path)))
            self.player1.setVolume(100)


    def audioDragged2(self, item):

        self.horizontalWidget_32.setVisible(False)
        self.horizontalWidget_9.setVisible(False)
        self.compare_btn.setEnabled(True)

        if item.data(QtCore.Qt.UserRole):   # Solo si llego la data
            self.selection2 = item.data(QtCore.Qt.UserRole)   # Guardo el audio

            index = self.selection2_listwidget.indexFromItem(item).row()
            self.selection2_listwidget.takeItem(index)   # Quita el item de la lista
            self.selection2_listwidget.clear()                  # Borra toda la lista
            self.selection2_listwidget.addItem(item)           # Solo agrego este item
            
            self.player2.setMedia(QMediaContent(QtCore.QUrl.fromLocalFile(self.selection2.path)))
            self.player2.setVolume(100)


    def compare(self):

        if self.selection1 and self.selection2:

            self.compare_btn.setEnabled(False)

            score, result = verifySpeaker(self.selection1.tensor, self.selection2.tensor)   # Se realiza la comparacion

            self.similarity_number_label.setText(str(round(score, 2)))

            if result:
                self.final_text_label.setText("Es la misma persona!")
            else:
                self.final_text_label.setText("No es la misma persona!")

            self.horizontalWidget_32.setVisible(True)
            self.horizontalWidget_9.setVisible(True)
            self.compare_btn.setEnabled(True)

        else:
            QMessageBox.warning(self, "Error al comparar", "No se seleccionaron audios para comparar")

    def player1StateChange(self, state):
        if state == QMediaPlayer.PlayingState:       # Si esta reproduciendo
            self.selection1_btn.setIcon(self.playIcon[1])
        else:                                       # Si esta pausado o detenido
            self.selection1_btn.setIcon(self.playIcon[0])
            if state == QMediaPlayer.StoppedState:  # Si esta detenido se vuelve el slider al inicio
                self.player1.setPosition(0)

    def player2StateChange(self, state):
        if state == QMediaPlayer.PlayingState:       # Si esta reproduciendo
            self.selection2_btn.setIcon(self.playIcon[1])
        else:                                       # Si esta pausado o detenido
            self.selection2_btn.setIcon(self.playIcon[0])
            if state == QMediaPlayer.StoppedState:  # Si esta detenido se vuelve el slider al inicio
                self.player2.setPosition(0)

    def playPause1(self):
        if self.selection1:
            if self.player1.state() == QMediaPlayer.PlayingState:
                self.player1.pause()
            else:
                self.player1.play()

    def playPause2(self):
        if self.selection2:
            if self.player2.state() == QMediaPlayer.PlayingState:
                self.player2.pause()
            else:
                self.player2.play()

    def recordAudio(self):
        if self.recorder.state() == QMediaRecorder.RecordingState:
            self.recorder.stop()
            print(self.recPath)
            name = os.path.basename(self.recPath).split(".")[0]
            audio = Audio(name, loadFile(self.recPath), self.recPath)
            self.addAudio(audio)
        else:
            self.recPath,_ = QFileDialog.getSaveFileName(self, "Grabar Audio", "", "WAV File (*.wav)")
            if self.recPath:
                self.recorder.setAudioSettings(self.encoder)
                self.recorder.setOutputLocation(QtCore.QUrl.fromLocalFile(self.recPath))
                self.recorder.record()


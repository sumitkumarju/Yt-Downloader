import sys
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qt import Qt, QTimer
from PyQt5 import QtCore
from collections import deque
from pytube import YouTube
import urllib.request
import ffmpeg
from mainwindow import Ui_mainwindow


class MainWindow(QtWidgets.QMainWindow, Ui_mainwindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.info.pressed.connect(self.getinfo)
        self.download.pressed.connect(self.getdownload)
        self.cancel.pressed.connect(self.close)


    def on_progress(self,stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage_of_completion = bytes_downloaded / total_size * 100
        self.progressBar.setProperty("value", percentage_of_completion)




    def getinfo(self):
        link=self.urlinput.text()
        print(link)
        self.yt = YouTube(link)
        self.yt.register_on_progress_callback(self.on_progress)
        print(self.yt.title)
        self.titleinput.setText(self.yt.title)
        self.authorinput.setText(self.yt.author)
        rating=float("{:.2f}".format(self.yt.rating))
        self.ratinginput.setText(str(rating))

        if self.yt.views>=1000000:
            views=float("{:.2f}".format(self.yt.views/1000000))
            view=str(views)+" M+"
        else:
            view= str(self.yt.views)
        self.viewsinput.setText(view)
        min=int(self.yt.length/60)
        sec=self.yt.length%60
        self.lengthinput.setText(f"{str(min)} min {str(sec)} s")


        self.scene = QGraphicsScene()
        url = self.yt.thumbnail_url
        with urllib.request.urlopen(url) as url:
            data = url.read()
        tempImg = QPixmap()
        tempImg.loadFromData(data)
        tempImg = tempImg.scaled(240, 180)
        self.graphicsPixmapItem = QGraphicsPixmapItem(tempImg)
        self.scene.addItem(self.graphicsPixmapItem)
        self.graphicsView.setScene(self.scene)

        lst_audio=[]
        p=self.yt.streams.filter(type="audio")
        for i in range(len(p.fmt_streams)):
            lst_audio.append(str(p.fmt_streams[i].abr))

        lst_video=[]
        t=self.yt.streams.filter(mime_type="video/webm")
        for i in range(len(t.fmt_streams)):
          lst_video.append(str(t.fmt_streams[i].resolution))

        for i,j in enumerate(lst_video):
           self.resolutioninput.setItemText(i, j)
           self.resolutioninput.addItem("")

        for i,j in enumerate(lst_audio):
           self.abrinput.setItemText(i, j)
           self.abrinput.addItem("")

    def getdownload(self):

        self.filePath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "mp4")
        file=self.filePath.split("/")[-1].split('.')[0]
        filePath=self.filePath.replace(f"{file}","")

        if self.typeinput.itemText(self.typeinput.currentIndex()) == "Video" :
            p=self.yt.streams.filter(res=f"{self.resolutioninput.itemText(self.resolutioninput.currentIndex())}",mime_type="video/webm")
            t=self.yt.streams.filter(mime_type="audio/webm",abr="160kbps")
            self.updates.setText("Downloading...")
            p.fmt_streams[0].download(filename='test_video')
            t.fmt_streams[0].download(filename='test_audio')
            self.updates.setText("Finishing...")
            input_video = ffmpeg.input('./test_video.webm')
            input_audio = ffmpeg.input('./test_audio.webm')
            ffmpeg.concat(input_video, input_audio, v=1, a=1).output(f'{self.filePath}.mp4').run()
        else:
            p=self.yt.streams.filter(abr=f"{self.abrinput.itemText(self.abrinput.currentIndex())}")
            p.fmt_streams[0].download(output_path=filePath,filename=file)
        self.updates.setText("Completed...")
        QMessageBox.information(QMessageBox(),'Successful','Download Competed.')












app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()

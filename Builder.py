
import os, sys
from PyQt5 import uic, QtWidgets, QtGui, QtCore, Qt
from PyQt5.QtGui import QIcon, QDrag
from PyQt5.QtWidgets import QFileDialog

os.system( str(f'pyinstaller.exe --onefile --windowed --icon=Icone.ico Catalogador-Eficaz.pyw') )


'''
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
arquivo = ''

def ESCOLHER_ARQUIVO():
    global arquivo
    arquivo = QFileDialog.getOpenFileNames()[0]
    ui.LineEdit_Arquivo.setText(arquivo)


def BUILD():
    if arquivo:
        try:
            os.system( str(f'pyinstaller.exe --onefile --windowed --icon=Icone.ico {arquivo}') )
        except:
            pass
    else:
        pass

ui.Btn_Arquivo.clicked.connection(ESCOLHER_ARQUIVO)
ui.Btn_Build.clicked.connection(BUILD)

MainWindow.show()
sys.exit(app.exec_())
'''
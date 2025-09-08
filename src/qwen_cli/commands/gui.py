def cmd_gui(args):
    try:
        from PyQt5 import QtWidgets, QtCore  # lazy import
    except Exception:
        print("❌ PyQt5 not installed. Install with: pip install PyQt5")
        return 1

    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    window.setWindowTitle("Qwen CLI – GUI (Experimental)")
    window.resize(800, 600)

    label = QtWidgets.QLabel("GUI placeholder – chat and config UI coming soon", window)
    try:
        label.setAlignment(QtCore.Qt.AlignCenter)
    except Exception:
        pass
    window.setCentralWidget(label)
    window.show()
    return app.exec_()



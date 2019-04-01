# -*- coding: utf-8 -*-
# Eduardo Marossi & Rafael Corsi @ insper.edu.br
# Dez/2017
# Disciplina Elementos de Sistemas
import sys, os, tempfile
import argparse

from PyQt5 import QtCore, QtGui

if sys.version_info[0] < 3:
    print ("Precisa ser o Python 3")
    exit();

import asm_utils, file_utils
import config_dialog

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QHeaderView, QFileDialog, QActionGroup, QMessageBox, QProgressDialog, QVBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QDesktopServices, QBrush
from PyQt5.QtCore import QThread, QTime, QFileSystemWatcher
from main_window import *
from simulator_task import SimulatorTask
from assembler_task import AssemblerTask
from lst_parser import LSTParser


class QEditorItemModel(QStandardItemModel):
    def __init__(self, rows, column, parent):
        self.breakpoints = []
        super().__init__(rows, column, parent)

    def data(self, index, role=Qt.DisplayRole):
        res = super().data(index, role)
        if role == Qt.BackgroundRole and index.row() in self.breakpoints:
            return QtGui.QColor(QtCore.Qt.red)
        return res

    def toggle_breakpoint(self, row):
        if row in self.breakpoints:
            self.breakpoints.remove(row)
        else:
            self.breakpoints.append(row)
        index = self.index(row, 1)
        self.data(index, Qt.BackgroundRole)

    def check_breakpoint_exists(self, row):
        return row in self.breakpoints

class AppMainWindow(QMainWindow):
    resized = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

    def resizeEvent(self, event):
        self.resized.emit()
        return QMainWindow.resizeEvent(self, event)


class AppMain(Ui_MainWindow):
    RAM_VIEW_INITIAL_SIZE = 10000
    R0M_VIEW_INITIAL_SIZE = 1000
    TEMP_MAX_RAM_USE = 1024*1000
    STEP_TIMER_IN_MS = 1000

    def __init__(self):
        Ui_MainWindow.__init__(self)

        ## class Variables
        self.config_dialog = None
        self.rom_stream = None
        self.rom_path = None
        self.rom_type_sel = None
        self.rom_model = None
        self.rom_watcher = None
        self.ram_model = None
        self.data_changed = None
        self.lst_parser = None
        self.last_step = None
        self.editor_converting = False
        self.pixmap_ALU = None
        self.asm_thread = None
        self.sim_thread = None
        self.config_dialog_ui = None
        self.actionROMGroup = None
        self.actionRAMGroup = None
        self.actionREGGroup = None
        self.step_timer = None
        self.window = AppMainWindow()

        # Setup Dialog, Editor, Actions, Threads, Img Resizing
        self.setup_dialog()
        self.setupUi(self.window)
        self.setup_editor()
        self.setup_actions()
        self.setup_threads()

    def show_alu(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile("theme/alu.png"))

    def load_icon(self):
        app_icon = QtGui.QIcon()
        app_icon.addFile('theme/icon/16x16.png', QtCore.QSize(16, 16))
        app_icon.addFile('theme/icon/24x24.png', QtCore.QSize(24, 24))
        app_icon.addFile('theme/icon/32x32.png', QtCore.QSize(32, 32))
        app_icon.addFile('theme/icon/48x48.png', QtCore.QSize(48, 48))
        app_icon.addFile('theme/icon/256x256.png', QtCore.QSize(256, 256))
        return app_icon

    def setup_editor(self):
        self.rom_stream = tempfile.SpooledTemporaryFile(max_size=self.TEMP_MAX_RAM_USE, mode="w+")
        self.rom_path = None
        self.rom_type_sel = self.actionROMAssembly
        self.lst_parser = None
        self.rom_watcher = QFileSystemWatcher()
        self.rom_watcher.fileChanged.connect(self.reload_rom)
        self.editor_converting = False
        self.spinBox.setValue(100)
        self.label_A.setStyleSheet('QLabel { font-size: 12pt; }')
        self.label_D.setStyleSheet('QLabel { font-size: 12pt; }')
        self.label_S.setStyleSheet('QLabel { font-size: 12pt; }')
        self.label_inM.setStyleSheet('QLabel { font-size: 12pt; }')
        self.label_outM.setStyleSheet('QLabel { font-size: 12pt; }')
        self.toolBar.addSeparator()
        self.toolBar.addWidget(self.label)
        self.toolBar.addWidget(self.spinBox)
        self.lineEdit_A.setStyleSheet(self.style_register())
        self.lineEdit_D.setStyleSheet(self.style_register())
        self.lineEdit_S.setStyleSheet(self.style_register())
        self.lineEdit_inM.setStyleSheet(self.style_register())
        self.lineEdit_outM.setStyleSheet(self.style_register())
        self.on_new()
        self.window.setWindowIcon(self.load_icon())

    def style_register(self):
        return 'QLineEdit { border: none; background-color: transparent; font-size:12pt; color:black; }'

    def style_register_active(self):
        return 'QLineEdit { border: none; background-color: yellow; font-size:12pt; color:black; }'

    def setup_threads(self):
        self.asm_thread = QThread()
        self.sim_thread = QThread()

    def setup_dialog(self):
        self.config_dialog = QDialog()
        self.config_dialog_ui = config_dialog.Ui_Dialog()
        self.config_dialog_ui.setupUi(self.config_dialog)
        self.config_dialog_ui.assemblerLineEdit.setText("../jar/Z01-Assembler.jar")
        self.config_dialog_ui.rtlLineEdit.setText("../Z01-Simulator-rtl/")

    def setup_clean_views(self, table, rows=100, caption="Dados", line_header=None):
        model = QEditorItemModel(rows, 1, self.window)
        model.setHorizontalHeaderItem(0, QStandardItem(caption))
        table.setModel(model)
        for k in range(0, table.horizontalHeader().count()):
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for l in range(0, rows):
            if line_header is None:
                model.setHeaderData(l, QtCore.Qt.Vertical, l)
            else:
                model.setHeaderData(l, QtCore.Qt.Vertical, line_header(l))

        return model

    def setup_actions(self):
        self.step_timer = QtCore.QTimer()
        self.step_timer.timeout.connect(self.on_proximo)

        self.actionNovo.triggered.connect(self.on_new)
        self.actionSalvar_ROM.triggered.connect(self.on_save)
        self.actionAbrir.triggered.connect(self.on_load)
        self.actionProximo.triggered.connect(self.on_proximo)
        self.actionExecutarFim.triggered.connect(self.on_executar_fim)
        self.actionParar.triggered.connect(self.on_parar)
        self.actionEraseRAM.triggered.connect(self.on_clear_ram)
        self.actionVoltarInicio.triggered.connect(self.on_voltar_inicio)
        self.spinBox.valueChanged.connect(self.on_voltar_inicio)
        self.actionROMAssembly.triggered.connect(self.on_rom_assembly)
        self.actionROMBinario.triggered.connect(self.on_rom_binary)
        self.actionROMGroup = QActionGroup(self.window)
        self.actionROMGroup.addAction(self.actionROMAssembly)
        self.actionROMGroup.addAction(self.actionROMBinario)
        self.actionROMAssembly.setChecked(True)
        self.but_ALU.clicked.connect(self.show_alu)
        self.config_dialog_ui.procurarButton.clicked.connect(self.on_search_assembler)
        self.config_dialog_ui.alterarButton.clicked.connect(self.config_dialog.close)
        self.actionConfiguracoes.triggered.connect(self.config_dialog.show)

    def change_rtl_dir(self, new_dir):
        self.config_dialog_ui.rtlLineEdit.setText(new_dir)

    def on_rom_assembly(self):
        self.editor_converting = True
        self.on_clear_rom()
        file_utils.copy_file_to_model(self.rom_stream, self.rom_model)
        self.rom_type_sel = self.actionROMAssembly
        self.editor_converting = False

    def on_rom_binary(self):
        self.editor_converting = True
        if self.rom_type_sel == self.actionROMAssembly:
            file_utils.copy_model_to_file(self.rom_model, self.rom_stream)
            self.assemble(self.load_converted_asm_bin)

        self.rom_type_sel = self.actionROMBinario

    def on_ram_tooltip(self, item):
        text = item.text().strip()

        try:
            val = int(text, 2)
        except ValueError:
            return

        item.setToolTip("{0:d} dec - {1:x} hex".format(val, val))

    def on_clear_rom(self):
        if self.rom_model is not None:
            rowCount = self.rom_model.rowCount()
        else:
            rowCount = self.R0M_VIEW_INITIAL_SIZE

        self.rom_model = self.setup_clean_views(self.romView, rows=rowCount, caption="ROM")
        self.romView.verticalHeader().sectionClicked.connect(self.rom_model.toggle_breakpoint)

    def on_clear_ram(self):
        self.ram_model = self.setup_clean_views(self.ramView, rows=self.RAM_VIEW_INITIAL_SIZE, caption="RAM", line_header=asm_utils.z01_ram_name)
        for i in range(0, self.RAM_VIEW_INITIAL_SIZE):
            item = QStandardItem("0000000000000000")
            self.on_ram_tooltip(item)
            self.ram_model.setItem(i, item)


    def on_new(self):
        self.rom_path = None
        self.on_clear_ram()
        self.on_clear_rom()
        self.rom_model.itemChanged.connect(self.valid_rom)
        self.ram_model.itemChanged.connect(self.valid_ram)
        self.actionROMAssembly.setEnabled(True)

        self.clear_simulation()

    def on_voltar_inicio(self):
        self.data_changed = True
        self.clear_simulation()

    def on_parar(self):
        self.step_timer.stop()

    def on_executar_fim(self):
        self.step_timer.start(self.STEP_TIMER_IN_MS)

    def show(self):
        self.window.show()

    def on_save(self):
        filename = self.rom_path

        if self.rom_path is not None:
            self.rom_watcher.removePath(self.rom_path)

        if filename is None:
            filename = QFileDialog.getSaveFileName(self.window, "Salve o arquivo", os.getcwd(), "Arquivos (*.hack *.nasm)")
            if len(filename) == 0 or len(filename[0]) == 0:
                return None
            filename = filename[0]
            self.rom_path = filename

        if self.actionROMAssembly.isChecked():
            file_utils.copy_model_to_file(self.rom_model, self.rom_stream)

        file_utils.stream_to_file(self.rom_stream, filename)
        self.rom_watcher.addPath(self.rom_path)

    def on_load(self):
        filename = QFileDialog.getOpenFileName(self.window, "Escolha arquivo", os.getcwd(), "Arquivos (*.asm *.hack *.nasm)")
        if len(filename) == 0 or len(filename[0]) == 0:
            return None

        if self.rom_path is not None:
            self.rom_watcher.removePath(self.rom_path)

        self.on_new()
        self.rom_path = filename[0]
        self.rom_watcher.addPath(self.rom_path)
        self.reload_rom()

    def reload_rom(self):
        return self.load_rom(self.rom_path)

    def load_rom(self, filename):
        if not os.path.exists(filename):
            return

        if filename.endswith(".asm") or filename.endswith(".nasm"):
            self.load_asm(filename, self.rom_model)
        elif filename.endswith(".bin") or filename.endswith(".hack"):
            self.load_bin(filename, self.rom_model)

    def on_search_assembler(self):
        filename = QFileDialog.getOpenFileName(self.window, "Escolha arquivo", os.getcwd(), "Arquivo JAR (*.jar)")
        if len(filename) == 0 or len(filename[0]) == 0:
            return None

        self.config_dialog_ui.assemblerLineEdit.setText(filename[0])

    def on_proximo(self):
        if self.data_changed:
            if self.lst_parser is not None:
                self.lst_parser.close()

            if self.actionROMAssembly.isChecked():
                file_utils.copy_model_to_file(self.rom_model, self.rom_stream)
                self.assemble(self.assemble_end)
            else:
                tmp_rom = tempfile.SpooledTemporaryFile(max_size=self.TEMP_MAX_RAM_USE, mode="w+")
                file_utils.copy_model_to_file(self.rom_model, tmp_rom)
                tmp_ram = self.get_updated_ram()
                self.simulate(tmp_rom, tmp_ram)
            return False
        step = self.lst_parser.advance()

        if "s_regAout" not in step:
            self.step_timer.stop()
            QMessageBox.warning(self.window, "Simulador", "Fim de simulação")
            return

        self.update_line_edit(self.lineEdit_A, step["s_regAout"])
        self.update_line_edit(self.lineEdit_S, step["s_regSout"])
        self.update_line_edit(self.lineEdit_D, step["s_regDout"])
        self.update_line_edit(self.lineEdit_inM, step["inM"])
        self.update_line_edit(self.lineEdit_outM, step["outM"])

        if self.last_step is not None:
            addr = int(step["s_regAout"], 2)
            index = self.ram_model.index(addr, 0)
            last_pc_counter = int(self.last_step["pcout"], 2)

            if int(step["writeM"]) == 0 and int(step["c_muxALUI_A"]) == 1 and int(self.last_step["c_muxALUI_A"]) == 0:
               self.ramView.setCurrentIndex(index)

            if int(step["writeM"]) == 1:
               self.ramView.setCurrentIndex(index)
               self.ram_model.itemFromIndex(index).setText(step["outM"])
        else:
            last_pc_counter = 0

        ## update ROM line
        pc_counter = int(step["pcout"], 2)

        if pc_counter < 0:
            pc_counter = 0

        if self.actionROMAssembly.isChecked():
            rom_line = asm_utils.z01_real_line(self.assembler_task.labels_pos, pc_counter)
        else:
            rom_line = pc_counter

        if self.rom_model.check_breakpoint_exists(rom_line):
            self.step_timer.stop()

        index = self.rom_model.index(rom_line, 0)
        self.romView.setCurrentIndex(index)

        print("PROXIMO")
        self.last_step = step

    def update_line_edit(self, line_edit, new_value, ignore=False):
        if line_edit.text() != new_value:
            line_edit.setText(new_value)
            if not ignore:
                line_edit.setStyleSheet(self.style_register_active())
            valid = self.valid_binary(line_edit)
            if valid:
                self.on_ram_tooltip(line_edit)
        else:
            line_edit.setStyleSheet(self.style_register())

    def valid_rom(self, item):
        if not item.text():
            return None

        text = item.text()
        index = item.index()

        while index.row() + 50 >= self.rom_model.rowCount():
            self.rom_model.appendRow(QStandardItem(""))


        if self.actionROMAssembly.isChecked():
            valid = asm_utils.z01_valid_assembly(item.text())
        elif self.actionROMBinario.isChecked():
            valid = self.valid_binary(item)
        else:
            valid = True

        if valid:
            if (self.actionROMBinario.isChecked()) and self.editor_converting is False:
                self.actionROMAssembly.setEnabled(False)
            self.data_changed = True
        else:
            item.setText("")

    def valid_ram(self, item):
        if not item.text():
            return None
        text = item.text()
        index = item.index()

        while index.row() + 100 >= self.ram_model.rowCount():
            self.ram_model.appendRow(QStandardItem("{0:0>16b}".format(0)))

        if text.startswith("d"):
            text = text[1:]
            if text.isdigit():
                item.setText("{0:0>16b}".format(int(text)))

        valid = self.valid_binary(item)

        if valid:
            #self.data_changed = True
            self.on_ram_tooltip(item)
        else:
            item.setText("{0:0>16b}".format(0))

    def assemble(self, callback):
        if self.asm_thread.isRunning() or self.sim_thread.isRunning():
            print("Assembler está sendo executado...")
            return False

        assembler = "java -jar " + self.config_dialog_ui.assemblerLineEdit.text()
        self.assembler_task = AssemblerTask(assembler, "temp/")
        rom_in = tempfile.SpooledTemporaryFile(max_size=self.TEMP_MAX_RAM_USE, mode="w+")
        rom_out = tempfile.SpooledTemporaryFile(max_size=self.TEMP_MAX_RAM_USE, mode="w+")
        file_utils.copy_file_to_file(self.rom_stream, rom_in)
        self.assembler_task.setup(rom_in, rom_out)
        self.assembler_task.finished.connect(callback)
        self.assembler_task.moveToThread(self.asm_thread)
        self.asm_thread.started.connect(self.assembler_task.run)
        self.asm_thread.start()


    def simulate(self, rom_file, ram_file):
        if self.asm_thread.isRunning() or self.sim_thread.isRunning():
            print("Simulador está sendo executado...")
            return False

        self.simulator_task = SimulatorTask("temp/", False, self.config_dialog_ui.simGUIBox.isChecked(), self.config_dialog_ui.rtlLineEdit.text())
        lst_out = tempfile.SpooledTemporaryFile(max_size=self.TEMP_MAX_RAM_USE, mode="w+")
        self.simulator_task.setup(rom_file, ram_file, lst_out, self.spinBox.value()*10+10)
        self.simulator_task.finished.connect(self.simulation_end)
        self.simulator_task.moveToThread(self.sim_thread)
        self.sim_thread.started.connect(self.simulator_task.run)
        self.sim_thread.start()
        self.lock_and_show_dialog()

    def lock_and_show_dialog(self):
        ## waits for ASM thread and SIM thread to end
        self.progress_dialog = QProgressDialog("Simulando...", "Cancelar", 0, 0, self.window)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        self.progress_dialog.setWindowTitle("RESimulatorGUI")
        self.progress_dialog.setWindowFlags(self.progress_dialog.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)

        while self.asm_thread.isRunning() or self.sim_thread.isRunning():
            qapp.processEvents()

        self.progress_dialog.reset()

    def get_updated_ram(self):
        ram = tempfile.SpooledTemporaryFile(max_size=self.TEMP_MAX_RAM_USE, mode="w+")
        file_utils.copy_model_to_file(self.ram_model, ram)
        return ram

    def check_assembler_sucess(self):
        if self.assembler_task is not None and self.assembler_task.success is True:
            return True
        QMessageBox.critical(self.window, "Assembler", "Erro ao traduzir assembly.")
        self.step_timer.stop()
        return False

    def assemble_end(self):
        self.asm_thread.quit() # ensure end of thread
        self.asm_thread.wait()
        ram = self.get_updated_ram()
        if not self.check_assembler_sucess():
            return
        print("ASM done!")
        self.simulate(self.assembler_task.stream_out, ram)

    def simulation_end(self):
        self.sim_thread.quit() #ensure end of thread
        self.sim_thread.wait()
        print("SIM done!")
        self.data_changed = False
        self.lst_parser = LSTParser(self.simulator_task.lst_stream)

        if self.actionROMAssembly.isChecked():
            rom_line = asm_utils.z01_real_line(self.assembler_task.labels_pos, 0)
        else:
            rom_line = 0
        index = self.rom_model.index(rom_line, 0)
        self.romView.setCurrentIndex(index)

    def load_converted_asm_bin(self):
        self.asm_thread.quit()
        self.asm_thread.wait()
        if not self.check_assembler_sucess():
            return
        self.on_clear_rom()
        file_utils.copy_file_to_model(self.assembler_task.stream_out, self.rom_model)
        self.editor_converting = False

    def load_converted_asm_hex(self):
        self.asm_thread.quit()
        self.asm_thread.wait()
        if not self.check_assembler_sucess():
            return
        self.on_clear_rom()
        file_utils.copy_file_to_model(self.assembler_task.stream_out, self.rom_model, asm_utils.bin_str_to_hex)
        self.editor_converting = False

    def valid_binary(self, item):
        valid = True
        text = item.text().strip()

        try:
            val = int(text, 2)
        except ValueError:
            valid = False

        if not valid:
           print("Invalid BIN Instruction: {}".format(item.text()))

        return valid

    def clear_simulation(self):
        self.last_step = None
        self.update_line_edit(self.lineEdit_A, "0000000000000000", True)
        self.update_line_edit(self.lineEdit_S, "0000000000000000", True)
        self.update_line_edit(self.lineEdit_D, "0000000000000000", True)
        self.update_line_edit(self.lineEdit_inM, "0000000000000000", True)
        self.update_line_edit(self.lineEdit_outM, "0000000000000000", True)
        self.data_changed = True
        index = self.ram_model.index(0, 0)
        self.ramView.setCurrentIndex(index)
        index = self.rom_model.index(0, 0)
        self.romView.setCurrentIndex(index)

    def load_file(self, filename, model):
        fp = open(filename, "r")
        counter = 0
        lines = file_utils.file_len(filename)
        self.rom_model = self.setup_clean_views(self.romView, rows=lines + 200, caption="ROM")
        self.on_clear_rom()

        for i, l in enumerate(fp):
            if asm_utils.z01_valid_assembly(l.strip()):
                index = self.rom_model.index(counter, 0)
                self.rom_model.itemFromIndex(index).setText(l.strip())
                counter += 1
        fp.close()

    def load_asm(self, filename, model):
        self.actionROMAssembly.setChecked(True)
        self.load_file(filename, model)

    def load_bin(self, filename, model):
        self.actionROMBinario.setChecked(True)
        self.actionROMAssembly.setEnabled(False)
        self.load_file(filename, model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Z01 Simulator command line options")
    parser.add_argument("--rtl_dir", default=None)
    args = parser.parse_args()
    qapp = QApplication(sys.argv)
    app = AppMain()
    if args.rtl_dir is not None:
    	app.change_rtl_dir(args.rtl_dir)
    app.show()
    sys.exit(qapp.exec_())

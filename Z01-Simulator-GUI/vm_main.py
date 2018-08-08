# -*- coding: utf-8 -*-
# Eduardo Marossi & Rafael Corsi @ insper.edu.br
# Dez/2017
# Disciplina Elementos de Sistemas
import sys, os, tempfile
import argparse

if sys.version_info[0] < 3:
	print ("Precisa ser o Python 3")
	exit()

import asm_utils, file_utils
import config_dialog
import vm_utils
import time
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QHeaderView, QFileDialog, QMessageBox, QProgressDialog
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QThread, QTime, QFileSystemWatcher
from vm_window import *
from simulator_task import SimulatorTask
from assembler_task import AssemblerTask
from vm_task import VMTask
from lst_parser import LSTParser


class AppMainWindow(QMainWindow):
	resized = QtCore.pyqtSignal()

	def __init__(self, parent=None):
		QMainWindow.__init__(self, parent)

	def resizeEvent(self, event):
		self.resized.emit()
		return QMainWindow.resizeEvent(self, event)


class AppMain(Ui_MainWindow):
	RAM_VIEW_INITIAL_SIZE = 10000
	TEMP_MAX_RAM_USE = 1024*1000
	STEP_TIMER_IN_MS = 100

	def __init__(self):
		Ui_MainWindow.__init__(self)

		## class Variables
		self.config_dialog = None
		self.rom_stream = None
		self.rom_path = None
		self.rom_model = None
		self.rom_watcher = None
		self.ram_model = None
		self.sim_real_line_old = 0
		self.sim_real_line_current = 0
		self.local_stack_model = None
		self.global_stack_model = None
		self.data_changed = None
		self.lst_parser = None
		self.sim_line = 0
		self.last_step = None
		self.asm_thread = None
		self.sim_thread = None
		self.vm_thread = None
		self.vm_task = None
		self.simulator_task = None
		self.assembler_task = None
		self.config_dialog_ui = None
		self.step_timer = None
		self.window = AppMainWindow()


		# Setup Dialog, Editor, Actions, Threads, Img Resizing
		self.setup_dialog()
		self.setupUi(self.window)
		self.setup_editor()
		self.setup_actions()
		self.setup_threads()

	def setup_editor(self):
		self.rom_stream = tempfile.SpooledTemporaryFile(max_size=self.TEMP_MAX_RAM_USE, mode="w+")
		self.rom_path = None
		self.lst_parser = None
		self.rom_watcher = QFileSystemWatcher()
		self.rom_watcher.fileChanged.connect(self.reload_rom)
		self.spinBox.setValue(500)
		self.on_new()

	def setup_threads(self):
		self.asm_thread = QThread()
		self.sim_thread = QThread()
		self.vm_thread = QThread()

	def setup_dialog(self):
		self.config_dialog = QDialog()
		self.config_dialog_ui = config_dialog.Ui_Dialog()
		self.config_dialog_ui.setupUi(self.config_dialog)
		self.config_dialog_ui.assemblerLineEdit.setText("../jar/Z01-Assembler.jar")
		self.config_dialog_ui.rtlLineEdit.setText("../Z01-Simulator-rtl-2/")

	def setup_clean_views(self, table, rows=100, caption="Dados", line_header=None):
		model = QStandardItemModel(rows, 1, self.window)
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
		self.config_dialog_ui.procurarButton.clicked.connect(self.on_search_assembler)
		self.config_dialog_ui.alterarButton.clicked.connect(self.config_dialog.close)
		self.actionConfiguracoes.triggered.connect(self.config_dialog.show)

	def change_rtl_dir(self, new_dir):
		self.config_dialog_ui.rtlLineEdit.setText(new_dir)

	def on_ram_tooltip(self, item):
		text = item.text().strip()

		try:
			val = int(text, 2)
		except ValueError:
			return

		item.setToolTip("{0:d} dec - {1:x} hex".format(val, val))

	def on_clear_ram(self):
		self.ram_model = self.setup_clean_views(self.ramView, rows=self.RAM_VIEW_INITIAL_SIZE, caption="RAM",
												line_header=asm_utils.z01_ram_name)
		for i in range(0, self.RAM_VIEW_INITIAL_SIZE):
			item = QStandardItem("0000000000000000")
			self.on_ram_tooltip(item)
			self.ram_model.setItem(i, item)

	def on_new(self):
		self.rom_path = None
		self.on_clear_ram()
		self.rom_model = self.setup_clean_views(self.romView, caption="Program")
		#self.local_stack_model = self.setup_clean_views(self.localStackView, caption="Local Stack")
		self.global_stack_model = self.setup_clean_views(self.globalStackView, caption="Global Stack",
														 line_header=vm_utils.vm_global_stack_name)
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
			filename = QFileDialog.getSaveFileName(self.window, "Salve o arquivo", os.getcwd(), "Arquivos (*.vm)")
			if len(filename) == 0 or len(filename[0]) == 0:
				return None
			filename = filename[0]
			self.rom_path = filename

		file_utils.copy_model_to_file(self.rom_model, self.rom_stream)
		file_utils.stream_to_file(self.rom_stream, filename)

		self.rom_watcher.addPath(self.rom_path)

	def on_load(self):
		filename = QFileDialog.getOpenFileName(self.window, "Escolha arquivo", os.getcwd()+"/examples/", "Arquivos (*.vm)")
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

		if filename.endswith(".asm") or filename.endswith(".vm"):
			self.load_vm(filename, self.rom_model)

	def on_search_assembler(self):
		filename = QFileDialog.getOpenFileName(self.window, "Escolha arquivo", os.getcwd(), "Arquivo JAR (*.jar)")
		if len(filename) == 0 or len(filename[0]) == 0:
			return None

		self.config_dialog_ui.assemblerLineEdit.setText(filename[0])


	def on_proximo(self):

		if self.data_changed:
			if self.lst_parser is not None:
				self.lst_parser.close()
			self.sim_line = 0
			file_utils.copy_model_to_file(self.rom_model, self.rom_stream)
			self.vm_translate(self.vm_end)
			return False

		while(True):

			#time.sleep(0.4)  # esse timer nao funcionou como eu esperava !

			self.sim_real_line_old = self.sim_real_line_current

			step = self.lst_parser.advance()

			if "s_regAout" not in step:
				self.step_timer.stop()
				QMessageBox.warning(self.window, "Simulador", "Fim de simulação")
				return False

			self.update_line_edit(self.lineEdit_SP, self.model_get_value(self.ram_model, 0))
			self.update_line_edit(self.lineEdit_LCL, self.model_get_value(self.ram_model, 1))
			self.update_line_edit(self.lineEdit_ARG, self.model_get_value(self.ram_model, 2))
			self.update_line_edit(self.lineEdit_THIS, self.model_get_value(self.ram_model, 3))
			self.update_line_edit(self.lineEdit_THAT, self.model_get_value(self.ram_model, 4))

			sp_index = self.ram_model.index(0, 0)  # SP

			if self.last_step is not None:
				addr = int(step["s_regAout"], 2)
				index = self.ram_model.index(addr, 0)
				last_sp = int(self.ram_model.itemFromIndex(sp_index).text(), 2)

				if int(step["writeM"]) == 0 and int(step["s_muxALUI_A"]) == 1 and int(self.last_step["s_muxALUI_A"]) == 0:
				   self.ramView.setCurrentIndex(index)

				if int(step["writeM"]) == 1:
				   self.ramView.setCurrentIndex(index)
				   self.ram_model.itemFromIndex(index).setText(step["outM"])
			else:
				last_sp = 256


			## descobrir linha com base no SP
			sp = int(self.ram_model.itemFromIndex(sp_index).text(), 2)
			if sp != last_sp:
				self.sim_line += 1

			self.refresh_stack(self.ram_model, 256, sp, self.global_stack_model, self.globalStackView)

			## update line
			pc = int(step["pcout"], 2) - 1
			self.sim_real_line_current = vm_utils.vm_command_line(self.assembler_task.commands_pos, self.assembler_task.comments_pos, self.assembler_task.labels_pos, pc)

			index = self.rom_model.index(self.sim_real_line_current, 0)
			self.romView.setCurrentIndex(index)

			print("PROXIMA INSTRUCAO NASM")
			self.last_step = step

			if(self.sim_real_line_current != self.sim_real_line_old):
				print("PROXIMA INSTRUCAO VM")
				break

	def model_get_value(self, model, row):
		index = model.index(row, 0)
		return model.itemFromIndex(index).text()

	def model_set_value(self, model, row, value, tooltip=False):
		index = model.index(row, 0)
		model.itemFromIndex(index).setText(value)
		self.on_ram_tooltip(model.itemFromIndex(index))
		if tooltip:
			self.on_ram_tooltip(model.itemFromIndex(index))

	def refresh_stack(self, ram_model, start_addr, end_addr, target_model, target_view):
		line = 0
		for i in range(start_addr, end_addr, 1):
			self.model_set_value(target_model, line, self.model_get_value(ram_model, i))
			line += 1
		index = target_model.index(line, 0)
		target_view.setCurrentIndex(index)

		for i in range(line, line+10):
			self.model_set_value(target_model, i, "")

	def update_line_edit(self, line_edit, new_value, ignore=False):
		if line_edit.text() != new_value:
			line_edit.setText(new_value)
			if not ignore:
				line_edit.setStyleSheet("QLineEdit {background-color: yellow;}")
			self.on_ram_tooltip(line_edit)
		else:
			line_edit.setStyleSheet("")

	def valid_rom(self, item):
		if not item.text():
			return None

		index = item.index()

		while index.row() + 50 >= self.rom_model.rowCount():
			self.rom_model.appendRow(QStandardItem(""))

		if not vm_utils.vm_valid_command(item.text()):
			item.setText("")

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
			self.on_ram_tooltip(item)
		else:
			item.setText("{0:0>16b}".format(0))

	def vm_translate(self, callback):
		if self.asm_thread.isRunning() or self.sim_thread.isRunning() or self.vm_thread.isRunning():
			print("[vm_translate] Tarefas de simulação em processamento por favor aguarde finalizar....")
			return False

		vm_translator = "java -jar ../jar/Z01-VMTranslator.jar"
		self.vm_task = VMTask(vm_translator, "temp/", True)
		nasm_out = tempfile.SpooledTemporaryFile(max_size=self.TEMP_MAX_RAM_USE, mode="w+")
		self.vm_task.setup(self.rom_stream, nasm_out)
		self.vm_task.finished.connect(callback)
		self.vm_task.moveToThread(self.vm_thread)
		self.vm_thread.started.connect(self.vm_task.run)
		self.vm_thread.start()

	def assemble(self, callback, nasm_file):
		if self.asm_thread.isRunning() or self.sim_thread.isRunning():
			print("[assemble] Tarefas de simulação em processamento por favor aguarde finalizar....")
			return False

		assembler = "java -jar " + self.config_dialog_ui.assemblerLineEdit.text()
		self.assembler_task = AssemblerTask(assembler, "temp/")
		rom_out = tempfile.SpooledTemporaryFile(max_size=self.TEMP_MAX_RAM_USE, mode="w+")
		self.assembler_task.setup(nasm_file, rom_out)
		self.assembler_task.finished.connect(callback)
		self.assembler_task.moveToThread(self.asm_thread)
		self.asm_thread.started.connect(self.assembler_task.run)
		self.asm_thread.start()

	def simulate(self, rom_file, ram_file):
		if self.asm_thread.isRunning() or self.sim_thread.isRunning():
			print("[simulate] Tarefas de simulação em processamento por favor aguarde finalizar....")
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

	def check_vm_sucess(self):
		if self.vm_task is not None and self.vm_task.success is True:
			return True
		QMessageBox.critical(self.window, "VM Translator", "Erro ao traduzir código VM para Assembly.")
		self.step_timer.stop()
		return False

	def vm_end(self):
		self.vm_thread.quit()
		self.vm_thread.wait()
		if not self.check_vm_sucess():
			return
		print("VM Translator done!")
		self.assemble(self.assemble_end, self.vm_task.stream_out)

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

	def clear_simulation(self):
		self.last_step = None
		self.update_line_edit(self.lineEdit_SP, "0000000000000000", True)
		self.update_line_edit(self.lineEdit_LCL, "0000000000000000", True)
		self.update_line_edit(self.lineEdit_ARG, "0000000000000000", True)
		self.update_line_edit(self.lineEdit_THIS, "0000000000000000", True)
		self.update_line_edit(self.lineEdit_THAT, "0000000000000000", True)
		self.data_changed = True
		index = self.ram_model.index(0, 0)
		self.ramView.setCurrentIndex(index)
		index = self.rom_model.index(0, 0)
		self.romView.setCurrentIndex(index)

	def load_file(self, filename, model):
		fp = open(filename, "r")
		counter = 0
		lines = file_utils.file_len(filename)
		self.rom_model = self.setup_clean_views(self.romView, rows=lines + 200, caption="Program")
		for i, l in enumerate(fp):
			if vm_utils.vm_valid_command(l.strip()):
				index = self.rom_model.index(counter, 0)
				self.rom_model.itemFromIndex(index).setText(l.strip())
				counter += 1
		fp.close()

	def load_vm(self, filename, model):
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

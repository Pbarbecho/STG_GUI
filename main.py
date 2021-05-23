import multiprocessing
import os, sys, time
from PyQt5.QtWidgets import *  # import sections
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from randomTrips import rt
from utils import create_folder
import subprocess


class DlgMain(QDialog):
    def __init__(self):
        super().__init__()

        # initial configurations
        self.realtraffic = ''
        self.simtime = 1
        self.taz_file = ''
        self.O_district = ''
        self.D_district = ''
        self.processors = multiprocessing.cpu_count()
        self.SUMO_exec = os.environ['SUMO_HOME']
        self.parents_dir = os.path.dirname(os.path.abspath('{}/'.format(__file__)))
        self.trips = ''
        self.outputs = ''
        self.SUMO_tool = ''
        self.SUMO_outputs = ''
        self.O = ''
        self.dua = ''
        self.ma = ''
        self.cfg = ''
        self.detector = ''
        self.xmltocsv = ''
        self.parsed = ''
        self.reroute = ''
        self.edges = ''
        self.reroute_probability = 0
        self.sumo_var_tripinfo = False
        self.sumo_var_emissions = False
        self.sumo_var_summary = False
        self.routing = ''
        self.osm = ''
        self.network = ''
        self.poly = ''

        # ventana principal
        self.setWindowTitle("STG")
        self.resize(400, 500)

        ####################### CREATE LABELS ########################
        # TITLES FONTS
        title_font = QFont("Times New Roman", 20, 75, False)
        subtitle_font = QFont("Times New Roman", 13, 13, False)
        # MAIN LABEL
        self.title_label = QLabel('SUMO Traffic Generation')
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        # requirements label
        self.requirements_label = QLabel('Requirements:')
        ###################### PROGRESS BAR ##########################
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyle(QStyleFactory.create('Windows'))
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        ####################### User text inputs districts ##################################
        self.O_distric = QPlainTextEdit()
        self.O_distric.setPlaceholderText('Enter the Origin District NAME as in the TAZ file')
        self.D_distric = QPlainTextEdit()
        self.D_distric.setPlaceholderText('Enter the Destination District NAME as in the TAZ file')
        #######################  BUILD NETWORK LOG TEXT BOX  ################################
        self.cmd_str = QPlainTextEdit()
        self.cmd_str.setPlaceholderText('Console logs')
        ######################  Text box  description of sumo tools     #####################
        self.RT_description = QTextEdit()
        self.MA_description = QTextEdit()
        self.DUA_description = QTextEdit()
        self.DUAI_description = QTextEdit()
        self.OD2_description = QTextEdit()

        #########
        # TO DO FALTA CREAR TEXTO HTML CON  LA DESCRIPCION DE CADA HERRAMIENTA
        html_RT = """
        < b > This text is bold < / b >
        """
        self.RT_description.setText(html_RT)
        self.RT_description.setReadOnly(True)
        self.MA_description.setText(html_RT)
        self.MA_description.setReadOnly(True)
        self.DUA_description.setText(html_RT)
        self.DUA_description.setReadOnly(True)
        self.DUAI_description.setText(html_RT)
        self.DUAI_description.setReadOnly(True)
        self.OD2_description.setText(html_RT)
        self.OD2_description.setReadOnly(True)

        #'The DUAIterate uses an assignment method called iter-ative, see Table 1, which tries to calculate the user equilibrium,meaning that it generate a route for each vehicle where the routecost (e.g., travel time) cannot be reduced by using an alterna-tive route.  This is done by iteratively calling the DUAR tool'
        #'The DUAR tool imports differ-ent demand definitions (trips or flows).'
        #('This tool allows researchers to quicklygenerate a set of random trips within a time interval. The RT tool prevents bottlenecksin the network. ')
        #'Generates random distribuition of vehicles'

        ##########################  TRAFFIC DEMAND BUTTONS    ################################
        # osm file
        self.osm_file_btn = QPushButton('OSM File')
        self.osm_file_btn.clicked.connect(self.evt_osm_file_btn_clicked)

        # Netconvert button
        self.netconvert_btn = QPushButton('Netconvert')
        self.netconvert_btn.clicked.connect(self.evt_netconvert_btn_clicked)

        # Polyconvert
        self.polyconvert_btn = QPushButton('Polyconvert')
        self.polyconvert_btn.clicked.connect(self.evt_polyconvert_btn_clicked)

        # Check boxes
        self.check_osm_file = QCheckBox()
        self.check_netconvert_file = QCheckBox()
        self.check_polyconvert_file = QCheckBox()
        self.check_osm_file.setEnabled(False)
        self.check_netconvert_file.setEnabled(False)
        self.check_polyconvert_file.setEnabled(False)

        # check box for netconvert
        self.netconvert_options_groupbox = QGroupBox()
        self.netconvert_urban_op = QCheckBox('Urban')
        self.netconvert_urban_op.setChecked(True)
        self.netconvert_highway_op = QCheckBox('Highway')
        self.netconvert_highway_op.setEnabled(False)
        self.netconvert_urban_op.toggled.connect(self.evt_netconvert_urban_op)
        self.netconvert_highway_op.toggled.connect(self.evt_netconvert_highway_op)

        #   GROUP BOXES  NETWORK BUILD
        self.osm_groupbox = QGroupBox('1. Select OpenStreetMaps file (.osm)')
        self.netconvert_groupbox = QGroupBox('2. Generate SUMO network file (.net.xml)')
        self.polyconvert_groupbox = QGroupBox('3. Generate polygons of the map (.poly.xml)')
        self.osm_groupbox.setFont(subtitle_font)
        self.netconvert_groupbox.setFont(subtitle_font)
        self.polyconvert_groupbox.setFont(subtitle_font)

        #######################    BUILD TRAFFIC BUTTONS   ############################
        # check box for sumo outputs
        self.sumo_groupbox = QGroupBox('SUMO Outputs')
        self.sumo_groupbox.setFont(subtitle_font)
        self.sumo_output_tripinfo = QCheckBox('Tripinfo')
        self.sumo_output_emissions = QCheckBox('Emissions')
        self.sumo_output_summary = QCheckBox('Summary')
        self.sumo_output_tripinfo.toggled.connect(self.evt_tripinfo_clicked)
        self.sumo_output_emissions.toggled.connect(self.evt_emissions_clicked)
        self.sumo_output_summary.toggled.connect(self.evt_summary_clicked)
        # spinbox for reroute probability
        self.sumo_rerouting_prob_spin = QSpinBox()
        self.sumo_rerouting_prob_spin.setWrapping(True)
        self.sumo_rerouting_prob_spin.setRange(0, 100)
        self.sumo_rerouting_prob_spin.setValue(0)
        self.sumo_rerouting_prob_spin.setSingleStep(10)
        self.sumo_rerouting_prob_spin.valueChanged.connect(self.evt_sumo_rerouting_prob_spin_clicked)
        # spinbox for number of simulation hours
        self.simtime_int_btn = QSpinBox()
        self.simtime_int_btn.setWrapping(True)
        self.simtime_int_btn.setRange(1, 24)
        self.simtime_int_btn.setValue(1)
        self.simtime_int_btn.setSingleStep(1)
        self.simtime_int_btn.valueChanged.connect(self.evt_simtime_int_btn_clicked)
        # READ ORIGIN TAZ button open File
        self.taz_file_btn = QPushButton('TAZ File')
        self.taz_file_btn.clicked.connect(self.evt_taz_file_btn_clicked)
        # READ real traffic button open File
        self.rt_file_btn = QPushButton('Traffic File')
        self.rt_file_btn.clicked.connect(self.evt_rt_file_btn_clicked)
        # Output button save File
        self.outputFile_btn = QPushButton('Output')
        self.outputFile_btn.clicked.connect(self.evt_output_file_clicked)
        # generate simulation button
        self.gen_btn = QPushButton('Generate', self)
        self.gen_btn.clicked.connect(self.evt_gen_btn_clicked)

        ########################     INSTANCIATE  TAB WIDGET  #############################
        self.tab_main_menu = QTabWidget()
        self.tab_main = QTabWidget()
        self.tab_selector = QTabWidget()

        # INSTANCIATE widgets for each TAB option
        self.wdg_build_network = QWidget()
        self.wdg_traffic_demand = QWidget()
        self.wdg_simulation = QWidget()
        self.wdg_outputs = QWidget()

        # INSTANCIATE widgets for each radio option
        self.wdg_RT = QWidget()
        self.wdg_MA = QWidget()
        self.wdg_DUA = QWidget()
        self.wdg_DUAI = QWidget()
        self.wdg_OD2 = QWidget()

        # create widgets for TAB options
        self.wdg_inputs = QWidget()
        self.wdg_outputs = QWidget()

        # SETUP LAYOUT
        self.setuplayout()


    #########################   GENERAL FUNCTIONS ############################################
    def Update_SUMO_exec_path(self):
        if self.SUMO_exec == '':
            warn_empty = QMessageBox.information(self, 'Missing File', 'Please set SUMO_HOME variable in your system.')
            # sys.exit('SUMO_HOME environment variable is not found.')
        else:
            # Update SUMO bin path
            list_sumo_path = os.path.abspath(self.SUMO_exec).split('/')
            if 'bin' not in list_sumo_path:
                self.SUMO_exec = os.path.join(self.SUMO_exec, 'bin/')

    def update_paths(self):
        self.SUMO_outputs = os.path.join(self.parents_dir, 'outputs')
        if not os.path.lexists(self.SUMO_outputs): os.makedirs(self.SUMO_outputs)
        self.SUMO_tool = os.path.join(self.SUMO_outputs, self.tool)
        create_folder(self.SUMO_tool)
        subfolders = ['trips', 'O', 'dua', 'ma', 'cfg', 'outputs', 'detector', 'xmltocsv', 'parsed', 'reroute',
                      'edges', 'duaiterate']
        # create subfolders
        for sf in subfolders : create_folder(os.path.join(self.SUMO_tool, sf))
        # update subfolders paths
        self.trips = os.path.join(self.SUMO_tool, 'trips')
        self.O = os.path.join(self.SUMO_tool, 'O')
        self.dua = os.path.join(self.SUMO_tool, 'dua')
        self.ma = os.path.join(self.SUMO_tool, 'ma')
        self.cfg = os.path.join(self.SUMO_tool, 'cfg')
        self.outputs = os.path.join(self.SUMO_tool, 'outputs')
        self.detector = os.path.join(self.SUMO_tool, 'detector')
        self.xmltocsv = os.path.join(self.SUMO_tool, 'xmltocsv')
        self.parsed = os.path.join(self.SUMO_tool, 'parsed')
        self.reroute = os.path.join(self.SUMO_tool, 'reroute')
        self.edges = os.path.join(self.SUMO_tool, 'edges')

    def get_selected_tool_str(self):
        tool_index = self.tab_selector.currentIndex()
        switcher = {0: "rt",1: "ma",2: "dua",3: "duai", 3:"od2"}
        return switcher.get(tool_index)

    #########################  DEFINE BUILD NETWORK  EVENTS #############################################
    def evt_osm_file_btn_clicked(self):
        fpath, extension = QFileDialog.getOpenFileName(self, 'Open File', '/Users/Pablo/',
                                                          'OSM File (*.osm)')
        self.osm = fpath
        self.check_osm_file.setChecked(True)
        self.cmd_str.setPlainText(f'OSM file successfully imported from: {fpath}')
        QMessageBox.information(self, 'Ok', 'OSM File imported')


    def evt_polyconvert_btn_clicked(self):
        if self.network:
            osm_parent_dir = os.path.dirname(self.osm)
            temp_poly_loc = os.path.join(osm_parent_dir,'osm.poly.xml')
            cmd = f'polyconvert -n {self.network} --osm-files {self.osm} -o {temp_poly_loc} --ignore-errors true'
            # convert to list for subprocess popoen
            cmd_list = cmd.split(' ')

            try:
                subprocess.Popen(cmd_list)
                self.poly = temp_poly_loc
                self.check_polyconvert_file.setChecked(True)
                self.cmd_str.setPlainText(f'Polygons file successfully generated: {cmd}')
                QMessageBox.information(self, 'Ok', 'Polygons file successfully generated')
            except Exception as e:
                self.cmd_str.setPlainText(str(e))
                QMessageBox.information(self, 'Error', 'SUMO polyconvert tool cannot executed. See console logs.')
        else:
            QMessageBox.information(self, 'Missing File', 'SUMO Network file is missing')


    def evt_netconvert_btn_clicked(self):
        self.Update_SUMO_exec_path()
        if self.osm:
            osm_parent_dir = os.path.dirname(self.osm)
            temp_network_loc = os.path.join(osm_parent_dir, 'osm.net.xml')

            # TO DO update highway else netconvert options
            if self.netconvert_urban_op.isChecked():
                cmd = f'{self.SUMO_exec}./netconvert -W --opposites.guess.fix-lengths --no-left-connections --check-lane-foes.all --junctions.join-turns --junctions.join --roundabouts.guess --no-turnarounds.tls --no-turnarounds --plain.extend-edge-shape --remove-edges.isolated --show-errors.connections-first-try --keep-edges.by-vclass passenger --ramps.guess --rectangular-lane-cut --edges.join --osm-files {self.osm} -o {temp_network_loc}'
            elif self.netconvert_highway_op.isChecked():
                cmd = f'{self.SUMO_exec}./netconvert -W --osm-files {self.osm} -o {temp_network_loc}'
            else:
                cmd = f'{self.SUMO_exec}./netconvert -W --no-turnarounds.tls --no-turnarounds --remove-edges.isolated --show-errors.connections-first-try --keep-edges.by-vclass passenger --ramps.guess --rectangular-lane-cut --edges.join --osm-files {self.osm} -o {temp_network_loc}'

            cmd = f'{self.SUMO_exec}./netconvert -W --opposites.guess.fix-lengths --no-left-connections --check-lane-foes.all --junctions.join-turns --junctions.join --roundabouts.guess --no-turnarounds.tls --no-turnarounds --plain.extend-edge-shape --remove-edges.isolated --show-errors.connections-first-try --keep-edges.by-vclass passenger --ramps.guess --rectangular-lane-cut --edges.join --osm-files {self.osm} -o {temp_network_loc}'
            # convert to list for subprocess popoen
            cmd_list = cmd.split(' ')

            try:
                subprocess.Popen(cmd_list)
                self.network = temp_network_loc
                self.check_netconvert_file.setChecked(True)
                self.cmd_str.setPlainText(f'SUMO Network file successfully generated: {cmd}')
                QMessageBox.information(self, 'Ok', 'SUMO Network file successfully generated')
            except Exception as e:
                self.cmd_str.setPlainText(str(e))
                QMessageBox.information(self, 'Error', 'SUMO netconvert tool cannot be executed. See console logs.')
        else:
            QMessageBox.information(self, 'Missing File', 'OSM file is missing')


    def evt_netconvert_highway_op(self):
        if self.netconvert_highway_op.checkState():self.netconvert_urban_op.setDisabled(True)
        else:self.netconvert_urban_op.setDisabled(False)

    def evt_netconvert_urban_op(self):
        if self.netconvert_urban_op.checkState(): self.netconvert_highway_op.setDisabled(True)
        else:self.netconvert_highway_op.setDisabled(False)

    ############################    DEFINE TRAFFIC DEMAND EVENTS    ################################
    def evt_tripinfo_clicked(self, value):
        self.sumo_var_tripinfo = value

    def evt_emissions_clicked(self, value):
        self.sumo_var_emissions = value

    def evt_summary_clicked(self, value):
        self.sumo_var_summary = value

    def evt_simtime_int_btn_clicked(self, value):
        self.simtime = value

    def evt_sumo_rerouting_prob_spin_clicked(self, value):
        self.reroute_probability = value

    def evt_rt_file_btn_clicked(self):
        # input of the path to the traffic file .csv
        fpath, extension = QFileDialog.getOpenFileName(self, 'Open File', '/',
                                                       'CSV (*.csv)')
        self.realtraffic = fpath

    def evt_taz_file_btn_clicked(self):
        # input one file
        fpath, extension = QFileDialog.getOpenFileName(self,'Open File', '/Users/Pablo/','JPG Files (*.jpg);; PNG Files (*.png)')
        self.taz_file = fpath

    def evt_output_file_clicked(self):
        # save new file
        fpath = QFileDialog.getExistingDirectory(self, 'Save File', '/Users/Pablo/')
        self.outputs = fpath

    def evt_gen_btn_clicked(self):
        # Find sumo installation
        self.Update_SUMO_exec_path()
        # Update Selected tool
        self.tool = self.get_selected_tool_str()
        self.O_district = self.O_distric.toPlainText()
        self.D_district = self.D_distric.toPlainText()

        # check for input files and general settings
        list_inputs = [self.realtraffic, self.trips, self.O_distric.toPlainText(), self.D_distric.toPlainText()]
        inputs_index = ['Traffic', 'Output', 'O-Distric', 'D-distric']
        inputs_type = ['File', 'File', 'NAME', 'NAME']

        empty_inputs = True
        while empty_inputs:
            for index, input in enumerate(list_inputs):
                if input == '':
                    warn_empty = QMessageBox.information(self, 'Missing File', f'Please select a valid {inputs_index[index]}'
                                                                       f' {inputs_type[index]}')
                    break
            empty_inputs = False
        # Routing selector
        if self.tab_selector.currentIndex() == 0:
            self.update_paths()
            rt(self, 0, 1, False)


    def setuplayout(self):
        #####################  LAYOUT #########################3
        self.tab_main_layout = QHBoxLayout()
        self.tab_main_layout.addWidget(self.tab_main_menu)
        #####################  TABS OF THE MAIN MENU #########################3
        self.tab_main_menu.addTab(self.wdg_build_network, "Build Network")
        self.tab_main_menu.addTab(self.wdg_MA, "Traffic Demand")
        self.tab_main_menu.addTab(self.wdg_DUA, "Simulation")
        self.tab_main_menu.addTab(self.wdg_DUA, "Outputs")
        ##################   BUILD NETWORK SUB LAYOUTS      #####################3
        self.osm_sublayout = QHBoxLayout()
        self.osm_sublayout.addWidget(self.osm_file_btn)
        self.osm_sublayout.addWidget(self.check_osm_file)
        self.osm_sublayout.setAlignment(Qt.AlignRight)
        self.osm_groupbox.setLayout(self.osm_sublayout)

        self.netconvert_sublayout = QHBoxLayout()
        self.netconvert_sublayout.addWidget(self.netconvert_btn)
        self.netconvert_sublayout.addWidget(self.check_netconvert_file)
        self.netconvert_sublayout.setAlignment(Qt.AlignRight)

        self.netconvert_options_sublayout = QVBoxLayout()
        self.netconvert_options_sublayout.addWidget(self.netconvert_urban_op)
        self.netconvert_options_sublayout.addWidget(self.netconvert_highway_op)

        self.netconvert_main_layout = QHBoxLayout()
        self.netconvert_main_layout.addLayout(self.netconvert_options_sublayout)
        self.netconvert_main_layout.addLayout(self.netconvert_sublayout)
        self.netconvert_groupbox.setLayout(self.netconvert_main_layout)

        self.polyconvert_sublayout = QHBoxLayout()
        self.polyconvert_sublayout.addWidget(self.polyconvert_btn)
        self.polyconvert_sublayout.addWidget(self.check_polyconvert_file)
        self.polyconvert_sublayout.setAlignment(Qt.AlignRight)
        self.polyconvert_groupbox.setLayout(self.polyconvert_sublayout)
        ##################   BUILD TRAFFIC DEMAND SUB LAYOUTS    #####################3




        ##################   CONTAINER BUILD NETWORK    #####################3
        self.container_build_network = QFormLayout()
        self.container_build_network.addRow(self.osm_groupbox)
        self.container_build_network.addRow(self.netconvert_groupbox)
        self.container_build_network.addRow(self.polyconvert_groupbox)
        self.container_build_network.addRow(self.cmd_str) # log text
        self.wdg_build_network.setLayout(self.container_build_network)
        ######################################################################








        """
        self.lyvertical = QVBoxLayout()
        self.ly_settings = QHBoxLayout()

        self.lysumooptions = QHBoxLayout()

        # CREATE LAYOUT - ORDER IMPORTANT
        self.lyvertical.addWidget(self.title_label)
        self.lyvertical.addWidget(self.tab_selector)
        self.lyvertical.addWidget(self.progress_bar)
        self.lyvertical.addWidget(self.gen_btn)

        self.lymainlayer.addLayout(self.lyvertical)
        self.lymainlayer.addWidget(self.tab_main)

        self.ly_settings.addWidget(self.simtime_int_btn)
        self.ly_settings.addWidget(self.rt_file_btn)
        # add tab
        self.tab_main.addTab(self.wdg_inputs, 'Inputs')
        self.tab_main.addTab(self.wdg_outputs, 'Outputs')

        # add  sumo options to layout
        self.lysumooptions.addWidget(self.sumo_output_tripinfo)
        self.lysumooptions.addWidget(self.sumo_output_emissions)
        self.lysumooptions.addWidget(self.sumo_output_summary)
        self.lysumooptions.addWidget(self.sumo_rerouting_prob_spin)
        self.sumo_groupbox.setLayout(self.lysumooptions)

        ###################  TAB INPUT / OUTPUT CONTAINERS ##################
        self.ly_input_TAB = QFormLayout()
        self.ly_input_TAB.setAlignment(Qt.AlignRight)
        self.ly_input_TAB.addRow('Time[h]',self.ly_settings)
        #self.ly_input_TAB.addRow('Time [h]', self.simtime_int_btn)
        self.ly_input_TAB.addRow('O-District', self.O_distric)
        self.ly_input_TAB.addRow('D-District', self.D_distric)
        self.ly_input_TAB.setRowWrapPolicy(QFormLayout.DontWrapRows)
        self.wdg_inputs.setLayout(self.ly_input_TAB)


        self.ly_output_TAB = QFormLayout()
        self.ly_output_TAB.addRow('', self.outputFile_btn)
        self.wdg_outputs.setLayout(self.ly_output_TAB)

        ################### SELECTOR CONTAINERS ##################
        self.ly_RT = QFormLayout()

        self.ly_RT.addRow(self.RT_description)
        self.ly_RT.addRow(self.sumo_groupbox)
        self.wdg_RT.setLayout(self.ly_RT)

        # setup MA
        self.ly_MA = QFormLayout()
        self.ly_MA.addRow(self.MA_description)
        self.wdg_MA.setLayout(self.ly_MA)

        # setup RT
        self.ly_DUA = QFormLayout()
        self.ly_DUA.addRow(self.DUA_description)
        self.wdg_DUA.setLayout(self.ly_DUA)

        # setup RT
        self.ly_DUAI = QFormLayout()
        self.ly_DUAI.addRow(self.DUAI_description)
        self.wdg_DUAI.setLayout(self.ly_DUAI)

        # setup RT
        self.ly_OD2 = QFormLayout()
        self.ly_OD2.addRow(self.OD2_description)
        self.wdg_OD2.setLayout(self.ly_OD2)

        ##################### Add container widgets to the TAB SELECTOR ###################
        self.tab_selector.addTab(self.wdg_RT, "Random")
        self.tab_selector.addTab(self.wdg_MA, "MARouter")
        self.tab_selector.addTab(self.wdg_DUA, "DUARouter")
        self.tab_selector.addTab(self.wdg_DUAI, "DUAIterate")
        self.tab_selector.addTab(self.wdg_OD2, "OD2Trips")

        """
        # Match with main layout
        self.setLayout(self.tab_main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)  # create applications
    dlgMain = DlgMain()  # create main GUI canvas
    dlgMain.show()  # Show gui console
    sys.exit(app.exec_())

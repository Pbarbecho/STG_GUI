import multiprocessing
import os, sys, time
from PyQt5.QtWidgets import *  # import sections
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from randomTrips import rt
from utils import create_folder

#import subprocess


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

        # ventana principal
        self.setWindowTitle("STG")
        self.resize(1000, 500)

        ####################### CREATE LABELS ######################
        # TITLES FONTS
        title_font = QFont("Times New Roman", 20, 75, False)
        subtitle_font = QFont("Times New Roman", 15, 70, False)
        # MAIN LABEL
        self.title_label = QLabel('SUMO Traffic Generation')
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)
        # requirements label
        self.requirements_label = QLabel('Requirements:')
        ################ PROGRESS BAR ######################
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyle(QStyleFactory.create('Windows'))
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        # User text inputs
        self.O_distric = QPlainTextEdit()
        self.O_distric.setPlaceholderText('Enter the Origin District NAME as in the TAZ file')
        self.D_distric = QPlainTextEdit()
        self.D_distric.setPlaceholderText('Enter the Destination District NAME as in the TAZ file')

        ########################################   TEXT BOX  ############################


         ####################################################################################

        # Text description of sumo tools
        self.RT_description = QTextEdit()
        self.MA_description = QTextEdit()
        self.DUA_description = QTextEdit()
        self.DUAI_description = QTextEdit()
        self.OD2_description = QTextEdit()

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

        ####################### CREATE BUTTONS ######################
        # check box for routing options
        self.sumo_groupbox = QGroupBox('SUMO Outputs')
        self.sumo_groupbox.setFont(subtitle_font)
        self.sumo_output_tripinfo = QCheckBox('Tripinfo')
        self.sumo_output_emissions = QCheckBox('Emissions')
        self.sumo_output_summary = QCheckBox('Summary')
        self.sumo_output_tripinfo.toggled.connect(self.evt_tripinfo_clicked)
        self.sumo_output_emissions.toggled.connect(self.evt_emissions_clicked)
        self.sumo_output_summary.toggled.connect(self.evt_summary_clicked)

        self.sumo_rerouting_prob_spin = QSpinBox()
        self.sumo_rerouting_prob_spin.setWrapping(True)
        self.sumo_rerouting_prob_spin.setRange(0, 100)
        self.sumo_rerouting_prob_spin.setValue(0)
        self.sumo_rerouting_prob_spin.setSingleStep(10)
        self.sumo_rerouting_prob_spin.valueChanged.connect(self.evt_sumo_rerouting_prob_spin_clicked)

        # Input button open File
        self.simtime_int_btn = QSpinBox()
        self.simtime_int_btn.setWrapping(True)
        self.simtime_int_btn.setRange(1,24)
        self.simtime_int_btn.setValue(1)
        self.simtime_int_btn.setSingleStep(1)
        self.simtime_int_btn.valueChanged.connect(self.evt_simtime_int_btn_clicked)

        # ORIGIN TAZ button open File
        self.taz_file_btn = QPushButton('TAZ File')
        self.taz_file_btn.clicked.connect(self.evt_taz_file_btn_clicked)

        # Real traffic button open File
        self.rt_file_btn = QPushButton('Traffic File')
        self.rt_file_btn.clicked.connect(self.evt_rt_file_btn_clicked)

        # Output button save File
        self.outputFile_btn = QPushButton('Output')
        self.outputFile_btn.clicked.connect(self.evt_output_file_clicked)

        # generate simulation button
        self.gen_btn = QPushButton('Generate', self)
        self.gen_btn.clicked.connect(self.evt_gen_btn_clicked)
        #################  NEW BUTTONS  ################################
        # WebWizard map
        self.WebWizard_btn = QPushButton('OSM WebWizard')
        self.WebWizard_btn.clicked.connect(self.WebWizard_btn_clicked)

        # Netconvert button
        self.netconvert_btn = QPushButton('Netconvert')
        self.netconvert_btn.clicked.connect(self.netconvert_btn_clicked)

        # Polyconvert
        self.polyconvert_btn = QPushButton('Polyconvert')
        self.polyconvert_btn.clicked.connect(self.polyconvert_btn_clicked)

         #################   GROUP BOXES  NETWORK BUILD  ##############################
        self.webwizard_groupbox = QGroupBox('1. Select MAP from OpenStreetMaps (.osm)')
        self.netconvert_groupbox = QGroupBox('2. Generate SUMO map (.net.xml)')
        self.polyconvert_groupbox = QGroupBox('3. Generate polygons of the map (.poly.xml)')
        self.webwizard_groupbox.setFont(subtitle_font)
        self.netconvert_groupbox.setFont(subtitle_font)
        self.polyconvert_groupbox.setFont(subtitle_font)
        #########################################################################




        # INSTANCIATE  TAB WIDGET

        # MAIN TAB
        self.tab_main_menu = QTabWidget()

        self.tab_selector = QTabWidget()
        self.tab_main = QTabWidget()

        # INSTANCIATE widgets for each radio option
        self.wdg_RT = QWidget()
        self.wdg_MA = QWidget()
        self.wdg_DUA = QWidget()
        self.wdg_DUAI = QWidget()
        self.wdg_OD2 = QWidget()

        self.wdg_build_network = QWidget()
        self.wdg_webwizard = QWidget()
        self.wdg_traffic_demand = QWidget()
        self.wdg_simulation = QWidget()

        #create widgets for tabs
        self.wdg_inputs = QWidget()
        self.wdg_outputs = QWidget()

        self.setuplayout()

    def Update_SUMO_exec_path(self):
        if self.SUMO_exec == '':
            warn_empty = QMessageBox.information(self, 'Missing File', 'Please set SUMO_HOME variable in your system.')
            # sys.exit('SUMO_HOME environment variable is not found.')
        else:
            # Update SUMO bin path
            if os.path.basename(self.SUMO_exec) != 'bin': self.SUMO_exec = os.path.join(self.SUMO_exec, 'bin')


    #################  DEFINE EVENTS ###############################
    def WebWizard_btn_clicked(self):
        path_str, state = QInputDialog.getText(self, 'Save OSM file', 'Enter path to save OSM file')
        if state:
            # path exist
            if os.path.exists(path_str):
                #update sumo path
                self.Update_SUMO_exec_path()
                # save path to osm file
                self.osm = path_str
                # WebWizard exec  python /opt/sumo-1.5.0/tools/osmWebWizard.py
                webwizard_path = os.path.join(self.SUMO_exec, '..', 'tools/osmWebWizard.py')
                os.system(f'python {webwizard_path}')


            else:
                QMessageBox.information(self, 'Information', 'Path is not valid')


    def netconvert_btn_clicked(self):
        print('netconvet')
    def polyconvert_btn_clicked(self):
        print('polyconvert')












    #########################################################################
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


    def evt_gen_btn_clicked(self):
        # Find sumo installation
        SUMO = os.environ['SUMO_HOME']
        if SUMO == '':
            warn_empty = QMessageBox.information(self, 'Missing File', 'Please set SUMO_HOME variable in your system.')
            sys.exit('SUMO_HOME environment variable is not found.')
        else:
            self.SUMO_exec = f'{SUMO}/bin/'

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

        """
        for x in range(100):
            print(x)
            time.sleep(0.1)
            self.progress_bar.setValue(x)
            app.processEvents()
        """



    def setuplayout(self):

        #####################  LAYOUT #########################3
        self.tab_main_layout = QHBoxLayout()
        self.tab_main_layout.addWidget(self.tab_main_menu)


        #####################  TABS OF THE MAIN MENU #########################3
        self.tab_main_menu.addTab(self.wdg_build_network, "Build Network")
        self.tab_main_menu.addTab(self.wdg_MA, "Traffic Demand")
        self.tab_main_menu.addTab(self.wdg_DUA, "Simulation")

        ##################   BUILD NETWORK SUB LAYOUTS      #####################3

        self.webwizard_sublayout = QHBoxLayout()
        self.webwizard_sublayout.addWidget(self.WebWizard_btn)
        self.webwizard_groupbox.setLayout(self.webwizard_sublayout)

        self.netconvert_sublayout = QHBoxLayout()
        self.netconvert_sublayout.addWidget(self.netconvert_btn)
        self.netconvert_groupbox.setLayout(self.netconvert_sublayout)

        self.polyconvert_sublayout = QHBoxLayout()
        self.polyconvert_sublayout.addWidget(self.polyconvert_btn)
        self.polyconvert_groupbox.setLayout(self.polyconvert_sublayout)


        ##################   CONTAINERS    #####################3
        self.container_build_network = QFormLayout()
        self.container_build_network.addRow(self.webwizard_groupbox)
        self.container_build_network.addRow(self.netconvert_groupbox)
        self.container_build_network.addRow(self.polyconvert_groupbox)
        self.wdg_build_network.setLayout(self.container_build_network)
        ####################################################3

        #self.webwizard_path = self.webwizard_dir.toPlainText()






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

import multiprocessing
import os, sys
from PyQt5.QtWidgets import *  # import sections
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from randomTrips import rt
from duarouter import dua_ma
from utils import create_folder, SUMO_outputs_process, exec_sim_cmd
from statistics import statistics_route_file
import subprocess


class MyThread(QThread):
    change_value = pyqtSignal(str)
    def run(self):
        self.change_value.emit('Done')


class DlgMain(QDialog):
    def __init__(self):
        super().__init__()

        # initial configurations
        self.isCommandExecutionSuccessful = False
        self.realtraffic = ''
        self.simtime = 1
        self.repetitions = 1
        self.taz_file = ''
        self.O_district = ''
        self.D_district = ''
        self.processors = multiprocessing.cpu_count()
        self.SUMO_exec = os.environ['SUMO_HOME']
        #self.SUMO_exec = '/opt/sumo-1.5.0/bin/'
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
        self.sumo_var_tripinfo = True
        self.sumo_var_emissions = False
        self.sumo_var_summary = False
        self.sumo_var_gui = False
        self.routing = ''
        self.osm = ''
        self.network = ''
        self.poly = ''
        self.rou_file = ''

        # ventana principal
        self.setWindowTitle("SUMO-based Traffic Generation Tool (STGT)")
        self.resize(600, 300)


        ###################  TEST PROGRESS BAR  ####################3

        self.progress_bar = QProgressBar()
        self.progress_bar.setStyle(QStyleFactory.create('Windows'))
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        ####################### CREATE LABELS ########################
        # TITLES FONTS
        title_font = QFont("Times New Roman", 20, 75, False)
        subtitle_font = QFont("Times New Roman", 15, 15, False)
        traffic_setting_label = QFont("Times New Roman", 15, 15, False)
        # MAIN LABEL
        self.title_label = QLabel('SUMO Traffic Generation')
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)


        ####################### User text inputs districts ##################################
        od_max_width = 200
        od_max_high = 40
        self.O_distric_label = QLabel('Origin TAZ')

        self.O_distric = QPlainTextEdit()

        self.O_distric.setPlaceholderText('Enter the Origin District NAME as in the TAZ file')
        self.O_distric.setMaximumSize(od_max_width, od_max_high)
        self.D_distric_label = QLabel('Destination TAZ')
        self.D_distric = QPlainTextEdit()
        self.D_distric.setMaximumSize(od_max_width, od_max_high)
        self.D_distric.setPlaceholderText('Enter the Destination District NAME as in the TAZ file')

        #######################  BUILD NETWORK LOG TEXT BOX  ################################
        self.cmd_str = QTextEdit()
        self.cmd_str.setPlaceholderText('Console logs')
        self.cmd_str.setReadOnly(True)

        self.traffic_demand_cmd =QTextEdit()
        self.traffic_demand_cmd.setPlaceholderText('Console logs')
        self.traffic_demand_cmd.setReadOnly(True)
        ######################  Text box  description of sumo tools     #####################
        self.RT_description = QTextEdit()
        self.MA_description = QTextEdit()
        self.DUA_description = QTextEdit()
        self.DUAI_description = QTextEdit()
        self.OD2_description = QTextEdit()

        #########
        # TO DO FALTA CREAR TEXTO HTML CON  LA DESCRIPCION DE CADA HERRAMIENTA
        html_RT = """
        < a > This tool allows researchers to quickly generate a set of random trips within a time interval. The RT tool prevents bottlenecks in the network. It uses an incremental traffic assignment method where the vehicle computes its route at the departure considering current conditions along the network. < / a >
        <p style=”text-align: justify;”>
        """

        html_MA = """
            < a > The MARouter tool is able to compute a microscopic (flows) or macroscopic user assignment.  The MAR generates a list of vehicle flows (i.e., microscopic), including the route distributions meaning that each route includes the probability to be selected. Here, the traffic assignation method employs resistive functions that approximate the travel time increment when the number of vehicles in the flow increases. < / a >
            """

        html_DUA = """
            < a > This tool computes vehicle routes that may be used by sumo using shortest path computation. It uses an empty-network traffic assignment method where each vehicle computes its route under the assumption that it is alone in the network. This behavior generates traffic congestions due to the sheer amount of traffic. < / a >
            """

        html_DUAI = """
            < a > This tool uses an assignment method called iterative, which tries to calculate the user equilibrium, meaning that it generate a route for each vehicle where the route cost (e.g., travel time) cannot be reduced by using an alternative route. This is done by iteratively calling the DUAR tool. < / a >
            """

        html_OD2 = """
            < a >  To allocate the traffic demand in the network, OD2 uses an incremental assignment method. Vehicles will calculate fastest paths according to their time of departure considering a traffic-loaded network. In this way, the incremental assignment prevents all vehicles from choosing the same route (i.e., prevents congested routes). By default, vehicles are uniformly distributed within the time interval coded in O/D matrices. < / a >
            """

        self.RT_description.setText(html_RT)
        self.RT_description.setReadOnly(True)
        self.MA_description.setText(html_MA)
        self.MA_description.setReadOnly(True)
        self.DUA_description.setText(html_DUA)
        self.DUA_description.setReadOnly(True)
        self.DUAI_description.setText(html_DUAI)
        self.DUAI_description.setReadOnly(True)
        self.OD2_description.setText(html_OD2)
        self.OD2_description.setReadOnly(True)

        #'The DUAIterate uses an assignment method called iter-ative, see Table 1, which tries to calculate the user equilibrium,meaning that it generate a route for each vehicle where the routecost (e.g., travel time) cannot be reduced by using an alterna-tive route.  This is done by iteratively calling the DUAR tool'
        #'The DUAR tool imports differ-ent demand definitions (trips or flows).'
        #('This tool allows researchers to quicklygenerate a set of random trips within a time interval. The RT tool prevents bottlenecksin the network. ')
        #'Generates random distribuition of vehicles'

        ##########################  SIMULATION BUTTONS    ################################

        self.sumo_simulation_label = QLabel('  Outputs:')
        self.sumo_simulation_label.setAlignment(Qt.AlignLeft)
        self.sumo_simulation_label.setFont(subtitle_font)

        self.cmd_output_str = QTextEdit()
        self.cmd_output_str.setPlaceholderText('Outputs')
        self.cmd_output_str.setReadOnly(True)

        self.run_simulation_btn = QPushButton('Run Simulation')
        self.run_simulation_btn.setMinimumWidth(120)
        self.run_simulation_btn.clicked.connect(self.evt_run_simulation_btn_clicked)

        self.process_outputs_simulation_btn = QPushButton('Process simulation outputs (.xml to .csv)')
        self.process_outputs_simulation_btn.setMinimumWidth(120)
        self.process_outputs_simulation_btn.clicked.connect(self.evt_process_outputs_simulation_btn_clicked)

        ##########################  TRAFFIC DEMAND BUTTONS    ################################
        tool_btn_wsize = 120
        # osm file
        self.osm_file_btn = QPushButton('OSM File')
        self.osm_file_btn.setMinimumWidth(tool_btn_wsize)
        self.osm_file_btn.clicked.connect(self.evt_osm_file_btn_clicked)

        # Netconvert button
        self.netconvert_btn = QPushButton('Netconvert')
        self.netconvert_btn.setMinimumWidth(tool_btn_wsize)
        #self.netconvert_btn.clicked.connect(self.evt_netconvert_btn_clicked)
        self.netconvert_btn.clicked.connect(self.start_progress_bar)


        # Polyconvert
        self.polyconvert_btn = QPushButton('Polyconvert')
        self.polyconvert_btn.setMinimumWidth(tool_btn_wsize)
        self.polyconvert_btn.clicked.connect(self.evt_polyconvert_btn_clicked)
        
        # Netedit 
        self.run_netedit_btn = QPushButton('Netedit')
        self.run_netedit_btn.setMaximumWidth(tool_btn_wsize)
        self.run_netedit_btn.clicked.connect(self.evt_netedit_btn_clicked)


        # Check boxes
        self.check_osm_file = QCheckBox()
        self.check_netconvert_file = QCheckBox()
        self.check_polyconvert_file = QCheckBox()
        self.check_netedit_file = QCheckBox()


        self.check_osm_file.setEnabled(False)
        self.check_netconvert_file.setEnabled(False)
        self.check_polyconvert_file.setEnabled(False)
        self.check_netedit_file.setEnabled(False)

        # Check boxes STATISTICS
        self.check_rou_file = QCheckBox()
        self.check_summary_file = QCheckBox()
        self.check_tripinfo_file = QCheckBox()
        self.check_emissions_file = QCheckBox()
        self.check_rou_file.setEnabled(False)
        self.check_summary_file.setEnabled(False)
        self.check_tripinfo_file.setEnabled(False)
        self.check_emissions_file.setEnabled(False)

        # check box for netconvert
        self.netconvert_options_groupbox = QGroupBox()

        self.netconvert_urban_op = QCheckBox('Urban')
        self.netconvert_urban_op.setChecked(True)

        self.netconvert_highway_op = QCheckBox('Highway')
        self.netconvert_highway_op.setEnabled(False)

        self.netconvert_urban_op.toggled.connect(self.evt_netconvert_urban_op)
        self.netconvert_highway_op.toggled.connect(self.evt_netconvert_highway_op)

        self.label_netedit = QLabel('Create traffic assigment zone (TAZ)')
        self.label_netedit.setAlignment(Qt.AlignLeft)
        self.label_netedit.setFont(subtitle_font)

        #   GROUP BOXES  NETWORK BUILD
        self.osm_groupbox = QGroupBox('1. Select OpenStreetMaps file (.osm)')
        self.netconvert_groupbox = QGroupBox('2. Generate SUMO network file (.net.xml)')
        self.polyconvert_groupbox = QGroupBox('3. Generate polygons of the map (.poly.xml)')
        self.taz_groupbox = QGroupBox('4. Optional:')


        self.osm_groupbox.setFont(subtitle_font)
        self.netconvert_groupbox.setFont(subtitle_font)
        self.polyconvert_groupbox.setFont(subtitle_font)
        self.taz_groupbox.setFont(subtitle_font)

        #####################    GROUP BOXES  TRAFFIC DEMAND   ##################

        self.simulation_groupbox = QGroupBox()
        self.simulation_groupbox.setFont(subtitle_font)

        self.traffic_setting_groupbox = QGroupBox()
        self.traffic_setting_groupbox.setFont(subtitle_font)
        self.realtraffic_groupbox = QGroupBox()
        self.realtraffic_groupbox.setFont(subtitle_font)
        self.rt_groupbox = QGroupBox()
        self.rt_groupbox.setFont(subtitle_font)
        self.ma_groupbox = QGroupBox()
        self.ma_groupbox.setFont(subtitle_font)
        self.dua_groupbox = QGroupBox()
        self.dua_groupbox.setFont(subtitle_font)
        self.duai_groupbox = QGroupBox()
        self.duai_groupbox.setFont(subtitle_font)
        self.od2_groupbox = QGroupBox()
        self.od2_groupbox.setFont(subtitle_font)

        #######################    STATISTICS BUTTONS   ############################
        self.statistics_groupbox = QGroupBox()
        self.statistics_groupbox.setFont(subtitle_font)

        self.label_rou_file = QLabel('Enter .rou file')
        self.label_rou_file.setAlignment(Qt.AlignLeft)
        self.label_rou_file.setFont(subtitle_font)

        self.read_route_file_btn = QPushButton('Rou (.rou.xml)')
        self.read_route_file_btn.clicked.connect(self.evt_read_route_file_btn_clicked)

        self.read_summary_file_btn = QPushButton('Summary (.sum.xml)')
        self.read_summary_file_btn.clicked.connect(self.evt_read_summary_file_btn_clicked)

        self.read_tripinfo_file_btn = QPushButton('TripInfo (.trip.xml)')
        self.read_tripinfo_file_btn.clicked.connect(self.evt_read_tripinfo_file_btn_clicked)

        self.read_emissions_file_btn = QPushButton('Emissions (.emi.xml)')
        self.read_emissions_file_btn.clicked.connect(self.evt_read_emissions_file_btn_clicked)

        #######################    BUILD TRAFFIC BUTTONS   ############################
        # check box for sumo outputs
        self.sumo_groupbox = QGroupBox('SUMO Outputs')
        self.sumo_groupbox.setFont(subtitle_font)
        self.sumo_output_tripinfo = QCheckBox('Tripinfo')
        self.sumo_output_tripinfo.setChecked(True)
        self.sumo_output_emissions = QCheckBox('Emissions')
        self.sumo_output_emissions.setChecked(True)
        self.sumo_output_summary = QCheckBox('Summary')
        self.sumo_output_summary.setChecked(True)
        self.sumo_gui = QCheckBox('GUI')
        self.sumo_gui.toggled.connect(self.evt_sumo_gui_clicked)
        self.sumo_output_tripinfo.toggled.connect(self.evt_tripinfo_clicked)
        self.sumo_output_emissions.toggled.connect(self.evt_emissions_clicked)
        self.sumo_output_summary.toggled.connect(self.evt_summary_clicked)
        # spinbox for reroute probability
        self.sumo_rerouting_prob_spin = QSpinBox()
        self.sumo_rerouting_prob_spin.setWrapping(True)
        self.sumo_rerouting_prob_spin.setRange(0, 100)
        self.sumo_rerouting_prob_spin.setValue(50)
        self.sumo_rerouting_prob_spin.setSingleStep(10)
        self.sumo_rerouting_prob_spin.setMaximumSize(95, 30)
        self.sumo_rerouting_prob_spin.setAlignment(Qt.AlignRight)
        self.sumo_rerouting_prob_spin.valueChanged.connect(self.evt_sumo_rerouting_prob_spin_clicked)

        self.sumo_rerouting_prob_label = QLabel('Reroute Probability')
        self.sumo_rerouting_prob_label.setAlignment(Qt.AlignRight)
        self.sumo_rerouting_prob_label.setFont(traffic_setting_label)

        # spinbox for number of simulation hours
        self.simtime_int_btn = QSpinBox()
        self.simtime_int_btn.setWrapping(True)
        self.simtime_int_btn.setRange(1, 24)
        self.simtime_int_btn.setValue(1)
        self.simtime_int_btn.setSingleStep(1)
        self.simtime_int_btn.setAlignment(Qt.AlignRight)
        self.simtime_int_btn.setFont(traffic_setting_label)
        self.simtime_int_btn.setMaximumSize(95, 30)
        self.simtime_int_btn.valueChanged.connect(self.evt_simtime_int_btn_clicked)

        # READ ORIGIN TAZ button open File
        self.taz_file_btn = QPushButton('TAZ File')
        self.taz_file_btn.clicked.connect(self.evt_taz_file_btn_clicked)

        # TRQAFFIC SETTINGS
        self.label_rt_file_btn = QLabel('Traffic (*.csv)')
        self.label_rt_file_btn.setAlignment(Qt.AlignRight)
        self.label_rt_file_btn.setFont(traffic_setting_label)

        self.label_simtime_btn = QLabel('Simulation Time [h]')
        self.label_simtime_btn.setAlignment(Qt.AlignRight)
        self.label_simtime_btn.setFont(traffic_setting_label)

        # READ real traffic button open File
        self.rt_file_btn = QPushButton('Load file')
        self.rt_file_btn.setMaximumWidth(130)
        self.rt_file_btn.clicked.connect(self.evt_rt_file_btn_clicked)

        # Output button save File
        self.outputFile_btn = QPushButton('Output')
        self.outputFile_btn.clicked.connect(self.evt_output_file_clicked)

        # update configuration file
        self.update_cfg_btn = QPushButton('Upload Configuration File')
        self.update_cfg_btn.clicked.connect(self.evt_update_cfg_btn_clicked)

        #################### TRAFFIC DEMAND BUTTONS ##########################
        # RT button
        wsize = 120
        self.rt_btn = QPushButton('RandomTrips')
        self.rt_btn.setMinimumWidth(wsize)
        self.rt_btn.clicked.connect(self.evt_rt_btn_clicked)

        # MA button
        self.ma_btn = QPushButton('MARouter')
        self.ma_btn.setMinimumWidth(wsize)
        self.ma_btn.clicked.connect(self.evt_ma_btn_clicked)

        # DUA button
        self.dua_btn = QPushButton('DUARouter')
        self.dua_btn.setMinimumWidth(wsize)
        self.dua_btn.clicked.connect(self.evt_dua_btn_clicked)

        # DUAI button
        self.duai_btn = QPushButton('DUAIterate')
        self.duai_btn.setMinimumWidth(wsize)
        self.duai_btn.clicked.connect(self.evt_duai_btn_clicked)

        # OD2 button
        self.od2_btn = QPushButton('OD2Trips')
        self.od2_btn.setMinimumWidth(wsize)
        self.od2_btn.clicked.connect(self.evt_od2_btn_clicked)

        ########################     INSTANCIATE  TAB TRAFFIC DEMAND ROUTING  #############################
        self.tab_routing_op = QTabWidget()


        ########################     INSTANCIATE  TAB WIDGET  #############################
        self.tab_main_menu = QTabWidget()
        self.tab_main = QTabWidget()
        self.tab_selector = QTabWidget()

        # INSTANCIATE widgets for each TAB option
        self.wdg_build_network = QWidget()
        self.wdg_traffic_demand = QWidget()
        self.wdg_simulation = QWidget()
        self.wdg_statistics = QWidget()
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


    #################################   GENERAL FUNCTIONS ############################################
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

    ##############################  STRATISTICS  #############################################
    def evt_read_route_file_btn_clicked(self):
        fpath, extension = QFileDialog.getOpenFileName(self, 'Open File', '/Users/Pablo/',
                                                       'Routes File (*.rou.*)')
        if fpath:
            self.rou_file = fpath
            self.check_rou_file.setChecked(True)
            QMessageBox.information(self, 'Ok', 'Routes File imported')

    def evt_read_summary_file_btn_clicked(self):
        fpath, extension = QFileDialog.getOpenFileName(self, 'Open File', '/Users/Pablo/',
                                                       'Routes File (*.rou.*)')
        if fpath:
            self.rou_file = fpath
            self.check_rou_file.setChecked(True)
            QMessageBox.information(self, 'Ok', 'Routes File imported')

    def evt_read_tripinfo_file_btn_clicked(self):
        fpath, extension = QFileDialog.getOpenFileName(self, 'Open File', '/Users/Pablo/',
                                                       'Routes File (*.rou.*)')
        if fpath:
            self.rou_file = fpath
            self.check_rou_file.setChecked(True)
            QMessageBox.information(self, 'Ok', 'Routes File imported')

    def evt_read_emissions_file_btn_clicked(self):
        fpath, extension = QFileDialog.getOpenFileName(self, 'Open File', '/Users/Pablo/',
                                                       'Routes File (*.rou.*)')
        if fpath:
            self.rou_file = fpath
            self.check_rou_file.setChecked(True)
            QMessageBox.information(self, 'Ok', 'Routes File imported')

    ##############################  PROGRESS BAR #############################################


    def start_progress_bar(self):
        self.thread = MyThread()
        self.thread.change_value.connect(self.evt_netconvert_btn_clicked)
        self.thread.start()

    def progress_bar_update(self,val):
        self.progress_bar.setValue(val)


    ##############################  DEFINE SIMULATION  EVENTS #############################################
    def evt_process_outputs_simulation_btn_clicked(self):
        cfg_list = os.listdir(self.cfg)
        if len(cfg_list)>=1:
            try:
                SUMO_outputs_process(self)
                QMessageBox.information(self, 'Ok', f'Tripinfo files successfully converted to .csv files {self.parsed}')
            except Exception as e:
                self.cmd_output_str.setPlainText(str(e))
                QMessageBox.information(self, 'Error', 'Files cannot be parsed. See console logs.')
        else:
            QMessageBox.information(self, 'Error', 'No output files has been generated.')

    def evt_update_cfg_btn_clicked(self):
        cfg_list = os.listdir(self.cfg)
        if cfg_list:
            # parse an xml file by name


            cfg_file_path = os.path.join(self.cfg, cfg_list[0])
            qfile = QFile(cfg_file_path)

            qtstrem = QTextStream(qfile)

            self.cmd_output_str.setPlainText(qtstrem)
        else:
            QMessageBox.information(self, 'Error', 'SUMO configuration file is not generated yet.')

    def evt_run_simulation_btn_clicked(self):
        if self.outputs:
            simulations_list = os.listdir(self.cfg)
            if simulations_list:
                if QMessageBox.information(self, 'Ok', 'Simulation may take a few minutes. Proceed?'):
                    self.cmd_output_str.setPlainText(f'Simulating ...............')
                    try:
                        for s in simulations_list:
                            exec_sim_cmd(s, self, self.sumo_var_gui)
                        output_files = os.listdir(self.outputs)
                        self.cmd_output_str.setPlainText(f'Simulation compleated. Outputs in {self.outputs} \n \n {output_files}')
                        QMessageBox.information(self, 'Ok', 'Simulation compleate')
                    except Exception as e:
                        self.cmd_output_str.setPlainText(str(e))
                        QMessageBox.information(self, 'Error', 'SUMO netconvert tool cannot be executed. See console logs.')
            else:
                QMessageBox.information(self, 'Error', 'ty configurations folder.')
        else:
            QMessageBox.information(self, 'Error', 'Please generate Traffic Demand files.')

    ##############################  DEFINE TRAFFIC DEMAND EVENTS #############################################
    def evt_od2_btn_clicked(self):
        # Find sumo installation
        self.Update_SUMO_exec_path()
        # Update Selected tool
        self.tool = 'rt'
        # output default folder

        self.O_district = self.O_distric.toPlainText()
        self.D_district = self.D_distric.toPlainText()

        if self.O_district and self.D_district:
            if self.realtraffic:
                self.update_paths()
                rt(self, 0, 1, False)
            else:
                warn_empty = QMessageBox.information(self, 'Missing File', 'Please select a valid traffic file.')
        else:
            warn_empty = QMessageBox.information(self, 'Missing File',
                                                 'Please enter a valid Origin/Destination TAZ names.')

    def evt_rt_btn_clicked(self):

        # Find sumo installation
        self.Update_SUMO_exec_path()
        # Update Selected tool
        self.tool = 'rt'
        # output default folder

        self.O_distric.setDisabled(True)
        self.D_distric.setDisabled(True)

        self.O_distric.setPlainText('ro')
        self.D_distric.setPlainText('rd')

        self.O_district = self.O_distric.toPlainText()
        self.D_district = self.D_distric.toPlainText()

        if self.O_district and self.D_district:
            if self.realtraffic:
                self.update_paths()
                if QMessageBox.information(self, 'Generating Traffic Demand',
                                           'Traffic demand generation may take some time, please wait. Proceed?'):
                    self.traffic_demand_cmd.setPlainText('Generating Traffic demand files .........')

                    try:
                        rt(self, 0, False)
                        QMessageBox.information(self, 'Traffic Demand', 'Traffic demand successfully generated.')
                        trips_list = os.listdir(self.trips)
                        self.traffic_demand_cmd.setPlainText(f'Traffic demand files generated in {self.trips}: {trips_list}.')

                    except Exception as e:
                        self.traffic_demand_cmd.setPlainText(str(e))
                        QMessageBox.information(self, 'Error', 'Traffic demand not generated. See console logs.')

            else:warn_empty = QMessageBox.information(self, 'Missing File', 'Please select a valid traffic file.')
        else:warn_empty = QMessageBox.information(self, 'Missing File', 'Please enter a valid Origin/Destination TAZ names.')


    def evt_dua_btn_clicked(self):
        # Find sumo installation
        self.Update_SUMO_exec_path()
        # Update Selected tool
        self.tool = 'dua'
        # output default folder

        #DUARouter requires TAZ O/D names
        self.O_distric.setDisabled(False)
        self.D_distric.setDisabled(False)
        #self.O_distric.setPlainText('ro')
        #self.D_distric.setPlainText('rd')

        self.O_district = self.O_distric.toPlainText()
        self.D_district = self.D_distric.toPlainText()

        if self.O_district and self.D_district:
            if self.realtraffic:
                self.update_paths()
                if QMessageBox.information(self, 'Generating Traffic Demand',
                                           'Traffic demand generation may take some time, please wait. Proceed?'):
                    self.traffic_demand_cmd.setPlainText('Generating Traffic demand files .........')
                    try:
                        dua_ma(self, 0, False)
                        QMessageBox.information(self, 'Traffic Demand', 'Traffic demand successfully generated.')
                        #trips_list = os.listdir(self.trips)
                        #self.traffic_demand_cmd.setPlainText(
                        #    f'Traffic demand files generated in {self.trips}: {trips_list}.')

                    except Exception as e:
                        self.traffic_demand_cmd.setPlainText(str(e))
                        QMessageBox.information(self, 'Error', 'Traffic demand not generated. See console logs.')

            else:
                warn_empty = QMessageBox.information(self, 'Missing File', 'Please select a valid traffic file.')
        else:
            warn_empty = QMessageBox.information(self, 'Missing File',
                                                 'Please enter a valid Origin/Destination TAZ names.')

    def evt_duai_btn_clicked(self):
        # Find sumo installation
        self.Update_SUMO_exec_path()
        # Update Selected tool
        self.tool = 'rt'
        # output default folder

        self.O_district = self.O_distric.toPlainText()
        self.D_district = self.D_distric.toPlainText()

        if self.O_district and self.D_district:
            if self.realtraffic:
                self.update_paths()
                rt(self, 0, 1, False)
            else:
                warn_empty = QMessageBox.information(self, 'Missing File', 'Please select a valid traffic file.')
        else:
            warn_empty = QMessageBox.information(self, 'Missing File',
                                                 'Please enter a valid Origin/Destination TAZ names.')

    def evt_ma_btn_clicked(self):
        # Find sumo installation
        self.Update_SUMO_exec_path()
        # Update Selected tool
        self.tool = 'rt'
        # output default folder

        self.O_district = self.O_distric.toPlainText()
        self.D_district = self.D_distric.toPlainText()

        if self.O_district and self.D_district:
            if self.realtraffic:
                self.update_paths()
                rt(self, 0, False) # config, k , gui
            else:
                warn_empty = QMessageBox.information(self, 'Missing File', 'Please select a valid traffic file.')
        else:
            warn_empty = QMessageBox.information(self, 'Missing File',
                                                 'Please enter a valid Origin/Destination TAZ names.')

    #########################  DEFINE BUILD NETWORK  EVENTS #############################################

    def evt_osm_file_btn_clicked(self):
        fpath, extension = QFileDialog.getOpenFileName(self, 'Open File', '/Users/Pablo/',
                                                          'OSM File (*.osm)')
        if fpath:
            self.osm = fpath
            self.check_osm_file.setChecked(True)
            self.cmd_str.setPlainText(f'OSM file successfully imported from: {fpath}')
            QMessageBox.information(self, 'Ok', 'OSM File imported')

    def evt_netedit_btn_clicked(self):
        self.Update_SUMO_exec_path()
        #if self.network and self.poly:
        if self.network:
            tool_path = os.path.join(self.SUMO_exec,'netedit')
            map_dir = os.path.dirname(self.network)
            self.taz_file = os.path.join(map_dir, 'TAZ.xml')

            self.cmd_str.setPlainText(f'Network file : {self.network}\n')
            self.cmd_str.setPlainText(f'TAZ file : {self.taz_file}\n')

            #os.system(f'touch {self.taz_file}')
            cmd = f'netedit -a {self.poly} -s {self.network} --additionals-output {self.taz_file}'
            # convert to list for subprocess popoen
            cmd_list = cmd.split(' ')

            try:
                output = subprocess.check_output(cmd_list, stderr=subprocess.STDOUT, universal_newlines=True)
                # Print out command's standard output (elegant)
                self.isCommandExecutionSuccessful = True
                self.cmd_str.setPlainText(f'Execute SUMO netedit tool : {cmd}')
                self.check_polyconvert_file.setChecked(True)

            except subprocess.CalledProcessError as error:
                self.isCommandExecutionSuccessful = False
                errorMessage = ">>> Error while executing:\n" \
                               + cmd \
                               + "\n>>> Returned with error:\n" \
                               + str(error.output)
                self.cmd_str.setPlainText(errorMessage)
                QMessageBox.critical(None,"ERROR",errorMessage)
                print("Error: " + errorMessage)
        else:
            QMessageBox.information(self, 'Missing File', 'SUMO Network and Polygons files are required')


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

    def evt_netconvert_btn_clicked(self, val):
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
        self.cmd_str.setPlainText(f'{val}')

    def evt_netconvert_highway_op(self):
        if self.netconvert_highway_op.checkState():self.netconvert_urban_op.setDisabled(True)
        else:self.netconvert_urban_op.setDisabled(False)

    def evt_netconvert_urban_op(self):
        if self.netconvert_urban_op.checkState(): self.netconvert_highway_op.setDisabled(True)
        else:self.netconvert_highway_op.setDisabled(False)

    ############################    DEFINE TRAFFIC DEMAND BUTTON EVENTS    ################################
    def evt_sumo_gui_clicked(self, value):
        self.sumo_var_gui = value

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

    ############3#####################  LAYOUT ###################################
    def setuplayout(self):

        self.tab_main_layout = QVBoxLayout()
        #self.tab_main_layout.addWidget(self.title_label) # title SUMO TRaafi generator
        self.tab_main_layout.addWidget(self.tab_main_menu)

        #####################  TABS OF THE MAIN MENU #########################3
        self.tab_main_menu.addTab(self.wdg_build_network, "Build Network")
        self.tab_main_menu.addTab(self.wdg_traffic_demand, "Traffic Demand")
        self.tab_main_menu.addTab(self.wdg_simulation, "Simulation")
        self.tab_main_menu.addTab(self.wdg_statistics, "Statistics")
        #self.tab_main_menu.addTab(self.tab_groupbox, "Outputs")

        ##################   BUILD NETWORK SUB LAYOUTS      #####################3
        self.osm_sublayout = QHBoxLayout()
        self.osm_sublayout.addWidget(self.osm_file_btn)
        self.osm_sublayout.addWidget(self.check_osm_file)
        self.osm_sublayout.setAlignment(Qt.AlignRight)
        self.osm_groupbox.setLayout(self.osm_sublayout)

        self.netconvert_options_sublayout = QHBoxLayout()
        self.netconvert_options_sublayout.addWidget(self.netconvert_urban_op)
        self.netconvert_options_sublayout.addWidget(self.netconvert_highway_op)

        self.netconvert_sublayout = QHBoxLayout()
        self.netconvert_sublayout.addWidget(self.netconvert_btn)
        self.netconvert_sublayout.addWidget(self.check_netconvert_file)


        self.netconvert_main_layout = QHBoxLayout()
        self.netconvert_main_layout.addLayout(self.netconvert_options_sublayout, Qt.AlignLeft)
        self.netconvert_main_layout.addLayout(self.netconvert_sublayout)
        self.netconvert_main_layout.setAlignment(Qt.AlignRight)
        self.netconvert_groupbox.setLayout(self.netconvert_main_layout)

        self.polyconvert_sublayout = QHBoxLayout()
        self.polyconvert_sublayout.addWidget(self.polyconvert_btn)
        self.polyconvert_sublayout.addWidget(self.check_polyconvert_file)
        self.polyconvert_sublayout.setAlignment(Qt.AlignRight)
        self.polyconvert_groupbox.setLayout(self.polyconvert_sublayout)

        self.taz_sublayout = QHBoxLayout()
        self.taz_sublayout.addWidget(self.label_netedit, Qt.AlignLeft)
        self.taz_sublayout.addWidget(self.run_netedit_btn, Qt.AlignRight)
        self.taz_sublayout.addWidget(self.check_netedit_file)
        self.taz_groupbox.setLayout(self.taz_sublayout)

        ##################   BUILD TRAFFIC DEMAND SUB LAYOUTS    #####################3
        # Compound traffic demand settings
        self.traffic_demand_settings_OD_ly = QVBoxLayout()
        self.traffic_demand_settings_OD_ly.addWidget(self.O_distric_label)
        self.traffic_demand_settings_OD_ly.addWidget(self.O_distric)
        self.traffic_demand_settings_OD_ly.addWidget(self.D_distric_label)
        self.traffic_demand_settings_OD_ly.addWidget(self.D_distric)

        self.traffic_demand_settings_GS_1_ly = QHBoxLayout()
        self.traffic_demand_settings_GS_1_ly.addWidget(self.label_rt_file_btn)
        self.traffic_demand_settings_GS_1_ly.addWidget(self.rt_file_btn)

        self.traffic_demand_settings_GS_2_ly = QHBoxLayout()
        self.traffic_demand_settings_GS_2_ly.addWidget(self.label_simtime_btn)
        self.traffic_demand_settings_GS_2_ly.addWidget(self.simtime_int_btn)

        self.traffic_demand_settings_GS_3_ly = QHBoxLayout()
        self.traffic_demand_settings_GS_3_ly.addWidget(self.sumo_rerouting_prob_label)
        self.traffic_demand_settings_GS_3_ly.addWidget(self.sumo_rerouting_prob_spin)

        self.traffic_demand_settings_GS_main_ly = QVBoxLayout()
        self.traffic_demand_settings_GS_main_ly.addLayout(self.traffic_demand_settings_GS_1_ly)
        self.traffic_demand_settings_GS_main_ly.addLayout(self.traffic_demand_settings_GS_2_ly)
        self.traffic_demand_settings_GS_main_ly.addLayout(self.traffic_demand_settings_GS_3_ly)

        self.traffic_demand_settings_main_ly = QHBoxLayout()
        self.traffic_demand_settings_main_ly.addLayout(self.traffic_demand_settings_OD_ly)
        self.traffic_demand_settings_main_ly.addLayout(self.traffic_demand_settings_GS_main_ly)
        self.traffic_setting_groupbox.setLayout(self.traffic_demand_settings_main_ly)


        self.simulation_main_ly = QHBoxLayout()
        self.simulation_main_ly.addWidget(self.sumo_output_tripinfo)
        self.simulation_main_ly.addWidget(self.sumo_output_summary)
        self.simulation_main_ly.addWidget(self.sumo_output_emissions)
        self.simulation_main_ly.addWidget(self.sumo_gui)
        #self.simulation_main_ly.addWidget(self.run_simulation_btn)
        self.simulation_groupbox.setLayout(self.simulation_main_ly)

        self.ly_RT = QHBoxLayout()
        self.ly_RT.addWidget(self.RT_description)
        self.ly_RT.addWidget(self.rt_btn)
        self.ly_RT.setAlignment(Qt.AlignRight)
        self.rt_groupbox.setLayout(self.ly_RT)

        self.ly_MA = QHBoxLayout()
        self.ly_MA.addWidget(self.MA_description)
        self.ly_MA.addWidget(self.ma_btn)
        self.ly_MA.setAlignment(Qt.AlignRight)
        self.ma_groupbox.setLayout(self.ly_MA)

        self.ly_DUA = QHBoxLayout()
        self.ly_DUA.addWidget(self.DUA_description)
        self.ly_DUA.addWidget(self.dua_btn)
        self.ly_DUA.setAlignment(Qt.AlignRight)
        self.dua_groupbox.setLayout(self.ly_DUA)

        self.ly_DUAI = QHBoxLayout()
        self.ly_DUAI.addWidget(self.DUAI_description)
        self.ly_DUAI.addWidget(self.duai_btn)
        self.ly_DUAI.setAlignment(Qt.AlignRight)
        self.duai_groupbox.setLayout(self.ly_DUAI)

        self.ly_OD2 = QHBoxLayout()
        self.ly_OD2.addWidget(self.OD2_description)
        self.ly_OD2.addWidget(self.od2_btn)
        self.ly_OD2.setAlignment(Qt.AlignRight)
        self.od2_groupbox.setLayout(self.ly_OD2)

        ################### STATISTICS LAYOUT  ###############################
        self.statistics_ly_rou = QHBoxLayout()
        self.statistics_ly_rou.addWidget(self.read_route_file_btn)
        self.statistics_ly_rou.addWidget(self.check_rou_file)

        self.statistics_ly_sum = QHBoxLayout()
        self.statistics_ly_sum.addWidget(self.read_summary_file_btn)
        self.statistics_ly_sum.addWidget(self.check_summary_file)

        self.statistics_ly_trip = QHBoxLayout()
        self.statistics_ly_trip.addWidget(self.read_tripinfo_file_btn)
        self.statistics_ly_trip.addWidget(self.check_tripinfo_file)

        self.statistics_ly_emi = QHBoxLayout()
        self.statistics_ly_emi.addWidget(self.read_emissions_file_btn)
        self.statistics_ly_emi.addWidget(self.check_emissions_file)

        self.statistics_main_ly = QVBoxLayout()
        self.statistics_main_ly.addLayout(self.statistics_ly_rou)
        self.statistics_main_ly.addLayout(self.statistics_ly_sum)
        self.statistics_main_ly.addLayout(self.statistics_ly_trip)
        self.statistics_main_ly.addLayout(self.statistics_ly_emi)
        self.statistics_groupbox.setLayout(self.statistics_main_ly)

        ##################   CONTAINER BUILD NETWORK    #####################3
        self.container_build_network = QFormLayout()
        self.container_build_network.addRow(self.osm_groupbox)
        self.container_build_network.addRow(self.netconvert_groupbox)
        self.container_build_network.addRow(self.polyconvert_groupbox)
        self.container_build_network.addRow(self.taz_groupbox)
        #self.container_build_network.addRow(self.progress_bar)
        self.container_build_network.addRow(self.cmd_str) # log text
        self.wdg_build_network.setLayout(self.container_build_network)
        #######################  TAB ROTUNGI WIDGETS  ####################
        self.wdg_tab_rt_routing = QWidget()
        self.wdg_tab_ma_routing = QWidget()
        self.wdg_tab_dua_routing = QWidget()
        self.wdg_tab_duai_routing = QWidget()
        self.wdg_tab_od2_routing = QWidget()
        ####################### TAB CONTAINERS TRAFFIC DEMAND ###################
        self.container_tab_rt_widget = QFormLayout()
        self.container_tab_rt_widget.addRow(self.rt_groupbox)
        self.wdg_tab_rt_routing.setLayout(self.container_tab_rt_widget)

        self.container_tab_ma_widget = QFormLayout()
        self.container_tab_ma_widget.addRow(self.ma_groupbox)
        self.wdg_tab_ma_routing.setLayout(self.container_tab_ma_widget)

        self.container_tab_dua_widget = QFormLayout()
        self.container_tab_dua_widget.addRow(self.dua_groupbox)
        self.wdg_tab_dua_routing.setLayout(self.container_tab_dua_widget)

        self.container_tab_duai_widget = QFormLayout()
        self.container_tab_duai_widget.addRow(self.duai_groupbox)
        self.wdg_tab_duai_routing.setLayout(self.container_tab_duai_widget)

        self.container_tab_od2_widget = QFormLayout()
        self.container_tab_od2_widget.addRow(self.od2_groupbox)
        self.wdg_tab_od2_routing.setLayout(self.container_tab_od2_widget)

        ########### TAB TRAFFIC DEMAND WIDGETS #############
        self.tab_routing_op.addTab(self.wdg_tab_rt_routing, "RandomTrips")
        self.tab_routing_op.addTab(self.wdg_tab_ma_routing, "MARouter")
        self.tab_routing_op.addTab(self.wdg_tab_dua_routing, "DUARouter")
        self.tab_routing_op.addTab(self.wdg_tab_duai_routing, "DUAIterate")
        self.tab_routing_op.addTab(self.wdg_tab_od2_routing, "OD2Trips")
        ##################   CONTAINER TRAFFIC DEMAND    #####################3
        self.container_traffic = QFormLayout()
        self.container_traffic.addRow(self.tab_routing_op)
        self.container_traffic.addRow(self.traffic_setting_groupbox)
        self.container_traffic.addRow(self.traffic_demand_cmd)
        self.wdg_traffic_demand.setLayout(self.container_traffic)
        ##################   CONTAINER SIMULATIONS     #####################3
        self.container_simulation = QFormLayout()
        self.container_simulation.addRow(self.sumo_simulation_label)
        self.container_simulation.addRow(self.simulation_groupbox)
        self.container_simulation.addRow(self.run_simulation_btn)
        self.container_simulation.addRow(self.process_outputs_simulation_btn)
        self.container_simulation.addRow(self.cmd_output_str)
        self.wdg_simulation.setLayout(self.container_simulation)
        ##################   CONTAINER STATISTICS     #####################3
        self.container_statistics = QFormLayout()
        self.container_statistics.addRow(self.statistics_groupbox)
        self.wdg_statistics.setLayout(self.container_statistics)


        # Match with main layout
        self.setLayout(self.tab_main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)  # create applications
    dlgMain = DlgMain()  # create main GUI canvas
    dlgMain.show()  # Show gui console
    sys.exit(app.exec_())








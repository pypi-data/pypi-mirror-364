from __future__ import annotations

from orangewidget import gui, settings, widget
from orangewidget.widget import Output
from silx.gui import qt

import tomwer.core.process.control.datalistener.datalistener
from orangecontrib.tomwer.widgets.utils import WidgetLongProcessing
from tomwer.core.process.control.datalistener import DataListener
from tomwer.core.process.control.datalistener.rpcserver import (
    send_signal_to_local_rpc_servers,
)
from tomwer.core.process.control.nxtomomill import H5ToNxProcess
from tomwer.core.scan.blissscan import BlissScan
from tomwer.core.scan.scanbase import TomwerScanBase
from tomwer.gui.control.datalistener import DataListenerWidget
from tomwer.synctools.datalistener import DataListenerQThread, MockDataListenerQThread
from tomwer.synctools.stacks.control.datalistener import DataListenerProcessStack
from tomwer.utils import docstring

try:
    # new HDF5Config class
    from nxtomomill.io.config import TomoHDF5Config as HDF5Config
except ImportError:
    from nxtomomill.io.config import HDF5Config

import functools
import logging
import signal
import sys
from typing import Iterable

logger = logging.getLogger(__name__)


class DataListenerOW(
    widget.OWBaseWidget, WidgetLongProcessing, DataListener, openclass=True
):
    """
    This widget is used to listen to a server notifying the widget when an
    acquisition is finished.
    Then the bliss file will be converted to .nx file, NXtomo compliant.
    """

    name = "scan listener"
    id = "orangecontrib.widgets.tomwer.control.DataListenerOW.DataListenerOW"
    description = (
        "The widget will receive information from bliss acquisition "
        "and wait for acquisition to be finished. Once finished it "
        "will call nxtomomill to convert from bliss .hdf5 to "
        "NXtomo compliant .nx file"
    )
    icon = "icons/datalistener.svg"
    priority = 10
    keywords = [
        "tomography",
        "file",
        "tomwer",
        "listener",
        "datalistener",
        "hdf5",
        "NXtomo",
    ]

    want_main_area = True
    want_control_area = False
    resizing_enabled = True

    ewokstaskclass = (
        tomwer.core.process.control.datalistener.datalistener._DataListenerTaskPlaceHolder
    )

    _blissConfiguration = settings.Setting(dict())
    # to keep backward compatibility

    _nxtomo_cfg_file = settings.Setting(str())
    # to keep backward compatibility

    _static_input = settings.Setting(dict())

    class Outputs:
        data = Output(name="data", type=TomwerScanBase, doc="one scan to be process")

    def __init__(self, parent=None):
        widget.OWBaseWidget.__init__(self, parent)
        WidgetLongProcessing.__init__(self)
        DataListener.__init__(self)
        self._processingStack = DataListenerProcessStack()
        self._processingStack.sigComputationEnded.connect(self._signal_scan_ready)
        self._widget = DataListenerWidget(parent=self)
        self._mock = False

        self._box = gui.vBox(self.mainArea, self.name)
        layout = self._box.layout()
        layout.addWidget(self._widget)

        # signal / slot connection
        self._widget.sigActivate.connect(self._activated)
        self._widget.sigDeactivate.connect(self._deactivated)
        self._widget.sigConfigurationChanged.connect(self._jsonRPCConfigChanged)
        self._widget.sigCFGFileChanged.connect(self._nxtomoFileChanged)
        self._widget.sigAcquisitionEnded.connect(self._process_bliss_file_frm_tuple)
        self._widget.sigServerStopped.connect(self._serverStopped)

        # manage server stop when delete directly the widget or stop by Ctr+C
        signal.signal(signal.SIGINT, self.handleSigTerm)
        onDestroy = functools.partial(self._stopServerBeforeclosing)
        self.destroyed.connect(onDestroy)

        # set up
        self._loadSettings()

        # for conveniance start the listener when create it.
        self.activate(True)

    def _loadSettings(self):
        if "bliss_server_configuration" in self._static_input:  # pylint: disable=E1135
            bliss_configuration = self._static_input[  # pylint: disable=E1136
                "bliss_server_configuration"
            ]
        else:
            bliss_configuration = self._blissConfiguration
        if bliss_configuration != {}:
            self._widget.setBlissServerConfiguation(bliss_configuration)
        if "nxtomomill_cfg_file" in self._static_input:  # pylint: disable=E1135
            nxtomo_cfg_file = self._static_input[  # pylint: disable=E1136
                "nxtomomill_cfg_file"
            ]
        else:
            nxtomo_cfg_file = self._nxtomo_cfg_file
        self._widget.setCFGFilePath(nxtomo_cfg_file)
        if "output_dir" in self._static_input:  # pylint: disable=E1135
            self._widget.setOutputFolder(
                self._static_input["output_dir"]  # pylint: disable=E1136
            )

    def getNXTomomillConfiguration(self):
        cfg_file = self._widget.getCFGFilePath()

        def create_default_config():
            configuration = HDF5Config()
            configuration.bam_single_file = True
            configuration.no_master_file = True
            return configuration

        if cfg_file in (None, ""):
            config = create_default_config()
        else:
            try:
                config = HDF5Config.from_cfg_file(cfg_file)
            except Exception as e:
                logger.warning(f"Fail to load configuration file. Error is {e}")
                config = create_default_config()

        return config

    def _process_bliss_file_frm_tuple(self, t):
        master_file, entry, proposal_file, saving_file, success = t
        bliss_scan = BlissScan(
            master_file=master_file,
            entry=str(entry) + ".1",
            proposal_file=proposal_file,
            saving_file=saving_file,
        )
        configuration = self.getNXTomomillConfiguration()
        # overwrite output file
        configuration.output_file = H5ToNxProcess.deduce_output_file_path(
            bliss_scan.master_file,
            entry=bliss_scan.entry,
            outputdir=self._widget.getOutputFolder(),
            scan=bliss_scan,
        )
        if success:
            self._processingStack.add(data=bliss_scan, configuration=configuration)
        else:
            # TODO: maybe remove the acquisition ?
            pass

    def _activated(self):
        self.activate(True)

    def _deactivated(self):
        self.activate(False)

    def _serverStopped(self):
        """
        Callback when the server is stopped
        """
        self.activate(False)

    @docstring(DataListener.activate)
    def activate(self, activate=True):
        if activate and not self.is_port_available():
            old = self._widget.blockSignals(True)
            self._widget.activate(activate=False)
            self._widget.blockSignals(old)
            dialog = _PortOccupyDialog(parent=self, port=self.port, host=self.host)
            dialog.setModal(False)
            if dialog.exec_() == qt.QDialog.Accepted:
                if dialog.retry_connection:
                    return self.activate(activate=True)
            else:
                return

        old = self._widget.blockSignals(True)
        self.set_configuration(self._widget.getBlissServerConfiguration())
        self._widget.activate(activate=activate)
        DataListener.activate(self, activate=activate)
        self.processing_state(activate, info="listener active")
        self._widget.blockSignals(old)

    def _signal_scan_ready(self, scan, future_tomo_obj):
        if scan is None:
            return
        assert isinstance(scan, Iterable)
        for s in scan:
            assert isinstance(s, TomwerScanBase)
            self.Outputs.data.send(s)

    def _ask_user_for_overwritting(self, file_path):
        msg = qt.QMessageBox(self)
        msg.setIcon(qt.QMessageBox.Question)
        types = qt.QMessageBox.Ok | qt.QMessageBox.Cancel
        msg.setStandardButtons(types)

        text = "NXtomomill will overwrite: \n %s. Do you agree ?" % file_path
        msg.setText(text)
        return msg.exec_() == qt.QMessageBox.Ok

    def _jsonRPCConfigChanged(self):
        self._blissConfiguration = self._widget.getBlissServerConfiguration()
        self._static_input["bliss_server_configuration"] = (  # pylint: disable=E1137
            self._widget.getBlissServerConfiguration()
        )
        self._static_input["output_dir"] = (  # pylint: disable=E1137
            self._widget.getOutputFolder()
        )
        if self.is_active():
            self.activate(False)
            self.activate(True)

    def _nxtomoFileChanged(self, cfg_file):
        self._nxtomo_cfg_file = cfg_file
        self._static_input["nxtomomill_cfg_file"] = cfg_file  # pylint: disable=E1137

    def setMock(self, mock, acquisitions):
        self._mock = mock
        self._mock_acquisitions = acquisitions

    @docstring(DataListenerWidget.getHost)
    def getHost(self):
        return self._widget.getHost()

    @docstring(DataListenerWidget.getPort)
    def getPort(self):
        return self._widget.getPort()

    def close(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.activate(False)
        super().close()

    @docstring(DataListener.create_listening_thread)
    def create_listening_thread(self):
        if self._mock is True:
            thread = MockDataListenerQThread(
                host=self.getHost(),
                port=self.getPort(),
                acquisitions=None,
                mock_acquisitions=self._mock_acquisitions,
            )
        else:
            thread = DataListenerQThread(
                host=self.getHost(), port=self.getPort(), acquisitions=None
            )
        # connect thread
        thread.sigAcquisitionStarted.connect(
            self._widget._acquisitionStarted, qt.Qt.DirectConnection
        )
        thread.sigAcquisitionEnded.connect(
            self._widget._acquisitionEnded, qt.Qt.DirectConnection
        )
        thread.sigScanAdded.connect(
            self._widget._acquisitionUpdated, qt.Qt.DirectConnection
        )
        thread.sigServerStop.connect(
            self._widget._serverStopped, qt.Qt.DirectConnection
        )
        return thread

    @docstring(DataListener.delete_listening_thread)
    def delete_listening_thread(self):
        self._listening_thread.sigAcquisitionStarted.disconnect(
            self._widget._acquisitionStarted
        )
        self._listening_thread.sigAcquisitionEnded.disconnect(
            self._widget._acquisitionEnded
        )
        self._listening_thread.sigScanAdded.disconnect(self._widget._acquisitionUpdated)
        self._listening_thread.sigServerStop.disconnect(self._widget._serverStopped)
        DataListener.delete_listening_thread(self)

    def _stopServerBeforeclosing(self):
        self.activate(False)

    def handleSigTerm(self, signo, *args, **kwargs):
        if signo == signal.SIGINT:
            self._stopServerBeforeclosing()
            sys.exit()

    def _get_n_scan_observe(self):
        return self._widget._observationWidget.observationTable.model().rowCount()

    def _get_n_scan_finished(self):
        return self._widget._historyWindow.scanHistory.model().rowCount()


class _PortOccupyDialog(qt.QDialog):
    def __init__(self, parent, port, host):
        qt.QDialog.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self._retry = False
        self.port = port
        self.host = host

        mess = (
            f"port ({port}) of {host} already in use. \n Maybe an other "
            "instance of `datalistener` is running in this session or "
            "another tomwer session. \n As this widget is connecting with "
            "bliss we enforce it to be unique."
        )
        self.layout().addWidget(qt.QLabel(mess, self))
        self.setWindowTitle("Unable to launch two listener in parallel")

        types = qt.QDialogButtonBox.Cancel | qt.QDialogButtonBox.Retry
        self._buttons = qt.QDialogButtonBox(self)
        self._buttons.setStandardButtons(types)
        self.layout().addWidget(self._buttons)

        self._sendSIGTERMMsb = qt.QPushButton("send SIGTERM", self)
        self._sendSIGTERMMsb.setToolTip(
            "Try to send SIGTERM signal to the "
            "local tomwer-rpcserver if any "
            "occupies the reserved port"
        )
        self._buttons.addButton(self._sendSIGTERMMsb, qt.QDialogButtonBox.ActionRole)
        self._sendSIGKILLMsb = qt.QPushButton("send SIGKILL", self)
        self._sendSIGKILLMsb.setToolTip(
            "Try to send SIGKILL signal to the "
            "local tomwer-rpcserver if any "
            "occupies the reserved port"
        )
        self._buttons.addButton(self._sendSIGKILLMsb, qt.QDialogButtonBox.ActionRole)

        # set up
        # for now we don't want to show "send signal" feature
        self._sendSIGTERMMsb.hide()
        self._sendSIGKILLMsb.hide()

        # connect signal / slot
        self._buttons.button(qt.QDialogButtonBox.Cancel).released.connect(self.reject)
        self._buttons.button(qt.QDialogButtonBox.Retry).released.connect(
            self._retry_connect
        )
        self._sendSIGTERMMsb.released.connect(self._emitSigterm)
        self._sendSIGKILLMsb.released.connect(self._emitSigkill)

    @property
    def retry_connection(self):
        return self._retry

    def _emitSigterm(self, *args, **kwargs):
        send_signal_to_local_rpc_servers(signal.SIGTERM, port=self.port)

    def _emitSigkill(self, *args, **kwargs):
        send_signal_to_local_rpc_servers(signal.SIGKILL, port=self.port)

    def _retry_connect(self, *args, **kargs):
        self._retry = True
        self.accept()

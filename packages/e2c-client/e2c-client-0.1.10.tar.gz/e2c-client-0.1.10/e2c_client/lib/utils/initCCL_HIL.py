# Trimmed down and slightly modified version of https://bitbucket.sco.alma.cl/projects/ALMA/repos/almasw/browse/ADC/SW/SWTools/CCLTools/src/initCCL.py
# import pdb;pdb.set_trace()

import sys


def _turn_amb_mgr(abm=None):
    # pylint: disable=undefined-variable  # CentralLO
    """
    Turn on ambManager.
    """
    # Note: devices with wide ranges are checked separately below
    # Obtain the AMB Manager instance
    from CCL.AmbManager import AmbManager
    from CCL.Antenna import Antenna

    from CCL.CentralLO import CentralLO
    from CCL.AOSTiming import AOSTiming

    abm_avail = []
    # abm_avail = abm_list
    abms_list = []
    # print "Available ABM parameters:" +str(abm_avail)
    if abm is not None:
        abm_avail = []
        abm_avail.append(abm)
    for abms in abm_avail:
        # print "ABM : %s" % str(abms)
        node_list = []
        node_list.append(abms)
        try:
            if abms == "ACADMC":
                clo = CentralLO(stickyFlag=1)
                if (
                    str(clo.getState()) != "Operational"
                    and str(clo.getState()) != "Degraded"
                ):
                    clo.controllerOperational()
                if not clo.isAmbManagerRunning("ACADMC"):
                    clo.startAmbManager("ACADMC")
                del clo
            if abms == "DMC":
                clo = CentralLO(stickyFlag=1)
                if (
                    str(clo.getState()) != "Operational"
                    and str(clo.getState()) != "Degraded"
                ):
                    clo.controllerOperational()
                if not clo.isAmbManagerRunning("DMC"):
                    clo.startAmbManager("DMC")
                del clo
            if abms == "DMC2":
                clo = CentralLO(stickyFlag=1)
                if (
                    str(clo.getState()) != "Operational"
                    and str(clo.getState()) != "Degraded"
                ):
                    clo.controllerOperational()
                if not clo.isAmbManagerRunning("DMC2"):
                    clo.startAmbManager("DMC2")
                del clo
            if abms == "DMC3":
                clo = CentralLO(stickyFlag=1)
                if (
                    str(clo.getState()) != "Operational"
                    and str(clo.getState()) != "Degraded"
                ):
                    clo.controllerOperational()
                if not clo.isAmbManagerRunning("DMC3"):
                    clo.startAmbManager("DMC3")
                del clo
            if abms == "DMC4":
                clo = CentralLO(stickyFlag=1)
                if (
                    str(clo.getState()) != "Operational"
                    and str(clo.getState()) != "Degraded"
                ):
                    clo.controllerOperational()
                if not clo.isAmbManagerRunning("DMC4"):
                    clo.startAmbManager("DMC4")
                del clo
            if abms == "LMC":
                clo = CentralLO(stickyFlag=1)
                if (
                    str(clo.getState()) != "Operational"
                    and str(clo.getState()) != "Degraded"
                ):
                    clo.controllerOperational()
                if not clo.isAmbManagerRunning("LMC"):
                    clo.startAmbManager("LMC")
                del clo
            if abms == "LMC2":
                clo = CentralLO(stickyFlag=1)
                if (
                    str(clo.getState()) != "Operational"
                    and str(clo.getState()) != "Degraded"
                ):
                    clo.controllerOperational()
                if not clo.isAmbManagerRunning("LMC2"):
                    clo.startAmbManager("LMC2")
                del clo
            if abms == "LMC3":
                clo = CentralLO(stickyFlag=1)
                if (
                    str(clo.getState()) != "Operational"
                    and str(clo.getState()) != "Degraded"
                ):
                    clo.controllerOperational()
                if not clo.isAmbManagerRunning("LMC3"):
                    clo.startAmbManager("LMC3")
                del clo
            if abms == "LMC4":
                clo = CentralLO(stickyFlag=1)
                if (
                    str(clo.getState()) != "Operational"
                    and str(clo.getState()) != "Degraded"
                ):
                    clo.controllerOperational()
                if not clo.isAmbManagerRunning("LMC4"):
                    clo.startAmbManager("LMC4")
                del clo
            if abms == "AOSTiming":
                aos = AOSTiming(stickyFlag=1)
                if (
                    str(aos.getState()) != "Operational"
                    and str(aos.getState()) != "Degraded"
                ):
                    aos.controllerOperational()
                if not aos.isAmbManagerRunning():
                    aos.startAmbManager()
                del aos
            if (
                (abms.rfind("DV") >= 0)
                or (abms.rfind("DA") >= 0)
                or (abms.rfind("PM") >= 0)
                or (abms.rfind("CM") >= 0)
                or (abms.rfind("LA") >= 0)
            ):
                ant = Antenna(abms)
                if not ant.isAmbManagerRunning():
                    ant.startAmbManager()
                del ant
            mgr = AmbManager(abms)
            # Get all nodes
            # pylint: disable=unused-variable
            nodes = mgr.getAllNodes()
            # Free the AMB Manager instance
            del mgr
        except Exception as ex:
            print("It was not possible turn on AmbManager for %s ABM" % abms)
            #            print ex
            return abms_list
        # Display the nodes
    #        print "Currently available devices:"
    #        for entry in nodes[0]:
    #            try:
    #                device_name = __get_device_name(entry.node)
    #            except Exception, ex:
    #                device_name = "Unknown"
    #                print ex
    #            print "Channel %d Node 0x%X" % (entry.channel, entry.node), "SN", entry.sn, ":", device_name
    #            node_list.append(entry.node)
    #        abms_list.append(node_list)
    #    if(abm is None):
    #        return abms_list
    return abms_list


#
# Nodes names
#


def __get_device_name(rca):
    """
    Node/name asignation
    """
    device_list = {
        0x00: "Antenna Control Unit [ACU]",
        0x01: "Pointing Computer",
        0x10: "FE Compressor [FEC]",
        0x13: "Front End Monitor & Control",
        0x1C: "Holography Receiver [HoloRX]",
        0x1D: "Holography DSP      [HoloDSP]",
        0x1E: "125MHz Reference Distributor",
        0x1F: "Optical Pointing Telescope",
        0x20: "Central Reference Distributor [CRD]",
        0x21: "Nutator",
        0x22: "LO Reference Receiver [LORR/LFTRR]",
        0x23: "Frontend Assembly",
        0x24: "Water Vapour Radiometer [WVR]",
        0x25: "Compressor [CMPR]",
        0x26: "Frontend Power Supply",
        0x27: "Master Laser Distribution [MLD]",
        0x28: "Calibration Widgets [ACD]",
        0x29: "IF Processor [IFProc]",
        0x2A: "IF Processor [IFProc]",
        0x2B: "Master Laser [ML]",
        0x2C: "Master Laser [ML]",
        0x30: "Digitizer Clock [DGCK]",
        0x31: "5MHz Distributor",
        0x32: "First LO Offset Generator [FLOOG]",
        0x33: "Low Frequency Reference Distribution [LFRD]",
        0x40: "2nd LO Synthesizer [LO2]",
        0x41: "2nd LO Synthesizer [LO2]",
        0x42: "2nd LO Synthesizer [LO2]",
        0x43: "2nd LO Synthesizer [LO2]",
        0x44: "IF Processor [IFProc]",
        0x45: "IF Processor [IFProc]",
        0x46: "IF Processor [IFProc]",
        0x47: "IF Processor [IFProc]",
        0x50: "DTS Transmitter Module [DTX]",
        0x51: "DTS Transmitter Module [DTX]",
        0x52: "DTS Transmitter Module [DTX]",
        0x53: "DTS Transmitter Module [DTX]",
        0x60: "Power Supply (analog rack) [PSA]",
        0x61: "Power Supply (digital rack) [PSD]",
        0x62: "Power Supply (CRD) [PSCRD]",
        0x3F: "Local Oscilator Reference Test Module [LORTM]",
    }
    name = "Unknown"
    try:
        name = device_list[rca]
    except:
        if rca in range(0x100, 0x1FF + 1):
            name = "DTS Receiver Module [DRX]"
        elif rca in range(0x200, 0x27F + 1):
            name = "Line Length Corrector [LLC]"
        elif rca in range(0x280, 0x29F + 1):
            name = "Fiber Optic Amplifier Demux [FOAD]"
        elif rca in range(0x300, 0x34F + 1):
            name = "Sub Array Switch [SAS]"
        elif rca in range(0x48, 0x4D + 1):
            name = "Photonic Reference Distributor [PRD]"
        elif rca in range(0x58, 0x5D + 1):
            name = "Power Supply LLC [PSLLC]"
        elif rca in range(0x5E, 0x63 + 1):
            name = "Power Supply SAS [PSSAS]"
        elif rca in range(0x38, 0x3D + 1):
            name = "Laser Synthesizer [LS]"
    return name


#
# Display a list of all available HW devices
#


def _getAllNodes(mgr):
    """ """
    nodes = []
    for channel in range(0, int(mgr.getNumberOfChannels()[0])):
        for node in mgr.getNodes(channel)[0]:
            nodes.append(node)
    return nodes


def get_devices(abm=None):
    """
    Displays which devices are currently available at the given
    ABM parameter (see the controller name as reference).
    Example:
    get_devices("DV01")
    """
    # Note: devices with wide ranges are checked separately below
    # Obtain the AMB Manager instance
    from Acspy.Clients.SimpleClient import PySimpleClient

    abm_avail = []
    # abm_avail = abm_list
    abms_list = []
    print("Available ABM parameters:" + str(abm_avail))
    if abm is not None:
        abm_avail = []
        abm_avail.append(abm)
    for abms in abm_avail:
        print("ABM : %s" % str(abms))
        node_list = []
        node_list.append(abms)
        try:
            mgr = None
            sys.stdout = open("/dev/null", "w")
            client = PySimpleClient("CAN STATUS")
            sys.stdout = sys.__stdout__
            deployed_mgrs = client.availableComponents(
                type_wildcard="IDL:alma/Control/AmbManager:1.0"
            )
            for deployed_mgr in deployed_mgrs:
                if deployed_mgr.name.__contains__(abms):
                    try:
                        mgr = client.getDynamicComponent(
                            deployed_mgr.name,
                            deployed_mgr.type,
                            deployed_mgr.code,
                            deployed_mgr.container_name,
                        )
                        break
                    except maciErrType.CannotGetComponentEx as e:
                        print("It was not possible get AmbManager for %s ABM" % abms)
                        print(e[0].shortDescription)
                        return []
                    except Exception as e:
                        print("It was not possible get AmbManager for %s ABM" % abms)
                        print(e.__str__())
                        return []
            if abms == "ACADMC":
                try:
                    mgr = client.getDynamicComponent(
                        "CONTROL/ACADMC/AmbManager",
                        "IDL:alma/Control/AmbManager:1.0",
                        "ambManagerImpl",
                        "CONTROL/ACADMC/cppContainer",
                    )
                except maciErrType.CannotGetComponentEx as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e[0].shortDescription)
                    return []
                except Exception as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e.__str__())
                    return []
            if abms == "DMC":
                try:
                    mgr = client.getDynamicComponent(
                        "CONTROL/DMC/AmbManager",
                        "IDL:alma/Control/AmbManager:1.0",
                        "ambManagerImpl",
                        "CONTROL/DMC/cppContainer",
                    )
                except maciErrType.CannotGetComponentEx as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e[0].shortDescription)
                    return []
                except Exception as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e.__str__())
                    return []
            if abms == "DMC2":
                try:
                    mgr = client.getDynamicComponent(
                        "CONTROL/DMC2/AmbManager",
                        "IDL:alma/Control/AmbManager:1.0",
                        "ambManagerImpl",
                        "CONTROL/DMC2/cppContainer",
                    )
                except maciErrType.CannotGetComponentEx as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e[0].shortDescription)
                    return []
                except Exception as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e.__str__())
                    return []
            if abms == "DMC3":
                try:
                    mgr = client.getDynamicComponent(
                        "CONTROL/DMC3/AmbManager",
                        "IDL:alma/Control/AmbManager:1.0",
                        "ambManagerImpl",
                        "CONTROL/DMC3/cppContainer",
                    )
                except maciErrType.CannotGetComponentEx as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e[0].shortDescription)
                    return []
                except Exception as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e.__str__())
                    return []
            if abms == "DMC4":
                try:
                    mgr = client.getDynamicComponent(
                        "CONTROL/DMC4/AmbManager",
                        "IDL:alma/Control/AmbManager:1.0",
                        "ambManagerImpl",
                        "CONTROL/DMC4/cppContainer",
                    )
                except maciErrType.CannotGetComponentEx as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e[0].shortDescription)
                    return []
                except Exception as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e.__str__())
                    return []
            if abms == "LMC":
                try:
                    mgr = client.getDynamicComponent(
                        "CONTROL/LMC/AmbManager",
                        "IDL:alma/Control/AmbManager:1.0",
                        "ambManagerImpl",
                        "CONTROL/LMC/cppContainer",
                    )
                except maciErrType.CannotGetComponentEx as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e[0].shortDescription)
                    return []
                except Exception as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e.__str__())
                    return []
            if abms == "LMC2":
                try:
                    mgr = client.getDynamicComponent(
                        "CONTROL/LMC2/AmbManager",
                        "IDL:alma/Control/AmbManager:1.0",
                        "ambManagerImpl",
                        "CONTROL/LMC2/cppContainer",
                    )
                except maciErrType.CannotGetComponentEx as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e[0].shortDescription)
                    return []
                except Exception as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e.__str__())
                    return []
            if abms == "LMC3":
                try:
                    mgr = client.getDynamicComponent(
                        "CONTROL/LMC3/AmbManager",
                        "IDL:alma/Control/AmbManager:1.0",
                        "ambManagerImpl",
                        "CONTROL/LMC3/cppContainer",
                    )
                except maciErrType.CannotGetComponentEx as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e[0].shortDescription)
                    return []
                except Exception as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e.__str__())
                    return []
            if abms == "LMC4":
                try:
                    mgr = client.getDynamicComponent(
                        "CONTROL/LMC4/AmbManager",
                        "IDL:alma/Control/AmbManager:1.0",
                        "ambManagerImpl",
                        "CONTROL/LMC4/cppContainer",
                    )
                except maciErrType.CannotGetComponentEx as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e[0].shortDescription)
                    return []
                except Exception as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(e.__str__())
                    return []
            if abms == "AOSTiming":
                try:
                    mgr = client.getDynamicComponent(
                        "CONTROL/ARTM/AmbManager",
                        "IDL:alma/Control/AmbManager:1.0",
                        "ambManagerImpl",
                        "CONTROL/ARTM/cppContainer",
                    )
                except maciErrType.CannotGetComponentEx as e:
                    print(e[0].shortDescription)
                    print(
                        "Remember: For SDTR and TCLOT, AOSTiming ABM is running in DMC machine."
                        " Try with get_devices('DMC')"
                    )
                    return []
                except Exception as e:
                    print("It was not possible get AmbManager for %s ABM" % abms)
                    print(
                        "Remember: For SDTR and TCLOT, AOSTiming ABM is running in DMC machine."
                        " Try with get_devices('DMC')"
                    )
                    print(e.__str__())
                    return []
            if mgr is None:
                print("No deployment for %s AmbManager" % abms)
                return []
            # Get all nodes
            nodes = _getAllNodes(mgr)
            _turn_amb_mgr(abms)
            # Free the AMB Manager instance
            del mgr
        except Exception as ex:
            print("It was not possible get AmbManager for %s ABM" % abms)
            print(ex.__str__())
            return abms_list
        finally:
            client.disconnect()

        # Display the nodes
        print("Currently available devices:")
        for entry in nodes:
            try:
                device_name = __get_device_name(entry.node)
            except Exception as ex:
                device_name = "Unknown"
                print(ex)
            print(
                "Channel %d Node 0x%X" % (entry.channel, entry.node), ":", device_name
            )
            node_list.append(entry.node)
        abms_list.append(node_list)
    if abm is None:
        return abms_list
    return []

# e2c-client

ALMA Ethernet-To-CAN socket server Python client package for LRU monitoring and control.

The `e2c-client` package provides an application and libraries for CAN-based monitoring and control of hardware devices through the Ethernet-To-CAN module.    
See ALMA-70.35.10.14-00.00.00.00-A-ICD for the ICD between Computing/E2C Socket Server Protocol and ALMA operations.

## Installation

    pip install e2c-client

If installed for user only in an APEx virtual environment, it may be necessary to unset the user PYTHONPATH environment variable for the current session:

    unset PYTHONPATH

## Installation for development

    git clone ssh://git@bitbucket.alma.cl:7999/eng/e2c-client.git
    cd e2c-client
    make venv
    source venv/bin/activate
    e2c-client --help

## Usage

Following is a non-exhaustive list of available commands, for illustrative purposes only. Use the following command for all available options:

    e2c-client --help
    e2c-client version

### Monitor-related commands

    e2c-client monitor --help
    e2c-client monitor request --host <host> --channel <channel> --node <node> --rca <RCA> # perform AMB monitor request
    e2c-client monitor temperature --host <host> --channel <channel> --node <node> # perform AMB monitor request for temperature
    e2c-client monitor nodes --host <host> # list all nodes and ESNs reported by E2C

### Control-related commands

    e2c-client control --help
    e2c-client monitor request --host <host> --channel <channel> --node <node> --rca <RCA> --data <data> # perform AMB control request

### Examples
#### Command-line client

List all CAN nodes (LRUs) reported by DV10 E2C
    
    $ e2c-client monitor nodes --host dv10-e2c
    Channel: 0, Node id: 0x22, ESN: 0x1080E126010800A2
    Channel: 0, Node id: 0x29, ESN: 0x10CD504101080009
    Channel: 0, Node id: 0x2a, ESN: 0x10697E41010800D3
    Channel: 0, Node id: 0x30, ESN: 0x1060264601080068
    Channel: 0, Node id: 0x32, ESN: 0x10CEB326010800D2
    Channel: 0, Node id: 0x40, ESN: 0x10986F4101080027
    Channel: 0, Node id: 0x41, ESN: 0x100FA82601080076
    Channel: 0, Node id: 0x42, ESN: 0x10E435460108006C
    Channel: 0, Node id: 0x43, ESN: 0x10C58041010800F6
    Channel: 0, Node id: 0x50, ESN: 0x108CFC4901080045
    Channel: 0, Node id: 0x51, ESN: 0x1090D84901080084
    Channel: 0, Node id: 0x52, ESN: 0x1007F149010800BB
    Channel: 0, Node id: 0x53, ESN: 0x10724A41010800EB
    Channel: 0, Node id: 0x60, ESN: 0x10C23E410108009E
    Channel: 0, Node id: 0x61, ESN: 0x105C3B7E020800D8
    Channel: 1, Node id: 0x24, ESN: 0x107F054A010800B3
    Channel: 1, Node id: 0x13, ESN: 0x10DA070401080072
    Channel: 1, Node id: 0x26, ESN: 0x107FB44C01080038
    Channel: 1, Node id: 0x28, ESN: 0x103D754101080051
    Channel: 2, Node id: 0x25, ESN: 0x104D994C010800AF

Request AMBSI temperature monitor point of DV10 LORR (raw data)

    $ e2c-client monitor request --host dv10-e2c --channel 0 --node 0x22 --rca 0x30003
    Error: 0
    Data: 
    0x55, 0x0, 0x8, 0x10

Request AMBSI temperature of DV10 LORR (utility function)

    $ e2c-client monitor temperature --host dv10-e2c --channel 0 --node 0x22 
    Temperature: 42.1875 [C]

Set BB attenuators on IFP0 of DA63 to A:12 dB, B:12.5 dB, C:9 dB, D:8.5 dB

    $ e2c-client control request --host da63-e2c --channel 0 --node 0x29 --rca 0x0181 --data "0x60 0x64 0x48 0x44"

#### Python library
    >>> import e2c_client
    >>> client = e2c_client.E2CClient("dv10-e2c")
    
    >>> # LORR on bus 0, node 0x22, relative CAN address 0x30003 (GET_AMBIENT_TEMPERATURE), mode 0 (monitor):
    >>> error, data = client.send_request(resource_id=0, bus_id=0, node_id=0x22, can_addr=0x30003, mode=0, data=b"")
    >>> print(", ".join(hex(b) for b in data))
    0x54, 0x0, 0x9, 0x10
    
    >>> # LORR on bus 0, node 0x22, relative CAN address 0x00082 (SET_CLEAR_FLAGS), mode 1 (control):
    >>> error, data = client.send_request(resource_id=0, bus_id=0, node_id=0x22, can_addr=0x00082, mode=1, data=b"\x01")
    
    >>> # Get E2C internal monitor point (GET_SERIAL_NUMBER, i.e., MAC address):
    >>> error, data = client.send_request(resource_id=0, bus_id=client.E2C_INTERNAL_CHANNEL,node_id=client.E2C_INTERNAL_NODE, can_addr=0x0000, mode=0, data=b"")
    >>> print(", ".join(hex(b) for b in data))
    0x0, 0xc, 0x69, 0xff, 0x0, 0xad, 0x0, 0x0

## TODO
Feel free to contribute on the following pending tasks:

* Improve error handling
* Add ICD errors number-to-description mapping for increased user understading on failures.
* Add real testing pytest template files.
* Code additional utility functions for critical recovery tasks like cryostat temperature and pressure monitoring, power supply status, etc.

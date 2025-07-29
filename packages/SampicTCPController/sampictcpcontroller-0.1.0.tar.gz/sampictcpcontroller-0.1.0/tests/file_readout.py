import argparse

from time import sleep
from SampicTCPController import SampicTCPController


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ipaddr", type=str, help="IP address of the controller")
    parser.add_argument("--port", type=int, help="port to use for the controller")
    parser.add_argument("--output", type=str, default="output.bin", help="output file to generate")

    args = parser.parse_args()

    sampic = SampicTCPController(args['ipaddr'], args['port'])
    sampic.dataTransmitToTCPClient(False)
    try:
        sampic.start(args['output'])
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        print("Acquisition stopped by C-c")
        sampic.stop()

if __name__ == '__main__':
    main()

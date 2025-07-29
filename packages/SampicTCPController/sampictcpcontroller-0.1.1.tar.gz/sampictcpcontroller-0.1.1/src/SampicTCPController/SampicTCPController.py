import socket
import logging
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class SampicTCPController:
    _socket = None
    _req_id: int = 0
    _run_req_id: int = 0
    _run_req_number: int = 0
    _started: bool = False
    _filename_base: str = None

    def __init__(self, ipaddr: str, port: int, timeout: float=-1.):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((ipaddr, port))
        if timeout > 0.:
            self._socket.settimeout(timeout)
        logger.info(f'Socket initialised for address {ipaddr}:{port}')
        self.stop()

    def fwVersion(self):
        answer = self._ask("FIRMWARE_VERSION?")
        if b'FIRMWARE_VERSION =' in answer:
            return self._sanitise(answer)
        logger.error(f"Invalid answer received from Sampic controller: {answer}")
        return None

    def swVersion(self):
        answer = self._ask("SOFTWARE_VERSION?")
        if b'SOFTWARE_VERSION =' in answer:
            return self._sanitise(answer)
        logger.error(f"Invalid answer received from Sampic controller: {answer}")
        return None

    def dataTransmitToTCPClient(self, enable: bool=True):
        if enable:
            answer = self._ask('ENABLE_DATA_TX_TO_TCP_CLIENT')
        else:
            answer = self._ask('DISABLE_DATA_TX_TO_TCP_CLIENT')
        if b'EXECUTED OK' in answer:
            logger.info(f'Successfully set the "data transmit to TCP client" flag to {enable}')
            return True
        logger.error('Failed to set the "data transmit to TCP client flag')
        return False

    def start(self, filename_base: str='', numHits: int=-1, acquisitionTime: int=-1) -> bool:
        '''Start the acquisition of frames into the output directory'''
        command = 'START_RUN'
        if filename_base:
            self._filename_base = filename_base
            command += f' -SAVETO {filename_base}'
        if numHits > 0:
            command += f' -HITS {numHits}'
        if acquisitionTime > 0:
            command += f' -TIME {acquisitionTime}'
        answer = self._ask(command)
        self._started = b'EXECUTED OK' in answer
        self._run_req_number = 1
        if self._started:
            self._run_req_id = self._req_id
            logger.info(f'Run started with command "{command}"')
        else:
            logger.error(f'Failed to start the run with command: "{command}". Received answer: {answer}')
        return self._started

    def stop(self):
        '''Stop the acquisition if started'''
        if not self._started:
            logger.warning("Requested to stop the acquisition although it was not started.")
        answer = self._ask('STOP_RUN')
        if b'EXECUTED OK' in answer:
            logger.info(f'Run stopped')
            self._started = False
        else:
            logger.error(f'Failed to stop the run. Received answer: {answer}')

    def read(self, buffer: bytearray, buffer_length: int=4096) -> int:
        if not self._started:
            raise RuntimeError('Acquisition must be started prior to readout')
        read_length = self._socket.recv_into(buffer, buffer_length)
        if b'RUN_FINISHED' in buffer:
            self._started = False
            return 0
        return read_length

    def acquireAndSave(self, output_filename: str, numHits: int=-1, acquisitionTime: int=-1):
        if not self.start(None, numHits, acquisitionTime):
            raise RuntimeError('Failed to start the acquisition')

        num_events = 0
        file = open(output_filename, 'wb')
        while True:
            try:
                buffer = self._socket.recv(1024)
                if b'RUN_FINISHED' in buffer:
                    break
                if b'\xab\xcd' in buffer:
                    num_events += 1
                file.write(bytearray(buffer))
            except KeyboardInterrupt:
                break
        self.stop()
        print(f"{num_events} event(s) acquired in this run")

    def numEvents(self):
        answer = self._ask("EVENT?", self._run_req_id, self._run_req_number)
        self._run_req_number += 1
        print(f"Num events recorded: {answer}")

    def _ask(self, command: str, request_id: int=-1, sub_request_id: int=-1):
        if not self._socket:
            raise RuntimeError(f'Socket not initialised. Cannot send the "{command}" command')
        if request_id < 0:
            request_id = self._req_id + 1
        if sub_request_id > 0:
            prepend = f'{request_id}.{sub_request_id}'
        else:
            prepend = f'{request_id}'
        built_command = f'#{prepend} {command}'
        logger.debug(f"Sending the following command to the board: {built_command}, request id={prepend}")
        self._socket.send(bytes(built_command, 'utf-8'))
        self._req_id = request_id
        return self._socket.recv(4096)

    def _sanitise(self, answer):
        return str(answer).replace("'", '').replace('\\n', '').split(' = ')[-1].strip()

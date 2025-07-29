import socket
import logging
import time

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

class SampicTCPController:
    _socket = None
    _req_id: int = 0
    _started: bool = False
    _filename_base: str = None
    _sleep_time: float = 0.5

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

    def start(self, filename_base: str='', numHits: int=-1, acquisitionTime: int=-1):
        '''Start the acquisition of frames into the output directory'''
        self._req_id += 1
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
        if self._started:
            logger.info(f'Run started with command "{command}"')
        else:
            logger.error(f'Failed to stop the run with command: "{command}". Received answer: {answer}')

    def stop(self):
        '''Stop the acquisition if started'''
        if not self._started:
            logger.warning("Requested to stop the acquisition although it was not started.")
        answer = self._ask('STOP_RUN')
        self._started = not(b'EXECUTED OK' in answer)
        if not self._started:
            logger.info(f'Run stopped')
        else:
            logger.error(f'Failed to stop the run. Received answer: {answer}')

    def read(self, buffer, buffer_length: int=1024) -> bool:
        if not self._started:
            raise RuntimeError('Acquisition must be started prior to readout')
        buffer = self._socket.recv(buffer_length)
        if 'RUN_FINISHED' in str(buffer):
            return False
        return True

    def acquireAndSave(self, output_filename: str, numHits: int=-1, acquisitionTime: int=-1):
        self.start(None, numHits, acquisitionTime)
        if not self._started:
            raise RuntimeError('Failed to start the acquisition')
        buffer = ''
        output_file = open(output_filename, 'wb')
        while True:
            try:
                buffer = self._socket.recv(1024)  #FIXME
                c_buffer = [hex(i) for i in buffer]
                print(len(c_buffer), c_buffer[0:12])
                if 'RUN_FINISHED' in str(buffer):
                    break
                output_file.write(buffer)
            except KeyboardInterrupt:
                break
        self.stop()

    def _ask(self, command: str):
        if not self._socket:
            raise RuntimeError(f'Socket not initialised. Cannot send the "{command}" command')
        self._req_id += 1
        built_command = f'#{self._req_id} {command}'
        self._socket.send(bytes(built_command, 'utf-8'))
        time.sleep(self._sleep_time)
        return self._socket.recv(1024)

    def _sanitise(self, answer):
        return str(answer).replace("'", '').replace('\\n', '').split(' = ')[-1].strip()

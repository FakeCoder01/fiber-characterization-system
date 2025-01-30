import time
import sqlite3
import numpy as np
from core.hardware_control import LaserController, Photodetector, AlignmentSystem
from core.image_analysis import FiberImageProcessor
from core.signal_processing import SignalProcessor
from core.models import MeasurementResult, init_db
import yaml
import threading
from queue import Queue

class FiberCharacterizationSystem:

    def __init__(self, config_file='config/config.yaml'):
        self.data_queue = Queue()

        with open(config_file) as f:
            self.config = yaml.safe_load(f)
            
        self.laser = LaserController(self.config['hardware']['laser'])
        self.detector = Photodetector(self.config['hardware']['detector'])
        self.alignment = AlignmentSystem()
        self.running = False
        
        self._init_database()
        self._start_data_acquisition()

    def _init_database(self):
        self.engine = init_db()
        self.conn = sqlite3.connect('measurements.db')
        
    def _start_data_acquisition(self):
        def acquisition_loop():
            while self.running:
                data = {
                    'timestamp': time.time(),
                    'wavelength': self.laser.get_current_wavelength(),
                    'power': self.detector.read_power()
                }
                self.data_queue.put(data)
                time.sleep(self.config['acquisition']['interval'])
                
        self.running = True
        self.acquisition_thread = threading.Thread(target=acquisition_loop)
        self.acquisition_thread.start()

    def run_full_characterization(self, sample):
        # automated alignment
        self.alignment.auto_align(self.detector)
        
        # spectral sweep
        wavelengths = np.linspace(
            self.config['sweep']['start'],
            self.config['sweep']['end'],
            self.config['sweep']['steps']
        )
        
        results = []
        for wl in wavelengths:
            self.laser.set_wavelength(wl)
            time.sleep(0.1)
            results.append(self.detector.read_power())
            
        # stores results
        measurement = MeasurementResult(
            fiber_type=sample['type'],
            wavelength=wl,
            power=np.mean(results),
            mfd=self.analyze_fiber_image(sample['image_path']),
            attenuation=SignalProcessor.calculate_attenuation(results, wavelengths)['alpha'],
            dispersion=SignalProcessor.analyze_dispersion(results, 
                self.config['acquisition']['sampling_rate'])['pmd']
        )
        
        self.conn.add(measurement)
        self.conn.commit()
        
        return measurement.to_dict()

    def analyze_fiber_image(self, image_path):
        analyzer = FiberImageProcessor(image_path)
        return analyzer.calculate_mfd()

    def shutdown(self):
        self.running = False
        self.acquisition_thread.join()
        self.conn.close()
        self.laser.shutdown()
        self.detector.shutdown()

if __name__ == '__main__':
    system = FiberCharacterizationSystem()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        system.shutdown()
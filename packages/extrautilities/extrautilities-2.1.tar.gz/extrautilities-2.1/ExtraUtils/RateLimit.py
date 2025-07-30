import threading
import time
from ExtraDecorators import validatetyping

class RateLimiter:
    @validatetyping
    def __init__(self, threshold:int,upperCap:int, decay_rate:int, decay_time:int, extreme_case:bool=False)->None:
        '''
        threshold: int -> The amount of triggers before the rate limiter will set hit to True
        upperCap: int -> The maximum amount of triggers to count (if reached any aditional triggers will not surpass the upperCap)
        decay_rate: int -> The amount of triggers that will be removed from the counter every decay cycle
        decay_time: int -> The time between each decay cycle
        extreme_case: bool -> if True, the RateLimited exception will be raised when the threshold is reached if False, only rate_limiter.hit will be set to True but no exception will be raised
        '''        
        self.threshold = threshold
        self.uppercap = upperCap
        self.decay_rate = decay_rate
        self.decay_time = decay_time
        self.extreme_case = extreme_case
        self.triggered = 0
        self.stoped = False
        self.lock = threading.Lock()
        self.decaying = True
        self.hit = False
        
        # Start decay thread
        decay_thread = threading.Thread(target=self.__decay)
        decay_thread.daemon = True
        decay_thread.start()

    def increment(self):
        with self.lock:
            if self.triggered < self.uppercap:
                self.triggered += 1
            if self.triggered > self.threshold:
                self.hit = True
                if self.extreme_case:
                    raise RateLimited()
            
    def __decay(self):
        while not self.stoped:
            time.sleep(self.decay_time)
            if not self.decaying:
                continue
            with self.lock:
                self.triggered -= self.decay_rate
                if self.triggered < self.threshold:
                    self.hit = False
                if self.triggered < 0:
                    self.triggered = 0
        
    def pause_decay(self):
        if self.stoped:
            raise ValueError("Decay is already stoped!")
        self.decaying = False
    
    def resume_decay(self):
        if self.stoped:
            raise ValueError("A stopped decay can't be resumed! Use ")
        self.decaying = True


class RateLimited(Exception):
    def __init__(self, message="Rate limit reached"):
        self.message = message
        super().__init__(self.message)
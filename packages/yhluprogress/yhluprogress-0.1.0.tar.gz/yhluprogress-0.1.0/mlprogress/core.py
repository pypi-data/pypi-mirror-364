import sys
import time

class MLProgress:
    def __init__(self, total, description="ML Progress", bar_length=40):
        self.total = total
        self.description = description
        self.bar_length = bar_length
        self.current = 0
        self.start_time = time.time()
        
    def update(self, increment=1):
        """更新进度"""
        self.current += increment
        self._print_progress()
        
    def _print_progress(self):
        """打印进度条"""
        progress = min(self.current / self.total, 1.0)
        filled_length = int(self.bar_length * progress)
        bar = '#' * filled_length + '-' * (self.bar_length - filled_length)
        percent = int(100 * progress)
        
        sys.stdout.write(f"\r{self.description}: [{bar}] {percent}%")
        sys.stdout.flush()
        
        if self.current >= self.total:
            sys.stdout.write("\n")
            
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.current < self.total:
            self.current = self.total
            self._print_progress()
            
    @classmethod
    def iter(cls, iterable, description="ML Progress", bar_length=40):
        """包装迭代器"""
        total = len(iterable)
        progress = cls(total, description, bar_length)
        for item in iterable:
            yield item
            progress.update()

import sys
import time
from io import StringIO
from unittest import TestCase, main
from mlprogress import MLProgress

class TestMLProgress(TestCase):
    def setUp(self):
        self._saved_stdout = sys.stdout
        sys.stdout = StringIO()
        
    def tearDown(self):
        sys.stdout = self._saved_stdout
        
    def test_basic_progress(self):
        total = 5
        pb = MLProgress(total, "Test")
        
        for i in range(total):
            pb.update()
            output = sys.stdout.getvalue()
            self.assertIn(f"Test: [", output)
            self.assertIn(f"] {int((i+1)/total*100)}%", output)
            
        self.assertTrue(output.endswith("\n"))
        
    def test_context_manager(self):
        total = 3
        with MLProgress(total, "Context Test") as pb:
            for i in range(total):
                pb.update()
                
        output = sys.stdout.getvalue()
        self.assertIn("Context Test: [###", output)
        self.assertIn("] 100%", output)
        
    def test_iterator_wrapper(self):
        items = [1, 2, 3, 4]
        for item in MLProgress.iter(items, "Iter Test"):
            pass
            
        output = sys.stdout.getvalue()
        self.assertIn("Iter Test: [####", output)
        self.assertIn("] 100%", output)
        
    def test_custom_length(self):
        pb = MLProgress(10, "Length Test", bar_length=20)
        pb.update(5)
        output = sys.stdout.getvalue()
        self.assertIn("[##########----------]", output)
        
    def test_description(self):
        pb = MLProgress(1, "Custom Description")
        pb.update()
        output = sys.stdout.getvalue()
        self.assertIn("Custom Description:", output)

if __name__ == "__main__":
    main()

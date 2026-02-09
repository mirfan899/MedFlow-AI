import sys
import os
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from medflow.agents.agent1 import SoapNoteGenerator
from medflow.agents.agent2 import PlanAnalyzer
from medflow.utils.pdf_generator import generate_soap_pdf

class TestMedFlowComponents(unittest.TestCase):
    def test_agent1_instantiation(self):
        mock_pipe = MagicMock()
        agent = SoapNoteGenerator(mock_pipe)
        self.assertIsInstance(agent, SoapNoteGenerator)

    def test_agent2_instantiation(self):
        mock_pipe = MagicMock()
        agent = PlanAnalyzer(mock_pipe)
        self.assertIsInstance(agent, PlanAnalyzer)

    def test_pdf_generator_import(self):
        self.assertTrue(callable(generate_soap_pdf))

if __name__ == '__main__':
    unittest.main()

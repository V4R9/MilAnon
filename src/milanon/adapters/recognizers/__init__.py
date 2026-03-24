"""Entity recognizers — one recognizer per detection strategy."""

from milanon.adapters.recognizers.list_recognizer import ListRecognizer
from milanon.adapters.recognizers.military_recognizer import MilitaryRecognizer
from milanon.adapters.recognizers.pattern_recognizer import PatternRecognizer

__all__ = ["ListRecognizer", "MilitaryRecognizer", "PatternRecognizer"]

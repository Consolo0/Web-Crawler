from src.Enums.ProcessorType import ProcessorType
from src.Error.UnrecognizedProcessorType import UnrecognizedProcessorType
from .HtmlChunkProcessor import HtmlChunkProcessor
from .ProductProcessor import ProductProcessor

class ProcessorFactory:
    def __init__(self):
        self.processors = {}

    def initialize_processor(self, navigation_strategy, sources_rules, navigator, navigator_lock, results, results_lock):
        self.processors = {
            ProcessorType.ProductProcessor.value: ProductProcessor(navigation_strategy, sources_rules, navigator, navigator_lock, results, results_lock),
            ProcessorType.HtmlChunkProcessor.value: HtmlChunkProcessor(navigation_strategy, sources_rules, results, results_lock),
        } 
    def get_processor(self, processor_type):
        if processor_type not in self.processors:
            raise UnrecognizedProcessorType(processor_type)
        
        return self.processors[processor_type]
import sys
from typing import List
from lxml.etree import XPathEvalError
from fastcore.transform import Transform

sys.path.append(".")
from src.spider.app.processors.models import SchemaBlockField, PipelineError


class SelectorProcessor(Transform):
    """Класс обработчика селекторов, таких как xpath или css.
    Идет первым, так как забирает данные из html.

    Args:
        Transform (_type_): _description_
    """

    def encodes(self, x: SchemaBlockField) -> SchemaBlockField | PipelineError:
        """Метод обработки данных, если не возникло ошибок

        Args:
            x (_type_): _description_
        """
        html_doc = x.html_doc
        field_name = x.field_name
        field_processors = x.field_processors
        output_field = x.output_field
        processed_data: List[str] | PipelineError = self.selector_processor_dispatcher(html_doc=html_doc,
                                                            field_processors=field_processors
                                                            )
        match processed_data:
            case list():
                x.output_field[field_name] = processed_data
                return x
            case PipelineError():
                return processed_data
    
    def encodes(self, x: PipelineError):
        """Метод пропускающий обработку при возникновении ошибки в предыдущем обработчике

        Args:
            x (PipelineError): _description_
        """
        return x
    
    def selector_processor_dispatcher(self, html_doc, field_processors: dict) -> List[str] | PipelineError:
        selectors = field_processors.get('selectors')
        if selectors and isinstance(selectors, dict):
            first_selector = list(selectors.keys())[0]
            match first_selector:
                case 'xpath':
                    xpath_selector = selectors['xpath']
                    selected_data = self.process_xpath_field(html_doc=html_doc, xpath_selector=xpath_selector)
                    return selected_data
                case 'css':
                    css_selector = selectors['css']
                    selected_data = self.process_css_field(html_doc=html_doc, css_selector=css_selector)
                    return selected_data
                case _:
                    return PipelineError("No valid selector is specified")
        else:
            return PipelineError("No selector is specified")
    
    @staticmethod
    def process_xpath_field(html_doc, xpath_selector: str) -> List[str] | PipelineError:
        """
        :param html_doc:
        :param field_selector:
        :return:
        """
        try:
            parsed_data = html_doc.xpath(xpath_selector)
        except XPathEvalError:
            parsed_data = PipelineError("Not valid xpath evaluation")
        return parsed_data

    @staticmethod
    def process_css_field(html_doc, css_selector: str) -> List[str]:
        pass

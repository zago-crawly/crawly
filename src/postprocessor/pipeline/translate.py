import sys
import requests
from fastcore.transform import Transform  
import json

sys.path.append('.')
from src.postprocessor.pipeline.models import PipelineError, SchemaBlockField

class Translate(Transform):
    
    def encodes(self, x: SchemaBlockField) -> SchemaBlockField | PipelineError:
        
        postprocessors = x.field_processors.get('postprocessors', '')
        constraints = x.field_processors.get('constraints', '')
        
        if postprocessors and constraints:
            max_length = int(constraints.get('max_length'))
            source_lang = postprocessors.get('source_lang')
            target_lang = postprocessors.get('target_lang')
            parsed_field_data = x.output_field[x.field_name]
        
            if int(max_length) > 1000:
                return PipelineError('Text is too big for translator. Max length is 1000 chars')
            if source_lang and target_lang:
                response = requests.post(
                    # url=f"http://{os.environ.get('TRANSLATOR_SERVER')}:{os.environ.get('TRANSLATOR_PORT')}/translate",
                    url="http://87.249.44.229:5000/translate",
                    data=
                        json.dumps({
                        'q': parsed_field_data,
                        'source': source_lang,
                        'target': target_lang
                        }),
                    headers={ "Content-Type": "application/json" }
                )
                translated_text = response.json()['translatedText']
                x.output_field[x.field_name] = translated_text
                return x
        return x

    def encodes(self, x: PipelineError):
        """Метод пропускающий обработку при возникновении ошибки в предыдущем обработчике

        Args:
            x (PipelineError): _description_
        """
        return x
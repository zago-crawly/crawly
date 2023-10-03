import geopy
import sys
from geopy.exc import GeocoderServiceError
from fastcore.transform import Transform

sys.path.append('.')
from src.postprocessor.pipeline.models import PipelineError, SchemaBlockField


class Geocode(Transform):
    
    def __init__(self, enc=None, dec=None, split_idx=None, order=None):
        super().__init__(enc, dec, split_idx, order)
        self.geocoder = geopy.geocoders.Nominatim(user_agent='html')
    
    def encodes(self, x: SchemaBlockField) -> SchemaBlockField | PipelineError:
        postprocessors = x.field_processors.get('postprocessors')
        if postprocessors:
            geocode_flag = postprocessors.get("geocode", False)
            if geocode_flag:
                locations = x.output_field[x.field_name]
                for loc in locations:
                    output_locations = []
                    try:
                        location = self.geocoder.geocode(loc)
                        if location:
                            result = {}
                            result['latitude'] = location.latitude
                            result['longitude'] = location.longitude
                            output_locations.append(result)
                    except GeocoderServiceError:
                        return PipelineError("Error while trying to geocode location")
                x.output_field[x.field_name] = output_locations
        return x
        
        
    def encodes(self, x: PipelineError):
        """Метод пропускающий обработку при возникновении ошибки в предыдущем обработчике

        Args:
            x (PipelineError): _description_
        """
        return x


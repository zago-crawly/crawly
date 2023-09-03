import sys
import pytz
from fastcore.transform import Transform
from datetime import datetime, timezone as tz

sys.path.append('.')
from src.spider.app.processors.models import PipelineError, SchemaBlockField


class TimeProcessor(Transform): # ToDo make this processor more concise
    
    def encodes(self, x: SchemaBlockField) -> SchemaBlockField | PipelineError:
        field_name = x.field_name
        output_field = x.output_field
        postprocessors = x.field_processors.get('postprocessors')
        parsed_field_data = output_field[field_name]
        
        if postprocessors and isinstance(parsed_field_data, str):
            initial_date_format = postprocessors.get('initial_date_format')
            new_date_format = postprocessors.get('new_date_format')
            if initial_date_format and new_date_format:
                try:
                    converted_data = self.convert_date_format(parsed_field_data, initial_date_format, new_date_format)
                    x.output_field[x.field_name] = converted_data
                    return x
                except ValueError:
                    return PipelineError("Error converting date")
            else: return x
        else: return x
                        

    def encodes(self, x: PipelineError):
        """Метод пропускающий обработку при возникновении ошибки в предыдущем обработчике

        Args:
            x (PipelineError): _description_
        """
        return x

    def convert_date_format(self, date_str, current_format, target_format):
        # Create a datetime object from the input string and current format
        date_obj = datetime.strptime(date_str, current_format)
        # Convert the datetime object to a new string using the target format
        new_date_str = date_obj.strftime(target_format)
        return new_date_str

    @staticmethod
    def locale_str_to_unix(timestr: str, format: str, timezone: str):
        try:
            datetime_obj = datetime.strptime(timestr, format)
            timezone_obj = pytz.timezone(timezone)
            localized_time = timezone_obj.localize(datetime_obj)
            utc_time = localized_time.astimezone(pytz.UTC)
            epoch = datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
            return int((utc_time - epoch).total_seconds())
        except BaseException: # ToDo handle exceptions more clearly
            return PipelineError("Date formating failed")

    @staticmethod
    def unix_to_locale_str(unix: int, format: str, timezone: str):
        if unix:
            utc_time = datetime.fromtimestamp(unix, tz=tz.utc)
            timezone_obj = pytz.timezone(timezone)
            localized = utc_time.astimezone(timezone_obj)
            locale_str = datetime.strftime(localized, format)
            return locale_str
        else:
            return None

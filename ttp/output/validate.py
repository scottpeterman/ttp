import logging
import json
log = logging.getLogger(__name__)

try:
    from cerberus import Validator
    HAS_LIBS = True
except ImportError:
    log.error("ttp.validate, failed to import Cerberus library, make sure it is installed")
    HAS_LIBS = False
    
if HAS_LIBS:
    validator_engine = Validator()

def validate(data, add_errors=False, allow_unknown=True, add_fields="", test_info=""):
    if not HAS_LIBS:
        return data
    # get validation schema from output load
    schema_data = _ttp_["output_object"].attributes.get('load')
    if not schema_data:
        log.error("ttp.output.validate: output '{}' no validation schema load found, make sure 'load' attribute specified".format(_ttp_["output_object"].name))
        return data
    # run validation
    validator_engine.allow_unknown = allow_unknown
    if "_anonymous_" in data:
        validation_result = validator_engine.validate(document=data["_anonymous_"], schema=schema_data)   
    else:
        validation_result = validator_engine.validate(document=data, schema=schema_data)  
    # form result
    ret = {
        'valid': validation_result
    }
    if add_errors:
        ret["errors"] = json.dumps(validator_engine.errors, sort_keys=True, separators=(',', ': '))
    if test_info.strip():
        ret["test_info"] = test_info
    # add additional fields
    add_fields = [i.strip() for i in add_fields.split(",")]
    for field_name in add_fields:
        if "_anonymous_" in data:
            if data["_anonymous_"].get(field_name):
                ret[field_name] = data["_anonymous_"][field_name]
                continue
        # continue looking in global variables
        if data.get(field_name):
            ret[field_name] = data[field_name]
        elif field_name in _ttp_["global_vars"]:
            ret[field_name] = _ttp_["global_vars"][field_name]
    return ret
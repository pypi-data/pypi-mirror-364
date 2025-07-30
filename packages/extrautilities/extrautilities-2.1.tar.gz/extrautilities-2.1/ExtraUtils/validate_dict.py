def validate_dict(format:dict, data:dict)->bool:
    for key, rule in format.items():
        if rule.get["__required"] and key not in data:
            print(f"❌  Missing required field {key}. @channel_points.py(validate_dict)")
            return False
        
        if rule.get("__type"):
            tpe = rule.get("__type")
            if not isinstance(data[key], tpe):
                print(f"❌  Invalid type for {key} expecting {tpe}. @channel_points.py(validate_dict)")
                return False
            if isinstance(data[key], dict):
                if not validate_dict(tpe, data[key]):
                    return False
            
        if isinstance(rule.get("__value"), list) and data[key] not in rule.get("__value"):
            print(f"❌  Invalid value for {key} expected to be a value contained in {rule.get('__value')}. @channel_points.py(validate_dict)")
            return False
        
        if rule.get("__range") and (isinstance(data[key], int) or isinstance(data[key], float)):
            min, max = rule.get("__range").split("..")
            min = int(min) if min else -999_999_999.0
            max = int(max) if max else 999_999_999.0
            dig = data[key]
            if isinstance(data[key], int):
                dig = float(data[key])
            if not min <= dig <= max:
                    print(f"❌  Invalid length for {key}. @channel_points.py(validate_dict)\n->length must be between {min} and {max}")
                    return False
            
        if rule.get("__length"):
            min, max = rule.get("__length").split("..")
            min = int(min) if min else -999_999_999
            max = int(max) if max else 999_999_999
            if not isinstance(data[key], dict):
                if not min <= len(data[key]) <= max:
                    print(f"❌  Invalid value for {key}. @channel_points.py(validate_dict)\n->value must be between {min} and {max}")
                    return False
    return True
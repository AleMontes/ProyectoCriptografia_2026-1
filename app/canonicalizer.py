import json

def canonicalize(data_dict):
    """
    Recibe un diccionario y devuelve los bytes canonicalizados listos para firmar
    Reglas:
    - Keys ordenadas alfabéticamente (sort_keys=True) 
    - Sin espacios en blanco (separators=(',', ':')) 
    - Codificación UTF-8 
    """
    
    json_str = json.dumps(
        data_dict,
        sort_keys=True,       
        separators=(',', ':') 
    )
    
    return json_str.encode('utf-8') 
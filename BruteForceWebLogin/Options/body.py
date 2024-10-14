# body.py

# Initial body format
body = "username=value&password=value"

def get_body():
    # Convert the initial body format to a dictionary
    body_dict = {}
    
    # Split the body string into key-value pairs
    pairs = body.split('&')
    for pair in pairs:
        key, value = pair.split('=')
        body_dict[key] = value
        
    return body_dict

from urllib.parse import quote


text_message = 'Dear {1},\nA new lead has been assigned for your location: {2}.\nPlease call the lead for further follow-up.\nRegards,\nWebzotica Business Famous Software Pvt Ltd.'

encoded_message = quote(text_message)

print(encoded_message)
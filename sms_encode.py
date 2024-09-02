from urllib.parse import quote


# text_message = 'Dear ,\nA new lead has been assigned for your location.\nPlease call the lead for further follow-up.\nRegards,\nWebzotica Business Famous Software Pvt Ltd.'
text_message = '''Text Message'''

encoded_message = quote(text_message)

print(encoded_message)
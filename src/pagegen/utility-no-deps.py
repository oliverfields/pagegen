def urlify(string):
	''' Anything wich isn't alphanumeric, - or _ gets replaced with a - '''
	url = string.lower()
	url = sub('[^/a-z0-9-_.]', '-', url)
	# Replace any double dashes
	url = sub('--', '-', url)
	return url


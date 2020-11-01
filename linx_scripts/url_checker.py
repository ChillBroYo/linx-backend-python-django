#Script to check that image can be accessed through S3 link

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

#Indicate the index of the last image uploaded to S3
image_index = 203

for i in range(image_index + 1):
	if i % 25 == 0 and i != 0:
		print(i, 'images checked')
		
	url = 'https://linx-images.s3.us-west-2.amazonaws.com/g' + str(i) + '.png'
	
	session = requests.Session()
	retry = Retry(connect=3, backoff_factor=0.5)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)

	header = session.head(url).headers

	#Triggered if PNG image could not be accessed
	if 'image/png' not in header.get('Content-Type'):
		print('Issue with image URL: ', url)

print('URL checker has finished')
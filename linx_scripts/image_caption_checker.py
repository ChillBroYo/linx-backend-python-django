#Script to check image captions through API endpoint

import requests

#Indicate the index of the last image uploaded to S3
image_index = 203

for i in range(image_index + 1):
	if i % 25 == 0 and i != 0:
		print(i, 'images checked')

	url = 'https://api.linx-services.com/get-image?image_type=general&image_index=' + str(i)
	response = requests.get(url)

	#Triggered if endpoint cannot be accessed
	if response.status_code != 200:
		print('Issue with API call: ', url)
		continue

	message = response.json()['message']

	#Triggered if image does not have a caption
	if not message.strip():
		print('Issue with image text: ', url)

print('Image caption checker has finished')
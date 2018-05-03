import requests
import boto3
from app.application import app


def get_auth0_mgmt_api_token():
	"""
	Returns a brand new API access token for the auth0 management API
	"""
	try:
		url = "https://bigfirmadvisors.auth0.com/oauth/token"
		r = requests.post(url,
				json={"grant_type":"client_credentials",
					  "client_id": app.config['MGMT_API_CLIENT_ID'],
					  "client_secret": app.config['MGMT_API_CLIENT_SECRET'],
					  "audience": app.config['MGMT_API_AUDIENCE']})

		r_json = r.json()
		return r_json.get('access_token')
	except:
		return None


def get_auth0_user_profile_from_token(access_token):
	"""
	Takes an access token that is given to the user after login
	and returns the user profile from that token.
	Note: only works if that token was granted the "open_id" scope.
	"""
	try:
		url = "https://bigfirmadvisors.auth0.com/userinfo"
		headers = {'Authorization': str("Bearer " + access_token)}
		r = requests.get(url, headers=headers)
		r_json = r.json()
		return r_json
	except:
		return None

def send_password_email(user_email, default_password):
	"""
	Send the given password to the given user_email
	"""

	e_subject = 'Your Big Firm Advisors Default Password'
	e_body = "Hello and welcome to Big Firm Advisors!\n\n\nYour new account is ready " + \
		"for you, and you can log in with the following temporary password: " + default_password + \
		"\n\nThis is just a temporary default password, so be sure to change it to something" + \
		" more secure in Account Settings. \n\n\nRegards, \nBig Firm Advisors"
	ses = boto3.client('ses',
					   aws_access_key_id = app.config['AWS_ACCESS_KEY_ID'],
					   aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
					   region_name=app.config['AWS_REGION_NAME'])
	ses.send_email(Source=app.config['AWS_SES_SOURCE_EMAIL'], # should be the SES email designated for sending emails
				   Message={
								'Subject': {
									'Charset': 'UTF-8',
									'Data': e_subject
								},
								'Body': {
									'Text': {
										'Charset': 'UTF-8',
										'Data': e_body
									}
								}
							},
				   Destination={
								   'ToAddresses': [user_email] # the email address of the user
							   },
				   ReplyToAddresses=[app.config['AWS_SES_TARGET_EMAIL']]) # technically this should be a noreply address

def send_welcome_email(user_email, welcome_message):
	"""
	Send the welcome message to the given user_email
	"""

	e_subject = 'Welcome to Big Firm Advisors!'
	e_body = welcome_message
	ses = boto3.client('ses',
					   aws_access_key_id = app.config['AWS_ACCESS_KEY_ID'],
					   aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
					   region_name=app.config['AWS_REGION_NAME'])
	ses.send_email(Source=app.config['AWS_SES_SOURCE_EMAIL'], # should be the SES email designated for sending emails
				   Message={
								'Subject': {
									'Charset': 'UTF-8',
									'Data': e_subject
								},
								'Body': {
									'Text': {
										'Charset': 'UTF-8',
										'Data': e_body
									}
								}
							},
				   Destination={
								   'ToAddresses': [user_email] # the email address of the user
							   },
				   ReplyToAddresses=[app.config['AWS_SES_TARGET_EMAIL']]) # technically this should be a noreply address

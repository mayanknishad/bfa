import requests

def get_access_token():
    """
    Gets access token for API testing
    """

    url = "https://bigfirmadvisors.auth0.com/oauth/token"
    r = requests.post(url, \
            json={"grant_type":"client_credentials",
                  "client_id": "SjsSCo3x1r9YguHMeYZbKaHw4Q8hiPVg",
                  "client_secret": "Y3TL8fhIqnjrAfDwdwbytjjKQhmqL-veV0mc0o1-4uDvdXt7DTioNUBmthjx8VVM",
                  "audience": "bfa-restricted-api"})
    r_json = r.json()
    return r_json.get('access_token')

if __name__ == '__main__':
    print("New Access Token for API: " + str(get_access_token()))

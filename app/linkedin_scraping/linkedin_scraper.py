# make sure to use python3, as the linkedin library is python3

from linkedin import linkedin
import csv

LINKEDIN_RETURN_URL = "http://127.0.0.1:5000/api/consultant/linkedin/"

class BFALinkedInScraper:

    def __init__(self, client_id, client_secret):
        self.application = self.setup_linkedin_application(client_id, client_secret)
        # /home/samarth/bigfirmadvisors-backend/app/linkedin_scraping/template_LI.csv

    def setup_linkedin_application(self, linkedin_client_id, linkedin_client_secret):
        """
        Sets up and returns a new LinkedInApplication that can be used to get data.
        Ensure that the LinkedIn app dashboard for the given client ID and client secret have
        the LINKEDIN_RETURN_URL at the top of this file in the 'Authorized Redurect URLs'
        """
        authentication = linkedin.LinkedInAuthentication(linkedin_client_id, linkedin_client_secret, LINKEDIN_RETURN_URL, \
            permissions=['r_basicprofile', \
                         'r_emailaddress', \
                         'rw_company_admin', \
                         'w_share'])
        print("Open this URL in your browser and give permissions if necessary: "  + authentication.authorization_url)  # open this url on your browser
        authentication.authorization_code = input("After you are redirected, copy the entire URL from your address bar and enter it here: ").replace(LINKEDIN_RETURN_URL + "?code=", "").split("&state=")[0]
        print("\n\n Your authorization code is: " + authentication.authorization_code)
        result = authentication.get_access_token()

        print ("Your new Access Token:", result.access_token)
        print ("Access Token Expires in (seconds):", result.expires_in)

        return linkedin.LinkedInApplication(authentication)

    def get_profile(self):
        return self.application.get_profile()


def csv_scraper(csv_path):
    """
    Takes a path to a CSV file containing two columns: linkedin_url and connected_through

    For each LinkedIn URL the CSV will specify the name of the BFA admin that is
    connected to the person at the URL.

    This function scrapes the CSV and returns a dictionary that has the
    BFA admin name as the key, and the list of LinkedIn URLs they are connected to as the value.
    """

    with open(csv_path) as csv_file:
        next(csv_file) # skip first line
        read_csv = csv.reader(csv_file, delimiter=",")

        connection_dictionary = {}
        for row in read_csv:
            if len(row) != 2:
                raise Exception('Found a row that did not have 2 columns: ' + str(row))
            linkedin_url = row[0]
            bfa_admin = row[1]

            # check if this bfa_admin is already a key in the dictionary
            if connection_dictionary.get(bfa_admin, None) is None:
                connection_dictionary[bfa_admin] = [linkedin_url] # put a new pair
            else:
                connection_dictionary[bfa_admin] += [linkedin_url] # append this URL to the list
        return connection_dictionary

def main():
    # connection_dictionary = csv_scraper(input('Please enter the absolute path of the CSV file you want to scrape:'))

    rambo_scraper = BFALinkedInScraper("78yhypxx44ebcs", "BFRwM01S69T9Wy4l")

    print("Rambo Profile: " + str(rambo_scraper.get_profile()))
    # print("Rambo Connections: " + str(rambo_scraper.get_connections()))

    # for bfa_admin in connection_dictionary:
    #     # get the bfa admin's name and login

if __name__ == '__main__':
    main()

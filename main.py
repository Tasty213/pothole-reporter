import json
from gov_form import GovForm

if __name__ == "__main__":
    with open("pothole_form.json", "r") as file:
        pothole_form = json.load(file)
    pothole_form = GovForm(pothole_form)
    print(pothole_form.submission_id)
    print(pothole_form.cfd_token)

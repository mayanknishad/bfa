"""
Imports BFA CSV data
"""

from pprint import pprint

from app.application import app

from sqlalchemy.sql.expression import and_

from app.models import (
    Advisor,
    Specialty,
    Subspecialty,
    BigFirm,
    Occupation,
    db,
    YearsOfExperienceRange
)


EXP_RANGE_TO_ENUM = {
    '': YearsOfExperienceRange.LEVEL0,
    '1-2': YearsOfExperienceRange.LEVEL1,
    '3-5': YearsOfExperienceRange.LEVEL2,
    '6-10': YearsOfExperienceRange.LEVEL3,
    '11-20': YearsOfExperienceRange.LEVEL4,
    '21+': YearsOfExperienceRange.LEVEL5,
    '30+': YearsOfExperienceRange.LEVEL6
}

IGNORE_CASES = {'not mentioned in linkedin'}

OCCUPATIONS = {
    'Attorney': {
        'Antitrust & Competition',
        'Appellate',
        'Commercial Litigation',
        'Corporate/M&A',
        'Banking/FinTech',
        'Bankruptcy & Workouts',
        'Bankruptcy Litigation',
        'Criminal Defense & Investigations',
        'Environment, Land & Resources',
        'Estate Planning',
        'Executive Compensation & Benefits',
        'Family Law',
        'Financial Regulatory',
        'Healthcare & Life Sciences',
        'Immigration',
        'Information Law, Data Privacy & Cybersecurity',
        'Insurance Litigation',
        'Intellectual Property Litigation',
        'Intellectual Property Transactions',
        'International Arbitration',
        'Labor & Employment',
        'Labor & Employment Litigation',
        'Media & Entertainment Litigation',
        'Media & Entertainment Transactions',
        'Oil & Gas Transactions',
        'Personal Injury',
        'Product Liability, Mass Torts & Consumer Class Actions',
        'Project Finance',
        'Public Company Representation',
        'Public & Tax-Exempt Finance',
        'Real Estate',
        'Securities',
        'Securities Litigation',
        'Start-Ups & Venture Capital',
        'Structured Finance',
        'Tax',
        'Technology Transactions'
    },
    'Accountant': {
        'Advisory',
        'Audit',
        'Tax',
        'Other'
    },
    'Management Consultant': {
        'Aerospace',
        'Banking & Capital Markets',
        'Biotechnology',
        'Chemicals',
        'Consumer Goods',
        'Education',
        'Healthcare',
        'Industrials',
        'Media/Telecom',
        'Metals',
        'Non-Profit',
        'Oil and Energy',
        'Other',
        'Pharmaceutical',
        'Private Equity',
        'Public Sector',
        'Real Estate',
        'Retail',
        'Technology',
        'Travel & Hospitality',
        'Financial Services'
    },
    'Investment Banker/Financial Advisor': {
        'Equity Research',
        'Fixed Income',
        'Investment Banking',
        'Other',
        'Sales & Trading',
    },
    'Entrepreneur': {
        'Aerospace',
        'Banking & Capital Markets',
        'Biotechnology',
        'Chemicals',
        'Consumer Goods',
        'Education',
        'Healthcare',
        'Industrials',
        'Media/Telecom',
        'Metals',
        'Non-Profit',
        'Oil and Energy',
        'Other',
        'Pharmaceutical',
        'Private Equity',
        'Public Sector',
        'Real Estate',
        'Retail',
        'Technology',
        'Travel & Hospitality',
        'Financial Services'
    }
}

ABBR_TO_STATE = {
    'AK': 'Alaska',
    'AL': 'Alabama',
    'AR': 'Arkansas',
    'AZ': 'Arizona',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'HI': 'Hawaii',
    'IA': 'Iowa',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'MA': 'Massachusetts',
    'MD': 'Maryland',
    'ME': 'Maine',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MO': 'Missouri',
    'MS': 'Mississippi',
    'MT': 'Montana',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'NE': 'Nebraska',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NV': 'Nevada',
    'NY': 'New York',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VA': 'Virginia',
    'VT': 'Vermont',
    'WA': 'Washington',
    'WI': 'Wisconsin',
    'WV': 'West Virginia',
    'WY': 'Wyoming'
}


def read_advisor_tsv(file_path):
    """
    Loads CSV data into dictionary
    :param file_path: file to read (str)
    :return: objects (dict)
    """
    advisor_data = []

    f = open(file_path, 'r')

    f.readline()

    for row in f:
        data = row.rstrip('\n').split('\t')

        if len(data) == 19:
            data.pop()

        for i, field in enumerate(data):
            if field.strip().lower() in IGNORE_CASES:
                data[i] = ''

        _, first_name, last_name, email, linkedin_url, occupation, specialties, subspecialties, \
            prev_big_firms, bf_yrs_exp, total_yrs_exp, current_bf, current_location, ug_school, \
            grad_school, brief_bio, index, ghulam_reviewed = data

        advisor_data.append({
            'first_name': first_name.strip(),
            'last_name': last_name.strip(),
            'email': email.strip(),
            'linkedin_url': linkedin_url.strip(),
            'occupations': occupation.strip(),
            'specialties': specialties.strip(),
            'subspecialties': subspecialties.strip(),
            'previous_firms': prev_big_firms.strip(),
            'current_firm_name': current_bf.strip(),
            'years_of_bigfirm_experience_range': EXP_RANGE_TO_ENUM[bf_yrs_exp.strip()],
            'years_of_experience_range': EXP_RANGE_TO_ENUM[total_yrs_exp.strip()],
            'location': current_location.strip(),
            'undergrad_education': ug_school.strip(),
            'grad_education': grad_school.strip(),
            'biography': brief_bio.strip()
        })

    return advisor_data


def validate(success, result):
    if not success:
        print(result)
        exit(-1)


def create_occupations():
    """
    Creates occupations from given hardcoded mapping
    :return: None
    """
    for occupation_name, specialties in OCCUPATIONS.items():
        success, result = create_occupation({'name': occupation_name})

        validate(success, result)

        occupation = result

        for specialty_name in specialties:
            success, result = create_specialty({
                'name': specialty_name,
                'occupation_id': occupation.pk_id,
                'occupation': occupation
            })

            validate(success, result)

            specialty = result
            occupation.specialties.append(specialty)


def create_advisors(_advisors_data):
    """
    Creates advisor objects and commits to db
    :param _advisors_data: advisor data (dict)
    :return: None
    """

    for advisor_data in _advisors_data:
        occupations = advisor_data.pop('occupations', '').strip()
        specialties = advisor_data.pop('specialties', '').strip()
        subspecialties = advisor_data.pop('subspecialties', '').strip()
        prev_firms = advisor_data.pop('previous_firms', '').strip()
        curr_firm_name = advisor_data.pop('current_firm_name', '').strip()
        location = advisor_data.pop('location', '').strip()

        city, state_abbr = location.split(', ') if location.count(',') == 1 else (None, '')

        advisor_data['city'] = city
        advisor_data['state'] = ABBR_TO_STATE.get(state_abbr, 'Other')

        advisor_data['status'] = 'Active'

        success, result = create_advisor(advisor_data)
        validate(success, result)

        advisor = result

        occupation_objs = []

        if occupations:
            for occupation_name in occupations.split(', '):
                if occupation_name not in OCCUPATIONS:
                    continue

                success, result = create_occupation({'name': occupation_name.strip().title()})
                validate(success, result)

                occupation = result
                occupation_objs.append(occupation)

                advisor.occupations.append(occupation)

            db.session.commit()

        if specialties:
            for specialty_name in specialties.split(', '):

                spec_occ = None
                for occupation in occupation_objs:
                    if specialty_name in OCCUPATIONS[occupation.name]:
                        spec_occ = occupation
                        break

                if not spec_occ:
                    continue

                success, result = create_specialty({
                    'name': specialty_name.strip().title(),
                    'occupation_id': spec_occ.pk_id,
                    'occupation': spec_occ
                })

                validate(success, result)

                specialty = result
                advisor.specialties.append(specialty)

            db.session.commit()

        if subspecialties:
            advisor.subspecialty_text = subspecialties

            db.session.commit()

        if prev_firms:
            for prev_firm_name in prev_firms.split(', '):
                success, result = create_bigfirm({'name': prev_firm_name.strip()})
                validate(success, result)

                big_firm = result
                advisor.previous_firms.append(big_firm)

            db.session.commit()

        if curr_firm_name:
            success, result = create_bigfirm({'name': curr_firm_name.strip()})
            validate(success, result)

            big_firm = result
            advisor.current_firm = big_firm
            advisor.current_firm_id = big_firm.pk_id

            db.session.commit()

        db.session.commit()


def get_or_create_object(data, cls):
    """
    Creates object based on class
    :param data: data to fill object with (dict)
    :param cls: class of object to create  (object)
    :return: created_or_exists (bool), obj (object)
    """
    if 'name' not in data:
        return False, 'No name in {} data {}'.format(cls.__name__, data)

    filters = []
    for field, value in data.items():
        filters.append(eval('{}.{}'.format(cls.__name__, field)) == value)

    old_obj = cls.query.filter(and_(*filters)).first()

    if old_obj:
        print('Found {}: {} - {}'.format(cls.__name__, old_obj, old_obj.pk_id))

        return True, old_obj

    obj = cls(**data)
    db.session.add(obj)
    db.session.commit()

    print('Created {}: {} - {}'.format(cls.__name__, obj, obj.pk_id))

    return True, obj


def create_advisor(adv_data):
    """
    Creates one advisor and commits to db
    :param adv_data: advisor data (dict)
    :return: created (bool), obj (object)
    """
    if 'email' not in adv_data:
        return False, 'No email in advisor data {}'.format(adv_data)

    old_advisor = Advisor.query.filter_by(email=adv_data.get('email')).first()

    if old_advisor:
        print('Found Advisor: {}'.format(old_advisor))

        return True, old_advisor

    # pprint(adv_data)

    advisor = Advisor(**adv_data)
    db.session.add(advisor)
    db.session.commit()

    print('Created Advisor: {}'.format(advisor))

    return True, advisor


def create_occupation(occ_data):
    """
    Creates occupation object and commits to db
    :param occ_data: occupation data (dict)
    :return: created (bool), obj (object)
    """
    return get_or_create_object(occ_data, Occupation)


def create_specialty(spec_data):
    """
    Creates specialty object and commits to db
    :param spec_data: specialty data (dict)
    :return: created (bool), obj (object)
    """
    return get_or_create_object(spec_data, Specialty)


def create_subspecialty(sub_data):
    """
    Creates one subspecialty and commits to db
    :param sub_data: subspecialty data (dict)
    :return: created (bool), obj (object)
    """
    return get_or_create_object(sub_data, Subspecialty)


def create_bigfirm(bf_data):
    """
    Creates big firm object and commits to db
    :param bf_data: big firm data (dict)
    :return: created (bool), obj (object)
    """
    return get_or_create_object(bf_data, BigFirm)


if __name__ == '__main__':
    advisors_data = read_advisor_tsv('./advisor-data.tsv')

    with app.app_context():
        create_occupations()
        create_advisors(advisors_data)

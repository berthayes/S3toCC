# This script reads a CSV file from http://fakenamegenerator.com
# and turns each row of CSV into a JSON object
# JSON object is then written to a directory and/or an S3 bucket

import csv
import json
from collections import namedtuple
import time
import boto3
import logging
from botocore.exceptions import ClientError

csv_file = '10_fake_names.csv'
#csv_file = 'fake_names.csv'



def upload_file(file_name, bucket, object_name):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


# csv_file = cfg.get(my_db_name, 'input_file')
with open(csv_file, 'r', encoding='utf-8-sig') as f:
    f_csv = csv.reader(f)
    headings = next(f_csv)
    Row = namedtuple('Row', headings)

    for r in f_csv:
        row = Row(*r)
        user_info = {
            'Number': row.Number,
            'Gender': row.Gender,
            'NameSet': row.NameSet,
            'Title': row.Title,
            'GivenName': row.GivenName,
            'MiddleInitial': row.MiddleInitial,
            'Surname': row.Surname,
            'StreetAddress': row.StreetAddress,
            'City': row.City,
            'State': row.State,
            'StateFull': row.StateFull,
            'ZipCode': row.ZipCode,
            'Country': row.Country,
            'CountryFull': row.CountryFull,
            'EmailAddress': row.EmailAddress,
            'Username': row.Username,
            'Password': row.Password,
            'BrowserUserAgent': str(row.BrowserUserAgent),
            'TelephoneNumber': row.TelephoneNumber,
            'TelephoneCountryCode': row.TelephoneCountryCode,
            'MothersMaiden': row.MothersMaiden,
            'Birthday': row.Birthday,
            'Age': row.Age,
            'TropicalZodiac': row.TropicalZodiac,
            'CCType': row.CCType,
            'CCNumber': row.CCNumber,
            'CVV2': row.CVV2,
            'CCExpires': row.CCExpires,
            'NationalID': row.NationalID,
            'UPS': row.UPS,
            'WesternUnionMTCN': row.WesternUnionMTCN,
            'MoneyGramMTCN': row.MoneyGramMTCN,
            'Color': row.Color,
            'Occupation': row.Occupation,
            'Company': row.Company,
            'Vehicle': row.Vehicle,
            'Domain': row.Domain,
            'BloodType': row.BloodType,
            'Pounds': row.Pounds,
            'Kilograms': row.Kilograms,
            'FeetInches': row.FeetInches,
            'Centimeters': row.Centimeters,
            'GUID': row.GUID,
            'Latitude': row.Latitude,
            'Longitude': row.Longitude
        }
        # print(json.dumps(user_info))
        filename = row.GivenName + "." + row.Surname + "." + str(time.time()) + ".json"
        jsonFilePath = "./json_files/" + filename
        with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
            jsonf.write(json.dumps(user_info, indent=4))

        # TODO: make these S3 parameters come from a conf file
        if upload_file(jsonFilePath, 'bhayes-chuckbucket', 'json_files/{}'.format(filename)):
            print("File is uploaded")
        else:
            print("problem")
        # time.sleep(.5)

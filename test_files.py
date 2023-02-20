import os, logging, sys
import pytest
import glob
import pandas as pd
import mrf
from pandas.testing import assert_frame_equal

# This test script runs any *.json files in the project's /test/ directory
# and compares the resulting CSV with a matching *.valid CSV file

# @pytest.fixture(scope="session")
def inputfiles():
    filelist = []
    for file in glob.glob('*'):
        if file[-5:] == '.json':
            filelist.append(file)
            logging.info(f'Added {file} to test list')

    return filelist

@pytest.mark.parametrize("inputfile", inputfiles())
def test_files(subtests, inputfile):
    with subtests.test(f'Testing {inputfile}'):
        outputfile = inputfile[:-5] + '.csv' 
        if os.path.basename(inputfile)[:6] == 'simple':
            logging.info(f'Processing simple file: {inputfile}')
            mrf.parse_simple(inputfile, outputfile)
        else:
            logging.info(f'Processing real file: {inputfile}')
            mrf.parse(inputfile, outputfile) # bcbstn.json, bcbstn.csv

        df_test = pd.read_csv(outputfile)
        df_test.sort_values(by=['npi', "code", "place_of_service_code", "rate"], inplace=True, ignore_index=True)

        validfile = inputfile[:-5] + '.valid'
        df_valid = pd.read_csv(validfile)
        df_valid.sort_values(by=['npi', "code", "place_of_service_code", "rate"], inplace=True, ignore_index=True)


        logging.info(f'Test file: {len(df_test)}  Valid file: {len(df_test)}')
        assert_frame_equal(df_valid, df_test)


import os, logging
import time
import click
import json
import pandas as pd

__author__ = "Paul Boal"
__email__ = "boalpe@slu.edu"

#
#TODO: Here or in other .py files, you need to add your own code to parse the JSON files
#      This is a very simple function for parsing a much simpler JSON input file.
#      There are many ways I could do this, but I've decided to show it using basic
#      Python features rather than Pandas or another library because Pandads's support
#      for JSON won't be sufficient for our real files.
#
def parse(inputfile, outputfile=None):
    return parse_simple(inputfile, outputfile)

# This is a simple parser used for a much simpler test file

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% MY FUNCTION - 01
def extract_cross_from_dictionary(data, column_name_dict):
    final_result = pd.DataFrame()
    for i in range(len(data)):
        record = data.loc[i:i].reset_index(drop=True)
        try:
            column_data = pd.DataFrame(record.loc[0, column_name_dict])
        except:
            column_data = pd.DataFrame([record.loc[0, column_name_dict]])

        record = record.drop([column_name_dict], axis=1)
        result = record.merge(column_data, how='cross')
        final_result = pd.concat([final_result, result]).reset_index(drop=True)
    return final_result

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% MY FUNCTION - 02
def extract_cross_from_list(data, column_name_list):
    final_result = pd.DataFrame()
    for i in range(len(data)):
        record = data.loc[i:i].reset_index(drop=True)
        value = record.loc[0, column_name_list]
        if isinstance(value, list):
            if len(value) > 1:
                for val in value:
                    record.loc[0, column_name_list] = val  # storing value in 'place_of_service_code'
                    final_result = pd.concat([final_result, record]).reset_index(drop=True)
            else:
                record.loc[0, column_name_list] = value[0]
                final_result = pd.concat([final_result, record]).reset_index(drop=True)
        else:
            final_result = pd.concat([final_result, record]).reset_index(drop=True)
    return final_result

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% BUILT IN FUNCTION
def parse_simple(inputfile, outputfile=None):
    """This function both writes to an output file and returns a dataframe
       with the information. That will make testing easier."""
    data_dict = json.load(open(inputfile))
    original_data = pd.DataFrame.from_dict(data_dict)

    # Extracting ---------------------------------------- column: provider_references
    # ==============================================================================
    data_col4 = original_data[["reporting_entity_name", "provider_references"]]
    column_name_dict = "provider_references"
    data_col4 = extract_cross_from_dictionary(data_col4, column_name_dict)
    column_name_dict = "provider_groups"
    data_col4 = extract_cross_from_dictionary(data_col4, column_name_dict)
    column_name_list = "npi"
    data_col4 = extract_cross_from_list(data_col4, column_name_list)

    data_col4 = data_col4[['reporting_entity_name', 'provider_group_id', 'npi']]

    # Extracting ---------------------------------------- column: in_network
    # ==============================================================================
    data_col5 = original_data[["in_network"]]

    column_name_dict = "in_network"
    data_col5 = extract_cross_from_dictionary(data_col5, column_name_dict)

    column_name_dict = "negotiated_rates"
    data_col5 = extract_cross_from_dictionary(data_col5, column_name_dict)

    column_name_dict = "negotiated_prices"
    data_col5 = extract_cross_from_dictionary(data_col5, column_name_dict)

    column_name_list = "service_code"
    data_col5 = extract_cross_from_list(data_col5, column_name_list)
    column_name_list = "billing_code_modifier"
    data_col5 = extract_cross_from_list(data_col5, column_name_list)

    data_col5 = data_col5.drop_duplicates(ignore_index=True)

    data_col5 = data_col5.drop("expiration_date", axis=1)

    columns_map = {'negotiation_arrangement': "negotiation_arrangement",
                   'billing_code_type': "code_type",
                   'billing_code': "code",
                   'provider_references': "provider_group_id",
                   'negotiated_type': "negotiated_type",
                   'negotiated_rate': "rate",
                   'service_code': "place_of_service_code",
                   'billing_class': "billing_class",
                   'billing_code_modifier': "modifier"
                   }

    data_col5 = data_col5.rename(columns=columns_map)

    # Merging ---------------------------------------- Extracted Columns: provider_references & in_network
    # ====================================================================================================
    final_data = pd.merge(data_col4, data_col5, on="provider_group_id", how="inner")

    required_columns = ['reporting_entity_name', 'npi', 'negotiation_arrangement', 'code_type', 'code', 'modifier',
                        'negotiated_type', 'billing_class', 'place_of_service_code', 'rate', 'provider_group_id']
    final_data = final_data[required_columns]

    columns_map = {'reporting_entity_name': "payer",
                   "negotiation_arrangement": "negotiated_arrangement",
                   }
    df = final_data.rename(columns=columns_map)

    df["npi"] = df["npi"].astype(int)
    df["place_of_service_code"] = df["place_of_service_code"].astype(int)
    df["rate"] = df["rate"].astype(float)

    df = df.sort_values(['npi', "code", "place_of_service_code", "rate"]).reset_index(drop=True)

    """# I know the data I'm looking for: name, type, breed
    # Other data I might encounter, I'll ignore.
    output = []
    for item in data:
        name = item.get('name')
        type = item.get('type')
        breed = item.get('breed')
        output.append([name,type,breed])

    df = pd.DataFrame(output, columns=['name','type','breed'])"""

    if outputfile is not None:
        df.to_csv(outputfile, index=False)

    return df


@click.command()
@click.argument('filename', type=click.Path(exists=True, dir_okay=False))
@click.option('--loglevel', type=click.Choice(['ERROR','WARNING','INFO','DEBUG','NOTSET']), 
                            default='INFO', help='Set logging level')
def run(filename, loglevel):

    logger = logging.getLogger()
    logger.setLevel(loglevel)

    start_ts = time.perf_counter()
    logger.debug(f'Running in DEBUG')
    logger.info(f'Processing file: {filename}')

    #
    #TODO: Here, you need to call your functions to parse the JSON, 
    #      create the right output format, and write that to a CSV file
    #
    fileName = filename.split(".")
    if fileName[1] == 'json':
        outputfile = fileName[0] + '.csv'
        df = parse(filename, outputfile)

    runtime_sec = int(time.perf_counter() - start_ts)
    logger.info(f'Runtime: {runtime_sec} sec')

    return df



if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s():%(lineno)d - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    run()


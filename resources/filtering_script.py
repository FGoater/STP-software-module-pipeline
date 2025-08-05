# importing modules
import pandas as pd
import logging
import re
import sys
import os

# set input values from command line
# inputs: input vcf, output vcf name, vaf threshold
try:
    input_vcf = sys.argv[1]
    output_vcf_file = sys.argv[2]
    vaf_threshold = float(sys.argv[3])
    log_file = sys.argv[4]
except IndexError:
    print("Incorrect number of command arguments entered, please try again.")
    sys.exit(1)
except ValueError:
    print("Vaf_threshold must be a number, please try again")
    sys.exit(1)


# Create and configure logger
logging.basicConfig(filename= log_file,
                    format="%(asctime)s %(levelname)s %(message)s",
                    filemode="w")
# Creating an object
logger = logging.getLogger()
#stream handler

stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
# Sets the logger threshold 
logger.setLevel(logging.DEBUG)

class InputError(Exception):
    """Custom error for errors related to inputs placed into the software"""
    pass

class VCFError(InputError):
    """Custom error for issues with the inputted vcf file"""
    pass




def check_inputs(input_vcf, output_vcf_file_name, vaf_threshold, log_file):
    """ Run prior the the rest of the script to ensure that the 
    inputted values form the run command are appropriate."""
    try:
        # output_vcf_name. Check the name is appropriate
        # check that the input is a string
        if type(output_vcf_file_name) != str:
            raise InputError("output file name is not a string, please correct.")
        # check that it is a vcf file
        
        elif output_vcf_file_name[-4:] != ".vcf":
            raise InputError("Output file name must be a .vcf file")
        
        # log_file name checks
        if type(log_file) != str:
            raise InputError("logging file name is not a string, please correct.")
        # check that it is a log file
        elif log_file[-4:] != ".log":
            raise InputError("logging file name must be a .log file")
        
        # check vaf_threshold
        if vaf_threshold > 1 or vaf_threshold < 0:
            raise InputError("vaf threshold value must be between 0 and 1.")
        
        # check input vcf 
        if type(input_vcf) != str:
            raise InputError("Input file name is not a string, please correct.")
        # check that it is a vcf file
        
        elif input_vcf[-4:] != ".vcf":
            raise InputError("Input file name must be a .vcf file")        
        
    except Exception as e:
        logging.error(f"Input file issue:{e}")
        sys.exit(1)

def create_output_file(input_file_name, output_file_name, vaf_threshold):
    """ creates the framework files for the outputs"""
        # opens the input file and intiates output file
    try:
        with open(input_file_name,'r') as input_vcf_file, open( output_file_name,'a') as output_vcf_file:
            # check that the output file is empty by checking the file size  
            if os.stat(output_file_name).st_size > 0:
                logging.warning("Output vcf file already contains data, please check output for duplicated entries or ensure the output file name is unique.")

            # read content from first file and select header lines
            for line in input_vcf_file:
                if line.startswith("##"):            
                    # append content to second file
                    output_vcf_file.write(line)
                if line.startswith("#CHROM"):
                    final_header_line = line
                    break

            # add line stating vaf_threshold used (other header details can be added here)
            output_vcf_file.write(f"##Variants filtered with population frequency threshold of: {vaf_threshold} \n")
            # finally add the column heading line
            output_vcf_file.write(final_header_line)


    except FileNotFoundError:
        logger.error("Input file given not found, please check file path and try again.")


def count_header_lines(vcf):
    """Count number of header line in vcf"""
    count = 0
    try:
        with open(vcf, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    count += 1
        if count == 0:
            raise ValueError("VCF does not appear to have a header.")
    except ValueError as e:
        logger.error(e)
        sys.exit(1)
    
    return count


def load_vcf_body(vcf):
    """Load vcf into dataframe and rename sample"""
    
    header_count = count_header_lines(vcf)
    df = pd.read_csv(vcf, sep='\t', skiprows=header_count-1)
    df.columns = ['#CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO','FORMAT', 'unknown']
    return df


def find_annotation_headings(vcf):
    """ Searches the vcf and pulls out the VEP annotation fields used. 
    To be used downstream to create an accurately labelled dataframe
    that can adapt to changes in VEP annotation selection. Returns list of strings."""
    # open the vcf
    try:
        with open(vcf, 'r') as vcf:
            #iterate through each line of the vcf
            for l in vcf:
                    # find the line that contains vcf information
                    if l.startswith('##INFO=<ID=CSQ'):
                        #regular expression captures the annotation headings
                        annotation_headings_match = re.search(r'Format: (.+?)">', l)
                        # split the annotation headings into a string by selecting string portion of match output
                        annotation_headings = annotation_headings_match.group(1).split('|')
                        #breaks out of block
                        break
    except FileNotFoundError:
        logging.error("Input vcf not found, please check file path and try again.")
    return annotation_headings


def chunk_annotations(vep_annotation_list, headings_list_length):
    """ VCF annotations can contain multiple transcripts which must be subdivided. """
    if len(vep_annotation_list) <= headings_list_length:
        list_output = vep_annotation_list
    # reduces interval number for variants with multiple transcripts
    else:
        list_output = [vep_annotation_list[i:i + headings_list_length - 1] for i in range(0, len(vep_annotation_list), headings_list_length - 1)]
    return  list_output


def make_variant_dataframe(variant_list, column_headings):
    # makes a flat list a list in a list
    # iterates through each element of the variant list
    # there is no list within the list, ei. a flat list,
    # it is wrapped in a list
    if all(not isinstance(i, list) for i in variant_list):
        variant_list = [variant_list]
        print(variant_list)
    
    column_heading_len = len(column_headings)
    variant_lens = []
    variant_lens.append(column_heading_len)

    for f in variant_list:
        length = len(f)
        variant_lens.append(length)

    print(variant_lens)




    try:
        df = pd.DataFrame(variant_list, columns = column_headings)
    
    except ValueError:
        column_headings = column_headings[:-1]
        df = pd.DataFrame(variant_list, columns = column_headings)
        pass
    logger.debug(variant_list)
    logger.debug(column_headings)
    
    df = pd.DataFrame(variant_list, columns = column_headings)
    return df
    
    



def gnomad_population_frequency_filter(variant_dataframe, vaf_threshold):

    # set filter status to 0 by default
    filter_activate = "0"
    logger.debug(variant_dataframe)

    try:
        # Convert 'MAX_AF' column to float
        variant_dataframe['MAX_AF'] = variant_dataframe['MAX_AF'].astype(float)

        # filter variant to search for high frequency variants 
        max_af = variant_dataframe[variant_dataframe['MAX_AF'] > vaf_threshold]
        logger.debug(max_af)
        
        #if anything is present in new dataframe, activate filter
        if not max_af.empty:
            filter_activate = "1"        

    except ValueError:
        logger.warning('No gnomAD frequencies found for this variant.')
        filter_activate = '2'
        pass

    return filter_activate


def clinvar_benign_filter(variant_dataframe):
    # set filter status to 0 by default
    filter_activate = "0"
    logger.debug(variant_dataframe)

    try:
        # Convert 'MAX_AF' column to float
        variant_dataframe['MAX_AF'] = variant_dataframe['MAX_AF'].astype(float)

        # filter variant to search for high frequency variants 
        clinical_sig = variant_dataframe[variant_dataframe['CLIN_SIG'] == 'benign']
        
        #if anything is present in new dataframe, activate filter
        if not clinical_sig.empty:
            filter_activate = "1"        

    except ValueError:
        logger.warning('No ClinVar record for this variant.')
        filter_activate = '2'
        pass

    return filter_activate


def clinvar_pathogenic_filter(variant_dataframe):
    # set filter status to 1 by default (filter out)
    filter_activate = "1"
    
    # select the clinvar records column and covert to strings 
    variant_dataframe['CLIN_SIG'] = variant_dataframe['CLIN_SIG'].astype(str)
        
    # collect all of the clinvar entry data into a single, lowercase string
    clin_sig_values = ' '.join(variant_dataframe['CLIN_SIG'].dropna().astype(str)).lower()
    logging.debug(f'Here\'s the clinvar records: {clin_sig_values}')
    
    # search the string for the word pathogenic
    pathogenic_found = re.search('pathogenic', clin_sig_values)
    
    # if 'pathogenic' is found, change filter activate to 0 (keep)
    if pathogenic_found != None:
            filter_activate = "0"    

    return filter_activate


def variant_filtering_block(variant_dataframe, vaf_threshold):
    """Returns a value, 0 (keep), 1 (filter out), 2 (filtering error)"""
    # By default variants are kept, so default to 0
    variant_filter_status = "0"
    
    """Filter OUT modules:
    All filters in this section must contain filter out conditions. 
    If any of these filters are activated (returns 1), the variant will 
    be filtered.
    """
    # starts a list to store filter results
    out_filters = []

    # filters out variant if population level above threshold
    gnomad_filter_response = gnomad_population_frequency_filter(variant_dataframe, vaf_threshold)

    # filters out variant if ClinVar record is benign
    clinvar_filter_response = clinvar_benign_filter(variant_dataframe)

    # places the response into the filter list
    out_filters.append(str(gnomad_filter_response))
    out_filters.append(str(clinvar_filter_response))

    # if any of the filters activated, variant status set to filter OUT
    if "1" in out_filters:
        logger.debug("Filter activated")
        variant_filter_status = "1"

    """ OVERRIDE filter checks:
    If any of the following filters are activated, irregardless of 
    the responses from the filter OUT modules, the variant will be kept.
    """
    # checks Clinvar records for pathogenic classification
    clinvar_pathogenic_response = clinvar_pathogenic_filter(variant_dataframe)
    print(f'Clinvar status:{clinvar_pathogenic_response}')

    # if override filter is activated, the variant is retained
    if clinvar_pathogenic_response == "0":
        variant_filter_status = "0"

    return variant_filter_status


def select_variants(data_frame, vcf, output_vcf, vaf_threshold):

    # select the VEP annotation fields
    annotation_headings = find_annotation_headings(vcf)
    annotation_headings_length = len(annotation_headings)

    # iterate through each line of the dataframe and select INFO
    for row in range(len(data_frame)):

        #select the whole variant row
        variant_string = data_frame.loc[row]

        # place into a string for appending to output file
        row_str = '\t'.join(map(str, variant_string.values))
        
        #select just the INFO row
        vep_annotation_string = data_frame['INFO'].loc[data_frame.index[row]]

        #isolate vep annotations
        vep_start_index = vep_annotation_string.find('CSQ=')
        isolated_vep_annotations = vep_annotation_string[vep_start_index:]

        # seperate the info line into a list
        vep_annotation_list = isolated_vep_annotations.split('|')

        # split the variant annotations transcripts into seperate lists
        vep_annotation_list_list = chunk_annotations(vep_annotation_list, annotation_headings_length)
        logger.debug(vep_annotation_list_list)

        # place the variant annotations into a dataframe with headings 
        variant_dataframe = make_variant_dataframe(vep_annotation_list_list, annotation_headings)
        
        # pass to filtering block
        filter_block_response = variant_filtering_block(variant_dataframe, vaf_threshold)

        # based on the filter block response, variants are added to the output file
        if filter_block_response == '0':
            output_vcf.write(row_str + '\n')

        elif filter_block_response == '1':
            logging.info("Variant has been filtered")

        else: 
            output_vcf.write(row_str + '\n')
            logger.warning("Variant failed filtering and has been included in the final output.")




""" Mainscript:

"""
# check inputs are appropriate
check_inputs(input_vcf, output_vcf_file, vaf_threshold, log_file)

# creates output file and copies over the vcf heading from the input vcf
create_output_file(input_vcf, output_vcf_file, vaf_threshold)  

# collects the annotation headings from the input vcf
annotation_headings = find_annotation_headings(input_vcf)
logger.debug(annotation_headings)

# loads the variants into a dataframe
data_frame = load_vcf_body(input_vcf)

# 
with open(output_vcf_file, "a") as output_file:
    select_variants(data_frame, input_vcf, output_file, float(vaf_threshold))

# end the script
print("Filtering complete.")
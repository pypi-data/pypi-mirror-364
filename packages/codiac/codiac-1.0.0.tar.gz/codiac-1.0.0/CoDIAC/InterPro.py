from collections import defaultdict
import requests
import logging
import pandas as pd

import timeit


def fetch_uniprotids(interpro_ID, REVIEWED=True, species='Homo sapiens'):
    """
    Given an InterPro_ID, fetch all the records (or only reviewed records) for all species or for a specific taxonomy. 

    Examples: Examples, use this module like this, the first being a more restrictive human with reviewed, versus all records associated within an Interpro ID: 
        .. code-block:: python
        
            fetch_uniprotids('IPR000980', REVIEWED=True, species='Homo sapiens') # human proteins with reviewed records
            fetch_uniprotids('IPR000980', REVIEWED=False, species='all') #all species records, reviewed and unreviewed
        
        
    Parameters
    ----------
        interpro_ID: str
            InterPro ID to search for
        REVIEWED: bool
            If TRUE, only reviewed records will be returned 
        species: string
            Using scientific name under the Uniprot taxonomy to define species. 
            See here for taxonomy names: https://www.uniprot.org/taxonomy?query=*
    
    Returns
    -------
        uniprot_ID_list: list
            list of all uniprot IDs found in search. If a species was set, all uniprot IDs for a species
            will be returned in this list, otherwise, all species from search will be returned.
        species_dict: dict
            Dictionary, with top keys equal to the species scientific name and 
            points to an inner dict that keeps track of the database source 'reviewed' or 'unreviewed'
            and has lists of the uniprot IDs found for that species under that database source.
    """
    count_data = 0 # count of records expected to be found
    #species = species.replace(" ", "+")
    interpro_url = "https://www.ebi.ac.uk/interpro/api"
    if REVIEWED: # if reviewed, we need to change the URL
        url = ''.join([interpro_url, "/protein/reviewed/entry/interpro/", interpro_ID, "/"])
    else:
        url = ''.join([interpro_url, "/protein/UniProt/entry/interpro/", interpro_ID, "/"])
    # if species is defined, we need to add this to the URL
    if species.lower() !='all':
        species_temp = species.replace(" ", "+")
        url = ''.join([url, "?search=", species_temp, "&page_size=200"])
    else: # if all species, we need to add a page size to the URL
        url = ''.join([url, "?&page_size=200"])
        if not REVIEWED:
            print("WARNING: About to search for all records for all species, this will take a while...")
    logging.basicConfig(filename='error.log',
                    format='%(asctime)s %(message)s',
                    encoding='utf-8',
                    level=logging.WARNING) # set up logging for requests exceptions
    fetch_all_results = []  # list to store all results

    try:
        with requests.Session() as session:
            response = session.get(url)  # make the request
            data = response.json()  # convert to json
            count_data = data['count']

            fetch_all_results.extend(data['results'])  # use extend instead of +

        # if there are more pages, we need to fetch these as well
        while data['next'] is not None:
            print("Found next page and downloading", data['next'])
            response = session.get(data['next'])
            data = response.json()
            fetch_all_results.extend(data['results'])  # use extend instead of +

    except requests.exceptions.RequestException as err:
        print('Found request exceptions...')
        print('Most likely error is species formatting, check %s' % species)
        logging.warning(err)

    UNIPROT_ID_LIST = []  # list to store all uniprot IDs
    uniprot_dict = {}  # dictionary to store uniprot IDs and their associated species
    species_dict = defaultdict(lambda: defaultdict(list))  # dictionary to store species and their associated uniprot IDs

    all_species = {'all', 'All', 'ALL'}

    for entry in fetch_all_results:  # loop through all results
        Uniprot_Accession = entry['metadata']['accession']
        source_database = entry['metadata']['source_database']
        Scientific_name = entry['metadata']['source_organism']['scientificName']

        if species not in all_species and species not in Scientific_name:
            continue

        UNIPROT_ID_LIST.append(Uniprot_Accession)
        uniprot_dict[Uniprot_Accession] = Scientific_name
        species_dict[Scientific_name][source_database].append(Uniprot_Accession)

    print(f"Fetched {len(UNIPROT_ID_LIST)} Uniprot IDs linked to {interpro_ID}, where count expected to be {count_data}")
    return(UNIPROT_ID_LIST, species_dict)


def collect_data_canonical(entry):
    """
    Given a domain feature from the InterPro API, collect the data for that feature
    and return a dictionary with the keys 'name', 'accession', 'num_boundaries', 'boundaries'
    where 'boundaries' is a list of dictionaries with keys 'start' and 'end'. This is 
    for the canonical specific call to the InterPro API, where metadata exists.
    
    Parameters
    ----------
    entry: dict
        dictionary from the InterPro API

    Returns
    -------
    dictionary: dict
        dictionary with the keys 'name', 'accession', 'num_boundaries', 'boundaries'
        where 'boundaries' is a list of dictionaries with keys 'start' and 'end'

    """
    entry_protein_locations = entry['proteins'][0]['entry_protein_locations']
    if entry_protein_locations is None:
        entry_protein_locations = []

    num_boundaries = len(entry_protein_locations)
    if num_boundaries == 0:
        return None

    dictionary = { 
        'name': entry['metadata']['name'],
        'accession': entry['metadata']['accession'],
        'num_boundaries': num_boundaries,
        'boundaries': [
            {
                'start': bounds['start'],
                'end': bounds['end']
            } 
            for i in range(num_boundaries)
            for bounds in [entry_protein_locations[i]['fragments'][0]]
            if bounds['dc-status'] == "CONTINUOUS"
        ]
    }
    if 'extra_fields' in entry and 'short_name' in entry['extra_fields']:
        dictionary['short'] = entry['extra_fields']['short_name']
    return dictionary


def collect_data_isoform(feature):
    """
    Given a domain feature from the InterPro API, collect the data for that feature
    and return a dictionary with the keys 'name', 'accession', 'num_boundaries', 'boundaries'
    where 'boundaries' is a list of dictionaries with keys 'start' and 'end'. This is 
    for the isoform specific call to the InterPro API, where the feature is a dictionary
    
    Parameters
    ----------
    entry: dict
        dictionary from the InterPro API

    Returns
    -------
    dictionary: dict
        dictionary with the keys 'name', 'accession', 'num_boundaries', 'boundaries'
        where 'boundaries' is a list of dictionaries with keys 'start' and 'end'

    """
    dictionary = {}    
    source_database = feature['source_database']

    accession = feature['accession'] 
    name = feature['name']
    type = feature['type']
    locations_list = feature['locations']
    boundaries = []
    
    for location in locations_list:
        for boundary in location['fragments']:
            #print(location)
            boundary_dict = {}
            boundary_dict['start'] = boundary['start']
            boundary_dict['end'] = boundary['end']
            boundary_dict['dc-status'] = boundary['dc-status']
            boundaries.append(boundary_dict)
    dictionary = {
        'name': name,
        'accession': accession,
        'type': type,
        'source_database': source_database,
        'num_boundaries': len(boundaries),
        'boundaries': boundaries
    }

    return dictionary


def fetch_InterPro_json(protein_accessions):
    """
    Instantiates an api fetch to InterPro database for domains. Returns a dictionary of those repsonses with keys equal 
    to the protein accession run.
    
    """
    interpro_url = "https://www.ebi.ac.uk/interpro/api"
    extra_fields = ['short_name']
    response_dict = {}
    # code you want to evaluate
    with requests.Session() as session:
        for protein_accession in protein_accessions:
            # check if protein is an isoform and chane the protein to add isform 
            if '-' in protein_accession:
                main_accession = protein_accession.split('-')[0]
                #https://www.ebi.ac.uk/interpro/api/protein/uniprot/P23497/?isoforms=P23497-4
                url = interpro_url + "/protein/uniprot/" + main_accession + "/?isoforms="+protein_accession#+"&extra_fields=" + ','.join(extra_fields)
                #url = interpro_url + "/entry/interpro/protein/uniprot/" + main_accession + "?extra_fields=" + ','.join(extra_fields) + "/?isoform="+protein_accession
# check if protein is a main accession and add the isoform
            else:
                # going through the same URL for isoforms as canonical, so fixing the canonical to use -1
                #url = interpro_url + "/protein/uniprot/" + protein_accession #+ "/?isoforms="+protein_accession+"-1"
                #shutting off short name fetch during this so we can ensure the names are all consistent between mixed canonical/isoform fetches
                url = interpro_url + "/entry/interpro/protein/uniprot/" + protein_accession #+ "?extra_fields=" + ','.join(extra_fields)
            #print(url)  # Debugging line
            try:
                response_dict[protein_accession] = session.get(url).json()
            except Exception as e:
                if session.get(url).status_code == 204:
                    response_dict[protein_accession] = {}
                    print(f"An empty response was received for {protein_accession} resulting in empty domain architecture.")
                else:
                    print(f"Error processing {protein_accession}: {e}")  # Debugging line
            #print(url)  # Debugging line
                
    return response_dict


def get_domains(protein_accessions):
    """
    Given a uniprot accession (protein_accession), return a list of domain dictionaries
    each domain dictionary has keys 'name', 'start', 'end', 'accession' (InterPro ID), 'num_boundaries' (number of this type found)
    These domains are in the order as returned by InterPro, where InterPro returns the parent nodes first. Once 
    we find domains that begin to overlap in the API response, we stop adding those to the final set of domains. 

    Parameters
    ----------
    protein_accession: str
        Uniprot accession ID for a protein
    Returns
    -------
    domain_dict: dict of list of dicts
        outer key values are the individual protein accessions
        these point to a list of dictionaries, each dictionary is a domain entry with keys 'name', 'start', 'end', 'accession', 'num_boundaries'
        this list is ordered by start positions of domains
    domain_string_dict: dict of lists of strings
        outer key values are the individual protein accessions
        these point to a list of stirngs, each string is information for the domain in this manner
        short_name:interpro_id:start:end
    arch_dict: dict of strings
        outer key values are the individual protein accessions
        these point to a string that is the domain architecture, | separated list of domain names
    """
    resp_dict = fetch_InterPro_json(protein_accessions) #pack and unpack as a list for a single domain fetch
    domain_dict = {}
    domain_string_dict = {}
    arch_dict = {}
    for protein_accession in resp_dict:
        domain_dict[protein_accession], domain_string_dict[protein_accession], arch_dict[protein_accession] = get_domains_from_response(resp_dict[protein_accession])
    
    # now let's get the short names for all domains found in that list of proteins.
    interpro_domain_list = []
    for protein_accession in domain_dict:
        if domain_dict[protein_accession]:
            interpro_domain_list.extend([domain['accession'] for domain in domain_dict[protein_accession]])

    unique_domain_list = [{'accession': accession} for accession in set(interpro_domain_list)]
    interpro_name_dict = fetch_interpro_short_names(unique_domain_list)
    #print(unique_domain_list)
    #print(interpro_name_dict)
    for protein_accession in domain_dict:
        # add the short names to the domain_dict, the domain_string_dict, and the arch_dict
        for i, domain in enumerate(domain_dict[protein_accession]):
            domain_dict[protein_accession][i]['short_name'] = interpro_name_dict[domain['accession']]
        domain_string_dict[protein_accession] = [f"{domain['short_name']}:{domain['accession']}:{domain['start']}:{domain['end']}" for domain in domain_dict[protein_accession]]
        arch_dict[protein_accession] = "|".join([domain['short_name'] for domain in domain_dict[protein_accession]])

    return domain_dict, domain_string_dict, arch_dict

def get_domains_from_response(resp):
    """
    Given a response from the InterPro API for a single protein search, return a list of domain dictionaries
    each domain dictionary has keys 'name', 'start', 'end', 'accession' (InterPro ID), 'num_boundaries' (number of this type found)
    These domains are in the order as returned by InterPro, where InterPro returns the parent nodes first. Once 
    we find domains that begin to overlap in the API response, we stop adding those to the final set of domains. 
    This returns the ordered list of domains and a list of domain information strings, based on start site. 

    This function can detect if the repsonse came as a fetch to the isoform specific call or the canonical protein and uses
    the correct approach to collect the data.

    Parameters
    ----------
    resp: dict
        response from the InterPro API (json) for a speicfic uniprot_id
    Returns
    -------
    sorted_domain_list: list
        list of dictionaries, each dictionary is a domain entry with keys 'name', 'start', 'end', 'accession', 'num_boundaries'
    domain_string_list: list
        list of domain information id:start:end
    domain_arch: string
        domain architecture as a string, | separated list of domain names
    """
    if resp:
        #It's a canonical record
        if 'results' in resp:  # this is the isoform specific fetch
            entry_results = resp['results']
            d_dict = {} # Dictionary to store domain information for each entry
            d_resolved = []
            for i, entry in enumerate(entry_results):
            #for i, entry in enumerate(entry_list):
                if entry['metadata']['type'] == 'domain': #get domain level only features
                    d_dict[i] = collect_data_canonical(entry)
            
            values = list(d_dict.keys())
            if values:
                d_resolved+=return_expanded_domains(d_dict[values[0]]) # a list now: kick off the resolved domains, now start walking through and decide if taking a new domain or not.
            
            for domain_num in values[1:]:
            
                d_resolved = resolve_domain(d_resolved, d_dict[domain_num])

            #having resolved, now let's sort the list and get the domain string information
            sorted_domain_list, domain_string_list, domain_arch = sort_domain_list(d_resolved)
            
        # It's an isoform
        elif 'features' in resp:  # this is the canonical fetch
            d_dict = {}
            for i, entry in enumerate(resp['features']):
                domain_dict = collect_data_isoform(resp['features'][entry])
                if domain_dict['source_database'] == 'interpro' and domain_dict['type'] == 'domain':  # only collect domains from InterPro
                    d_dict[i] = domain_dict
                
            values = list(d_dict.keys())    

        # values = list(d_dict.keys())
            d_resolved = []
            if values:
                d_resolved+=return_expanded_domains(d_dict[values[0]]) # a list now: kick off the resolved domains, now start walking through and decide if taking a new domain or not.

            for domain_num in values[1:]:
                d_resolved = resolve_domain(d_resolved, d_dict[domain_num])

        #having resolved, now let's sort the list and get the domain string information
            sorted_domain_list, domain_string_list, domain_arch = sort_domain_list(d_resolved)
    else:
        sorted_domain_list = []
        domain_string_list = []
        domain_arch = ''
    return sorted_domain_list, domain_string_list, domain_arch

  
def return_expanded_domains(domain_entry):
    """
    Given a domain entry, such as from collect_data, return a list of expanded domains where there is only 
    one boundary per set. This will reset the dictionary, such that instead of 'boundaries' with a list of ['start': x, 'end': y]
    it will be a single boundary with 'start': x, 'end': y as keys in the dictionary.
    """
    boundary_list = domain_entry['boundaries']
    domain_new = domain_entry.copy()
    domain_new['start'] = boundary_list[0]['start']
    domain_new['end'] = boundary_list[0]['end']
    domain_list = []
    domain_list.append(domain_new)
    #make a new dictionary with the start and end values of subsequent domains (Then go through and pop boundaries off all)
    if len(boundary_list) > 1:
        for i in range(1, len(boundary_list)):
            domain_temp = domain_entry.copy()
            domain_temp['start'] = boundary_list[i]['start']
            domain_temp['end'] = boundary_list[i]['end']
            domain_list.append(domain_temp)
    for domain in domain_list: #remove the boundaries term now
        domain.pop('boundaries')
    return domain_list

def resolve_domain(d_resolved, dict_entry, threshold=0.5):
    """
    Given a list of resolved domains and a new domain entry, resolve the new domain entry with the existing domains
    Keep the new domain entry if it does not overlap by more than threshold% with any existing domain. Default threshold is
    50% (or 0.5)
    Parameters
    ----------
    d_resolved: list
        list of dictionaries, each dictionary is a domain entry with keys 'name', 'start', 'end', 'accession', 'num_boundaries'
    dict_entry: dict
        dictionary of domain information with that comes from collect_data on an entry. This function expands multiple domain entries, meaning that these are prioritized as they are encountered first
    threshold: float
        threshold for rejecting domains by overlap, default is 0.5, should be between 0 and 1
    Returns
    -------
    d_resolved: list
        list of dictionaries, each dictionary is a domain entry with keys 'name', 'start', 'end', 'accession', 'num_boundaries'
    """
    # d_resolved is a list of dictionaries, each dictionary is a domain entry
    #setup the existing boundaries that are in d_resolved
    if threshold < 0 or threshold > 1:
        threshold = 0.5 #set to default
        print("WARN: Threshold must be between 0 and 1 for rejecting domains by overlap, setting to default of 0.5")

    boundary_array = []
    for domain in d_resolved:
        boundary_array.append(set(range(domain['start'], domain['end'])))
    
    #expand the dict_entry as well to a list
    new_domains = return_expanded_domains(dict_entry)
    #print("DEBUG: have these new domains")
    #print(new_domains)

    #first expand if multiple boundaries exist in the dict_entry
    for domain in new_domains:
        range_new = set(range(domain['start'], domain['end']))
        found_intersecting = False
        for range_existing in boundary_array:
            #check if the set overlap between the new range and the existing range is greater than 
            # 50% of the new range. If so, do not add the new range.
            if len(range_new.intersection(range_existing))/len(min(range_new, range_existing)) > threshold:
                found_intersecting = True
                break
        if not found_intersecting:
            d_resolved.append(domain)
    return d_resolved

def sort_domain_list(domain_list):
    """
    Given a list of resolved domains, return a string of domain information id:start:end and a sorted list of
    the domains according to the start site. 

    Parameters
    ----------
    domain_list: list
        list of domain dictionaries, where the dictonaries have keys 'name', 'accession', 'start', 'end'
    Returns
    -------
    sorted_domain_list: list
        list of domain dictionaries, now sorted by the start positions, also there is short name added
    domain_string_list: list
        list of domain information id:start:end
    domain_arch: string
        domain architecture as a string, | separated list of domain names

    """
    domdict = {}
    for domain in domain_list:
        start = int(domain['start'])
        if start in domdict:
            print("ERROR: More than one domain have the same start position!")
        domdict[start] = domain

    sorted_dict = dict(sorted(domdict.items(),reverse=False))
    sorted_domain_list = []
    domain_string_list = []
    domain_arch_names = []

    # get the short names for the domains if 'short' is not in the domain dictionary
    # test it 
    # if 'short' not in domain_list[0]:
    #     interpro_short_names = fetch_interpro_short_names(domain_list)
    #     for domain in domain_list:
    #         accession = domain['accession']
    #         if accession in interpro_short_names:
    #             domain['short'] = interpro_short_names[accession]
    #         else:
    #             domain['short'] = 'Unknown'

    for key, value in sorted_dict.items():
        sorted_domain_list.append(value)
        #domain_string_list.append(value['short']+':'+value['accession']+':'+str(key)+':'+str(value['end']))
        domain_string_list.append(value['accession']+':'+str(key)+':'+str(value['end']))
        #domain_arch_names.append(value['short'])
    return sorted_domain_list, domain_string_list, '|'.join(domain_arch_names)


def fetch_domain_short_name(interpro_id):
    """
    Given an InterPro ID, fetch the short name of the domain from the InterPro API.
    
    Parameters
    ----------
    interpro_id: str
        InterPro ID to search for
    
    Returns
    -------
    short_name: str
        Short name of the domain associated with the InterPro ID
    """
    interpro_url = "https://www.ebi.ac.uk/interpro/api"
    url = f"{interpro_url}/entry/interpro/{interpro_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        short_name = data['metadata']['name']['short']
        return short_name
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching short name for {interpro_id}: {e}")
        return None
    
def fetch_interpro_short_names(domain_list):
    """
    Given a list of domains with domain['accession'] the InterPro ID, fetch the short names for each InterPro ID and return a dictionary
    with InterPro ID as keys and short names as values.

    Parameters
    ----------
    domain_list: list
        List of domains in a protein record, where each domain has a dictionary with an 'accession' key

    Returns
    -------
    dict
        Dictionary with InterPro ID as keys and short names as values
    """
    interpro_short_names = {}

    interpro_ids = [domain['accession'] for domain in domain_list if 'accession' in domain]
    interpro_ids = list(set(interpro_ids))  # Remove duplicates
    for interpro_id in interpro_ids:
        short_name = fetch_domain_short_name(interpro_id)
        if short_name:
            interpro_short_names[interpro_id] = short_name
        else:
            interpro_short_names[interpro_id] = None  # Handle cases where short name is not found
    return interpro_short_names



def appendRefFile(input_RefFile, outputfile):
    '''
    Takes a reference file generated made by CoDIAC.UniProt.makeRefFile and adds 
    interpro domain metadata as a new column (i.e. this appends domain information defined by InterPro
    to the Uniprot reference)

    Parameters
    ----------
    input_RefFile: string
        name of the input reference file generated from the  makeRefFile function in CODAC.py
    outputfile: string
        name of the file to be outputted by this function
        
    Returns
    -------
    df: Pandas Dataframe
        In addition to printing the dataframe to a CSV file (as defined by outputfile)
        this returns the dataframe that is presented
    '''
    df = pd.read_csv(input_RefFile)
    uniprotList = df['UniProt ID'].to_list()
    print("Fetching domains..")
    domain_dict, domain_string_dict, domain_arch_dict = get_domains(uniprotList)
    print("Appending domains to file..")    
    for i in range(len(uniprotList)):
        df.at[i, 'Interpro Domains'] = ';'.join(domain_string_dict[uniprotList[i]])
        df.at[i, 'Interpro Domain Architecture'] = domain_arch_dict[uniprotList[i]]
    #df['Interpro Domains'] = metadata_string_list
    #df['Interpro Domain Architecture'] = domain_arch_list
    df.to_csv(outputfile, index=False)
    print('Interpro metadata succesfully incorporated')
    return df

def Main():
    parser = argparse.ArgumentParser()
    parser.add_argument("InterPro_ID",help="InterPro ID you wish to enter", type=str)
    parser.add_argument("Output_Dir", help="Directory to write the file with Uniprot IDs", type=str)

    args=parser.parse_args()

    df = pd.DataFrame()
    df['Uniprot ID'] = fetch_uniprotids(args.InterPro_ID)
    PATH = args.Output_Dir+'/UniProt_IDs.csv'
    df.to_csv(PATH, index=False)

if __name__ =='__main__':
    Main()
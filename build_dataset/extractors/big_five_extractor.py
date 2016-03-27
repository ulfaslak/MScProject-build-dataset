from sensible_raw.loaders import loader
import requests as rq
import numpy as np
import json
import os

class Big_five_extractor:
    """Get Big Five values for users
    
    Initiate with token, and run main for each user.
    
    Parameters
    ----------
    token : str
        Research token like b68b684617bdbc5adec25ac83479e7
    """
    
    def __init__(self, token=None):
        
        ROOTPATH = os.path.abspath('')
        
        try:
            with open(ROOTPATH + '/build_dataset/data_cache/questionnaire.json', 'r') as infile:
                dat = json.load(infile)
            print "[big_five_extractor] Loaded data from local copy!"
        except IOError:
            if token == None:
                raise Exception('You must provide a token.')
            print "[big_five_extractor] Loading data from API...",
            dat = rq.get("https://www.sensible.dtu.dk/sensible-dtu/connectors/connector_answer/v1/aggregate_questionnaire_question/get_aggregated_questionnaire_data/?bearer_token=%s&format=json&decrypted=false&form_version=90920167766cb9d5d5767b692b9d3acb&sortby=timestamp&order=1&limit=1000&" % token).json()
            print "... success!"
            with open(ROOTPATH + '/build_dataset/data_cache/questionnaire.json', 'w') as infile:
                json.dump(dat,infile)
            print "[big_five_extractor] Making local copy!"
                
        bfi_dat = dict(
            (
                response['user'][1:-1], 
                dict((k,v) for k,v in response.items() if k[:2] == "bf")
            )
                for response in dat['results'])
        
        response_codes = {'meget_uenig': 0, 'uenig': 1, 
                          'hverken_enig_eller_uenig': 2, 
                          'enig': 3, 'meget_enig': 4}

        big5_map = {
                    "bfi_talk": {"dim": "extraversion", "reversed": False},
                    "bfi_error": {"dim": "aggreeableness", "reversed": True},
                    "bfi_work": {"dim": "conscientiousness", "reversed": False},
                    "bfi_depressed": {"dim": "neuroticism", "reversed": False},
                    "bfi_original": {"dim": "openness", "reversed": False},
                    "bfi_reserved": {"dim": "extraversion", "reversed": True},
                    "bfi_helpfull": {"dim": "aggreeableness", "reversed": False},
                    "bfi_careless": {"dim": "conscientiousness", "reversed": True},
                    "bfi_relaxed": {"dim": "neuroticism", "reversed": True},
                    "bfi_currious": {"dim": "openness", "reversed": False},
                    "bfi_energi": {"dim": "extraversion", "reversed": False},
                    "bfi_fight": {"dim": "aggreeableness", "reversed": True},
                    "bfi_reliable": {"dim": "conscientiousness", "reversed": False},
                    "bfi_tense": {"dim": "neuroticism", "reversed": False},
                    "bfi_creative": {"dim": "openness", "reversed": False},
                    "bfi_enthusiasm": {"dim": "extraversion", "reversed": False},
                    "bfi_forgive": {"dim": "aggreeableness", "reversed": False},
                    "bfi_disorderly": {"dim": "conscientiousness", "reversed": True},
                    "bfi_worry": {"dim": "neuroticism", "reversed": False},
                    "bfi_imagination": {"dim": "openness", "reversed": False},
                    "bfi_quiet": {"dim": "extraversion", "reversed": True},
                    "bfi_confident": {"dim": "aggreeableness", "reversed": False},
                    "bfi_lazy": {"dim": "conscientiousness", "reversed": True},
                    "bfi_stable": {"dim": "neuroticism", "reversed": True},
                    "bfi_inventive": {"dim": "openness", "reversed": False},
                    "bfi_strong_personality": {"dim": "extraversion", "reversed": False},
                    "bfi_cold": {"dim": "aggreeableness", "reversed": True},
                    "bfi_hold_on": {"dim": "conscientiousness", "reversed": False},
                    "bfi_unbalanced": {"dim": "neuroticism", "reversed": False},
                    "bfi_art": {"dim": "openness", "reversed": False},
                    "bfi_shy": {"dim": "extraversion", "reversed": True},
                    "bfi_caring": {"dim": "aggreeableness", "reversed": False},
                    "bfi_effective": {"dim": "conscientiousness", "reversed": False},
                    "bfi_calm": {"dim": "neuroticism", "reversed": True},
                    "bfi_rutine": {"dim": "openness", "reversed": True},
                    "bfi_social": {"dim": "extraversion", "reversed": False},
                    "bfi_rude": {"dim": "aggreeableness", "reversed": True},
                    "bf_complet": {"dim": "conscientiousness", "reversed": False},
                    "bfi_nervous": {"dim": "conscientiousness", "reversed": False},
                    "bfi_play": {"dim": "openness", "reversed": False},
                    "bfi_few_art": {"dim": "openness", "reversed": True},
                    "bfi_coorporation": {"dim": "aggreeableness", "reversed": False},
                    "bfi_distract": {"dim": "conscientiousness", "reversed": True},
                    "bfi_taste_art": {"dim": "openness", "reversed": False}
                    }
        
        dataset = {}

        for user, questions in bfi_dat.items():
            append_datapoint = True
            big5_vals = {"openness": [], "extraversion": [], "aggreeableness": [], "conscientiousness": [], "neuroticism": []}

            for q, a in questions.items():
                if a == u'':
                    append_datapoint = False
                    break
                dim = big5_map[q]['dim']
                rev = big5_map[q]['reversed']
                if rev:
                    big5_vals[dim].append(4-response_codes[a[1:-1]])
                else:
                    big5_vals[dim].append(response_codes[a[1:-1]])

            if append_datapoint:
                big5_vals = dict((k,np.mean(v)) for k,v in big5_vals.items())
                dataset[user] = big5_vals
                
        self.dataset = dataset
        
        
        
    def main(self, user):
        """Get Big Five values for user
        
        Parameter
        ---------
        user : user-id (hash value)
        
        Return
        ------
        bfi_values : dict
        
            Example
            -------
            >>> bf = Big_five_extractor("278cs0a9e3aa7630dc1b62b85b2d73")
            >>> bf.main("198c5029e3aa7630cc1b62b85b2d74")
            {'aggreeableness': 2.5555555555555554,
             'conscientiousness': 3.0,
             'extraversion': 2.0,
             'neuroticism': 1.0,
             'openness': 2.6000000000000001}
        """
        user_raw_value = loader.get_raw_value("user", user)
        bfi_values = self.dataset[user_raw_value]
        ocean = ['openness', 'conscientiousness', 'extraversion', 'aggreeableness', 'neuroticism']
        return np.array([bfi_values[t] for k in ocean])


import pandas as pd
from collections import defaultdict
from datetime import datetime as dt
import numpy as np
import os

from workers import load_sensible_data as lsd
from workers import apply_time_constraints as atc

class Sms_extractor:
    """Extract features from SMS data for a single user
    
    Run the main function with a user ID and a list of time ranges. Every 
    feature extractor within class computes a float value for each time range.
    
    Parameters
    ----------
    time_constraint : list object
        Every item is a dict of form {'hours': <list of hours>, 'days': <list of days>, 
        'spans': <list of timespan-tuples>}
        
    Output
    ------
    datapoint : dict

        Example
        -------
            {'sms_fractions_of_conversations_started': 0.34782608695652173,
             'sms_traffic': 3.6888794541139363,
             'sms_overall_received_responsiveness': -9.0581865605306326,
             'sms_overall_responsiveness': -9.0610147611536238,
             'sms_selectivity_in_responsiveness': -5.4102083517105317}
    """
    
    def __init__(self, time_constraint, suppress=[], auxlabel="", load_old_datasources=False):
        
        self.suppress = suppress
        self.auxlabel = auxlabel
        
        ROOTPATH = os.path.abspath('')
        
        if not load_old_datasources:
            
            print "[sms] Building datasource from scratch ...",
            df_sms = lsd.load(time_constraint['spans'], "sms")

            # Filter out non-delivered messages
            df_sms = df_sms[df_sms['status'] <= 0]

            df_sms = atc.apply(df_sms, time_constraint)

            # Sort dataframe
            self.df_sms = df_sms.sort(['timestamp'], ascending=[1])
            self.users = set(self.df_sms['user'])
            
            # Save
            print "... succes! Saving."
            self.df_sms.to_pickle(ROOTPATH + '/data/%sdf_sms.pickle' % auxlabel)
            
        else:
            # Load
            print "[sms] Loading datasource from local."
            self.df_sms = pd.read_pickle(ROOTPATH + '/data/%sdf_sms.pickle' % auxlabel)
            self.users = set(self.df_sms['user'])
        
        print "[sms] Number of datapoints in range:", len(self.df_sms)
        
        
    # -------------------- #
    # Supporting functions #
    # -------------------- #
    
    def __partition_dyad_messages_to_conversations(self, messages):
        conversations = []

        timestamps = sorted(messages['timestamp']/1000)

        conversation_breaks = []
        for i, _ in enumerate(timestamps):
            if i == 0:
                continue
            delta_t = timestamps[i] - timestamps[i-1]

            if delta_t > self.expiration_time * 3600:
                start_break = int(timestamps[i-1])
                end_break = int(timestamps[i])
                conversation_breaks.append([start_break, end_break])

        conversations = []

        if len(conversation_breaks) == 0:
            conversations.append(messages)
            return conversations

        for i, _ in enumerate(conversation_breaks):
            if i == 0:
                conv_end = conversation_breaks[i][0]
                conversation = messages[
                    messages['timestamp']/1000 <= conv_end]
                conversations.append(conversation)
                continue
            if i == len(conversation_breaks)-1:
                conv_start = conversation_breaks[i][1]
                conversation = messages[
                    messages['timestamp']/1000 >= conv_start]
                conversations.append(conversation)
                continue

            conv_start = conversation_breaks[i-1][1]
            conv_end = conversation_breaks[i][0]
            conversation = messages[
                messages['timestamp']/1000 >= conv_start][
                messages['timestamp']/1000 <= conv_end]

            conversations.append(conversation)

        return conversations
    
    
    def __compute_user_conversations(self, expiration_time=6):
        
        self.expiration_time = expiration_time
    
        user_messages = self.df_sms[self.df_sms['user']==self.user]

        # the people that the user texts with
        conversers = set(user_messages['address'])

        user_conversations = {}

        for c in conversers:
            c_messages = user_messages[user_messages['address'] == c]

            c_conversations = self.__partition_dyad_messages_to_conversations(c_messages)

            user_conversations[c] = c_conversations

        return user_conversations
    
    
    def __compute_conversation_response_times(self, conversation):
        conversation = conversation.sort(['timestamp'],ascending=[1])
        
        response_times = defaultdict(list)

        sender_prev = {}
        sender = {}

        for i, message in enumerate(conversation.iterrows()):

            if i == 0:
                initiator = message[1]['type']
                sender_prev = {'actor': message[1]['type'],
                            'timestamp': message[1]['timestamp']}
                continue

            sender = {'actor': message[1]['type'],
                      'timestamp': message[1]['timestamp']}

            if sender['actor'] == sender_prev['actor']:
                continue

            response_time = (sender['timestamp'] - sender_prev['timestamp'])/1000

            response_times[sender['actor']].append(response_time)

            sender_prev = {'actor': message[1]['type'],
                           'timestamp': message[1]['timestamp']}
        
        response_time_user = np.mean(response_times[2])
        response_time_converser = np.mean(response_times[1])
        
        # Add expiration_time in seconds to response time for he who doesn't respond
        if np.isnan(response_time_user) and initiator == 1:
            response_time_user = self.expiration_time * 3600
        if np.isnan(response_time_converser) and initiator == 2:
            response_time_converser = self.expiration_time * 3600
            
            
        #print self.expiration_time

        return response_time_user, response_time_converser
    
    
    def __compute_responsiveness_from_responsetimes(self,responsetimes):
        if len(responsetimes)==0: return 0
        return 1.0/np.mean(responsetimes)
    
    def __compute_selectivity_in_responsiveness(self,responsetimes):
        if 0 in responsetimes: responsetimes.remove(0)
        if len(responsetimes)==0: return 0
        return np.std(1.0/np.array(responsetimes))+0.0001
        
    
    
    # ------------------- #
    # Computate functions #
    # ------------------- #
    
    def _compute_sms_traffic(self):
        messages = self.df_sms[self.df_sms['user']==self.user]
        return {'%ssms_traffic' % self.auxlabel: len(messages)}
    
    def _compute_features_4_to_7(self):
        user_conversations = self.__compute_user_conversations()

        converser_response_times = {}
        conversations_started = 0
        conversations_count = 0

        i = 0
        for converser, conversations in user_conversations.items():

            # compute response times
            response_times = [self.__compute_conversation_response_times(c) for c in conversations] #[(907.0, 36.0), (nan, nan), (239.0, 205.0), (140.0, 50.0)]

            average_outgoing = np.mean([r[0] for r in response_times])
            average_incoming = np.mean([r[1] for r in response_times])

            converser_response_times[converser] = {'average_outgoing': average_outgoing, 'average_incoming': average_incoming}

            conversations_started += len([c for c in conversations if list(c['type'])[0] == 2])
            conversations_count += len(conversations)

            #i += 1
            #if i > 5:
            #    return converser_response_times

        # compute feature 4
        responsetimes_list = [v['average_outgoing'] for _,v in converser_response_times.items()
                               if not np.isnan(v['average_outgoing'])]
        
        overall_responsiveness = self.__compute_responsiveness_from_responsetimes(
            responsetimes_list)

        # compute feature 5
        received_responsetimes_list = [v['average_incoming'] for _,v in converser_response_times.items() 
                                        if not np.isnan(v['average_incoming'])]
        
        overall_received_responsiveness = self.__compute_responsiveness_from_responsetimes(
            received_responsetimes_list)
        
        # compute feature 6
        selectivity_in_responsiveness = self.__compute_selectivity_in_responsiveness(
            responsetimes_list)

        # compute feature 7
        fractions_of_conversations_started = conversations_started * 1.0/conversations_count

        return {'%ssms_overall_responsiveness' % self.auxlabel: overall_responsiveness, 
                '%ssms_overall_received_responsiveness' % self.auxlabel: overall_received_responsiveness, 
                '%ssms_selectivity_in_responsiveness' % self.auxlabel: selectivity_in_responsiveness, 
                '%ssms_fractions_of_conversations_started' % self.auxlabel: fractions_of_conversations_started}
    
    
    def __transform_datapoint(self,datapoint):
        instructions = {
            '%ssms_fractions_of_conversations_started' % self.auxlabel: (lambda x: x), 
            '%ssms_traffic' % self.auxlabel: (lambda x: np.log(x)), 
            '%ssms_overall_received_responsiveness' % self.auxlabel: (lambda x: np.log(x+0.00001)),
            '%ssms_overall_responsiveness' % self.auxlabel: (lambda x: np.log(x+0.00001)),
            '%ssms_selectivity_in_responsiveness' % self.auxlabel: (lambda x: np.log(x+0.00001))
        }
        
        datapoint = dict((k, instructions[k](v)) for k,v in datapoint.items())
        
        return datapoint
                        

    
    def main(self, user, transformed=True):
        if user not in self.users:
            raise Exception('User %s not in dataset' % user)
        
        self.user = user
        
        datapoint_sms = {}
        
        extractors = [self._compute_sms_traffic(), 
                      self._compute_features_4_to_7()]
        
        for i, ex in enumerate(extractors):
            if i in self.suppress:
                continue
            datapoint_sms.update(ex)
            
        if transformed:
            datapoint_sms = self.__transform_datapoint(datapoint_sms)        
        
        return datapoint_sms
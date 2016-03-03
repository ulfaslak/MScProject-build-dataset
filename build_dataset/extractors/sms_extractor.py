import pandas as pd
from collections import defaultdict
from datetime import datetime as dt
import numpy as np
import os

from build_dataset.workers import load_sensible_data as lsd
from build_dataset.workers import apply_time_constraints as atc

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
			{'[sms]_initiated_percent': 0.34782608695652173,
			 '[sms]_concluded_percent': 0.45482608695652173,
			 '[sms]_outgoing_percent': 0.68732608695652173,
			 '[sms]_chat_overlap': 0.68732608695652173,
			 '[sms]_traffic': 3.6888794541139363,
			 '[sms]_responsiveness_received': -9.0581865605306326,
			 '[sms]_responsiveness': -9.0610147611536238,
			 '[sms]_responsiveness_std': -5.4102083517105317}
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
			print "...succes! Saving."
			self.df_sms.to_pickle(ROOTPATH + '/build_dataset/data_cache/%sdf_sms.pickle' % auxlabel)
			
		else:
			# Load
			print "[sms] Loading datasource from local."
			self.df_sms = pd.read_pickle(ROOTPATH + '/build_dataset/data_cache/%sdf_sms.pickle' % auxlabel)
			self.users = set(self.df_sms['user'])
		
		print "[sms] Number of datapoints in range:", len(self.df_sms)
		
		
	# -------------------- #
	# Supporting functions #
	# -------------------- #
	
	def __partition_dyad_messages_to_chats(self, messages):
		chats = []

		timestamps = sorted(messages['timestamp']/1000)

		chat_breaks = []
		for i, _ in enumerate(timestamps):
			if i == 0:
				continue
			delta_t = timestamps[i] - timestamps[i-1]

			if delta_t > self.expiration_time * 3600:
				start_break = int(timestamps[i-1])
				end_break = int(timestamps[i])
				chat_breaks.append([start_break, end_break])

		chats = []

		if len(chat_breaks) == 0:
			chats.append(messages)
			return chats

		for i, _ in enumerate(chat_breaks):
			if i == 0:
				conv_end = chat_breaks[i][0]
				chat = messages[
					messages['timestamp']/1000 <= conv_end]
				chats.append(chat)
				continue
			if i == len(chat_breaks)-1:
				conv_start = chat_breaks[i][1]
				chat = messages[
					messages['timestamp']/1000 >= conv_start]
				chats.append(chat)
				continue

			conv_start = chat_breaks[i-1][1]
			conv_end = chat_breaks[i][0]
			chat = messages[
				messages['timestamp']/1000 >= conv_start][
				messages['timestamp']/1000 <= conv_end]

			chats.append(chat)

		return chats
	
	
	def __compute_user_chats(self, expiration_time=6):
		
		self.expiration_time = expiration_time
	
		user_messages = self.df_sms[self.df_sms['user']==self.user]

		# the people that the user texts with
		conversers = set(user_messages['address'])

		user_chats = {}

		for c in conversers:
			c_messages = user_messages[user_messages['address'] == c]

			c_chats = self.__partition_dyad_messages_to_chats(c_messages)

			user_chats[c] = c_chats

		return user_chats
	
	
	def __compute_chat_response_times(self, chat):
		chat = chat.sort(['timestamp'],ascending=[1])
		
		response_times = defaultdict(list)

		sender_prev = {}
		sender = {}

		for i, message in enumerate(chat.iterrows()):

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


		return response_time_user, response_time_converser
	

	
	def __compute_responsiveness_from_responsetimes(self,responsetimes):
		if len(responsetimes)==0: return 0
		return 1.0/np.mean(responsetimes)
	
	def __compute_responsiveness_std(self,responsetimes):
		if 0 in responsetimes: responsetimes.remove(0)
		if len(responsetimes)==0: return 0
		return np.std(1.0/np.array(responsetimes))+0.0001


	def __compute_overlap(self, chat_spans):
		# Bin
		chat_spans = sorted(chat_spans, key=lambda x: (x[0], x[1]))
		
		# Fill in empty buckets with 0s
		for i in range(24):
			if i not in hist:
				hist[i] = 0
				
		return hist
		
	
	
	# ---------- #
	# Extraction #
	# ---------- #
	
	def _compute_sms_traffic(self):
		messages = self.df_sms[self.df_sms['user']==self.user]
		return {'%s[sms]_traffic' % self.auxlabel: len(messages)}

	def _compute_outgoing_percent(self):
		messages = self.df_sms[self.df_sms['user']==self.user]
		outgoing_percent = len(messages[messages['type']==2]) * 1.0/len(messages)
		return {'%s[sms]_outgoing_percent' % self.auxlabel: outgoing_percent}
	
	def _compute_features_from_chats(self):

		converser_response_times = {}
		chats_initiated = 0
		chats_concluded = 0
		chats_count = 0
		chat_spans = []

		i = 0
		for converser, chats in self.user_chats.items():
			# compute response times
			response_times = [self.__compute_chat_response_times(c) for c in chats] #[(907.0, 36.0), (nan, nan), (239.0, 205.0), (140.0, 50.0)]

			average_outgoing = np.mean([r[0] for r in response_times])
			average_incoming = np.mean([r[1] for r in response_times])

			converser_response_times[converser] = {'average_outgoing': average_outgoing, 'average_incoming': average_incoming}

			chats_initiated += len([c for c in chats if list(c['type'])[0] == 2])
			chats_concluded += len([c for c in chats if list(c['type'])[-1] == 2])
			chats_count += len(chats)
			chat_spans.expand([(list(c['timestamp'])[0]/1000, list(c['timestamp'])[-1]/1000) for c in chats])

		# compute feature 4
		responsetimes_list = [v['average_outgoing'] for _,v in converser_response_times.items()
							   if not np.isnan(v['average_outgoing'])]
		
		responsiveness = self.__compute_responsiveness_from_responsetimes(
			responsetimes_list)

		# compute feature 5
		received_responsetimes_list = [v['average_incoming'] for _,v in converser_response_times.items() 
										if not np.isnan(v['average_incoming'])]
		responsiveness_received = self.__compute_responsiveness_from_responsetimes(
			received_responsetimes_list)
		
		# compute feature 6
	   	_responsiveness_std = self.__compute_responsiveness_std(
	   		responsetimes_list)

		# compute feature 7, 8
		initiated_percent = chats_initiated * 1.0/chats_count
		concluded_percent = chats_concluded * 1.0/chats_count

		# compute feature 9


		return {'%s[sms]_responsiveness' % self.auxlabel: responsiveness, 
				'%s[sms]_responsiveness_received' % self.auxlabel: responsiveness_received, 
				'%s[sms]_responsiveness_std' % self.auxlabel:_responsiveness_std, 
				'%s[sms]_concluded_percent' % self.auxlabel: initiated_percent,
				'%s[sms]_initiated_percent' % self.auxlabel: initiated_percent}
	
	
	def __transform_datapoint(self,datapoint):
		instructions = {
			'%s[sms]_initiated_percent' % self.auxlabel: (lambda x: x), 
			'%s[sms]_concluded_percent' % self.auxlabel: (lambda x: x), 
			'%s[sms]_traffic' % self.auxlabel: (lambda x: np.log(x)), 
			'%s[sms]_outgoing_percent' % self.auxlabel: (lambda x: x), 
			'%s[sms]_responsiveness_received' % self.auxlabel: (lambda x: np.log(x+0.00001)),
			'%s[sms]_responsiveness' % self.auxlabel: (lambda x: np.log(x+0.00001)),
			'%s[sms]_responsiveness_std' % self.auxlabel: (lambda x: np.log(x+0.00001))
		}
		
		datapoint = dict((k, instructions[k](v)) for k,v in datapoint.items())
		
		return datapoint
						
		
	def __filtering_condition(self, datapoint, feature):
		if feature in datapoint:
			if datapoint[feature] <= 0:
				raise Exception('[sms] %d %s is 0' % (self.user,feature))

	
	def main(self, user, transformed=True):
		if user not in self.users:
			raise Exception('[sms] User %s not in dataset' % user)
		
		self.user = user
		self.user_chats = self.__compute_user_chats()
		
		datapoint = {}
		
		extractors = [self._compute_outgoing_percent(),
					  self._compute_sms_traffic(),
					  self._compute_chat_features()]
		
		# Exclusion condition
		for i, ex in enumerate(extractors):
			if i in self.suppress:
				continue
			datapoint.update(ex)

		# Add filtering conditions
		self.__filtering_condition(datapoint, '%s[sms]_responsiveness_received' % self.auxlabel)
		self.__filtering_condition(datapoint, '%s[sms]_responsiveness' % self.auxlabel)
		self.__filtering_condition(datapoint, '%s[sms]_responsiveness_std' % self.auxlabel)   
			
		if transformed:
			datapoint = self.__transform_datapoint(datapoint)        
		
		return datapoint
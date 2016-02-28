# Python
from sensible_raw.loaders import loader
import numpy as np
from sklearn.preprocessing import scale
from collections import Counter, defaultdict
import sys
from datetime import datetime as dt
import json

# Feature extractors
from extractors.sms_extractor import Sms_extractor
from extractors.stop_locations_extractor import Stop_locations_extractor
from extractors.screen_extractor import Screen_extractor
##from facebook_friends_extractor import Facebook_friends_extractor
from extractors.bluetooth_extractor import Bluetooth_extractor
##from calllog_extractor import Calllog_extractor
##from location_extractor import Location_extractor
from extractors.big_five_extractor import Big_five_extractor

# Analysis
from analysis.outlier_detection import Outlier_detector_svm, Outlier_detector_kd
from analysis.location_reference import Load_location_reference
#from analysis.social_state_reference import Load_social_state_reference
from analysis.consensus_archetypes import Consensus_archetypes


class Build_dataset:
	"""Build a datamatrix for ParTI analysis, from raw.

	Parameters
	----------
	time_constraint : int
		Study/school periods (0), exam periods (1) and holiday (2)

	Return
	------
	X : numpy.ndarray
		N x M matrix, where N is users and M is traits
	Y : numpy.ndarray
		N x 5 matrix, where N is users and 5 is Big Five traits
	M : numpy.ndarray
		N x 6 matrix, where N is users and 6 is consensus archetype matching
		levels in Big Five space.
	"""


	def __init__(self,time_constrait, load_depth="shallow"):
		self.tcn = self.__time_constraint(time_constraint)
		self.tcl = "tc%d_" % time_constraint


	def __time_constraint(self, time_constraint):

		if time_constraint == 0: # School periods (when there are lectures)
			return {'hours': range(24), 'days': range(7), 'spans': [
													("06/01/14","24/01/14"), 
													("03/02/14","16/05/14"), 
													("01/09/14","05/12/14"), 
													("02/06/14","20/06/14")]}
		if time_constraint == 1: # Exam periods
			return {'hours': range(24), 'days': range(7), 'spans': [
													("17/05/14","01/06/14"), 
													("06/12/14", "21/12/14")]}
		if time_constraint == 2: # Holiday periods
			return {'hours': range(24), 'days': range(7), 'spans': [
													("01/01/14","05/01/14"), 
													("25/01/14","02/02/14"), 
													("14/04/14","20/04/14"), 
													("21/06/14","30/08/14"), 
													("22/12/14", "31/12/14")]}

	def __load_extractors(self, load_cached_data=True):

		sms = Sms_extractor(self.tcn, suppress=[], auxlabel=self.tcl, load_old_datasources=load_cached_data)
		stop_locations = Stop_locations_extractor(self.tcn, suppress=[], auxlabel=self.tcl, load_old_datasources=load_cached_data)
		screen = Screen_extractor(self.tcn, suppress=[], auxlabel=self.tcl, load_old_datasources=load_cached_data)
		##facebook_friends = Facebook_friends_extractor()
		bluetooth = Bluetooth_extractor(self.tcn, suppress=[], auxlabel=self.tcl, load_old_datasources=load_cached_data)
		##calllog = Calllog_extractor()
		##location = Location_extractor()
		big_five = Big_five_extractor()

		return sms, stop_locations, screen, bluetooth, big_five





	def __extract_userfeatures(self, load_depth):
		if load_depth=="shallow":
			with open('build_dataset/data_cache/dataset_X.json') as infile:
		        dataset_X = json.load(infile)
		    with open('build_dataset/data_cache/dataset_Y.json') as infile:
		        dataset_Y = json.load(infile)

		else:
			if load_depth=="scratch":
				sms, stop_locations, screen, bluetooth, big_five = self.__load_extractors(
					load_cached_data=False)
			elif load_depth=="deep":
				sms, stop_locations, screen, bluetooth, big_five = self.__load_extractors(
					load_cached_data=True)

			dataset_X = {}
		    dataset_Y = {}

		    for user in users:

		        if user%10 == 0:
		            print user,

		        datapoint_x = {}
		        datapoint_y = {}

		        # Ordered by fail/execution speed
		        try:
		            datapoint_x.update(bluetooth.main(user))
		            datapoint_x.update(stop_locations.main(user))
		            datapoint_x.update(sms.main(user))
		            datapoint_x.update(screen.main(user))
		            #datapoint_x.update(facebook_friends.main(user))
		            #datapoint_x.update(calllog.main(user))
		            #datapoint_x.update(location.main(user))
		            datapoint_y.update(big_five.main(user))
		        except Exception as e:
		            print "<"+str(e)+">",
		            continue

		        dataset_X[user] = datapoint_x
		        dataset_Y[user] = datapoint_y
		        
		    # Store loaded data    
		    with open('build_dataset/data_cache/dataset_X.json', 'w') as outfile:
		        json.dump(dataset_X,outfile)
		    with open('build_dataset/data_cache/dataset_Y.json', 'w') as outfile:
		        json.dump(dataset_Y,outfile)  

		return dataset_X, dataset_Y


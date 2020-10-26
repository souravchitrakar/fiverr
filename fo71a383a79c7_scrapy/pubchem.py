# -*- coding: utf-8 -*-
import scrapy
import csv
import re
import sys
import json
import os
import requests

from scrapy import signals
from pydispatch import dispatcher
from scrapy.utils.response import open_in_browser
import logging

class PubchemSpider(scrapy.Spider):
	name = 'pubchem'
	logging.basicConfig(
		filename='log.txt',
		format='%(levelname)s: %(message)s',
		level=logging.ERROR
	)
	start_urls = ['https://pubchem.ncbi.nlm.nih.gov/compound/1']
	
	CSV_TITLE = [
				"Link", "name", "Molecular Weight:", "InChI", "InChI Key", "Canonical SMILES", "Molecular Formula", 
				"cas1", "cas2", "cas3", "cas4", "deprecated cas", "EC", "IUPAC Name", "HSDB", "Wikipedia1", "wikipedia2", "pictograms", "Signal", "ECHA1", "ECHA2", "ECHA3", "ECHA4", "1HNMR", "13CNMR"
			]
			
	TITLE = ["Error Links"]
			
	download_delay = 2.0

	def __init__(self):
		dispatcher.connect(self.spider_closed, signals.spider_closed)
		self.csv_file = open("Results.csv", "w", newline='', encoding='utf-8')
		self.csv_wr = csv.writer(self.csv_file, quoting=csv.QUOTE_ALL)
		self.csv_wr.writerow(self.CSV_TITLE)
		
		self.csv_file = open("Error_links.csv", "w", newline='', encoding='utf-8')
		self.csv_err = csv.writer(self.csv_file, quoting=csv.QUOTE_ALL)
		self.csv_err.writerow(self.TITLE)
		
	def spider_closed(self, spider):
		self.csv_file.close()
	
	def start_requests(self):
		for i in range(1, 151):
			Response_URL = "https://pubchem.ncbi.nlm.nih.gov/compound/" + str(i)
			json_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/" + str(i) + "/JSON/"
			rq = scrapy.Request(json_url, callback=self.parse)
			rq.meta['Response_URL'] = Response_URL
			yield rq
			
	def parse(self, response):
		Link = response.meta['Response_URL']
		if response.status != 200:
			self.csv_err.writerow([Link])
		else:
			print ('Scraping URL =>{} and response status {}'.format(response.url, response.status))
		print ("Scraping URL =>", response.url)
		Link = response.meta['Response_URL']
		data = json.loads(response.text)
		name = data['Record']['RecordTitle']
		Molecular_Weight = []
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for secs in sections['Section']:
					if 'Section' in secs:
						for sect in secs['Section']:
							for (key, value) in sect.items():
								if 'Molecular Weight' in value:
									for info in sect['Information']:
										MolecularWeight = str(info['Value']['Number'][0]) + ' ' + str(info['Value']['Unit'])
										Molecular_Weight.append(MolecularWeight)
		if Molecular_Weight:
			Molecular_Weight = Molecular_Weight[0]
		else:
			Molecular_Weight = ''
										
		InChI = []
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for secs in sections['Section']:
					if 'Section' in secs:
						for (key, value) in secs.items():
							if 'Computed Descriptors' in value:
								for sect in secs['Section']:
									for (key, value) in sect.items():								
										if 'International Chemical Identifier (InChI)' in value:
											for info in sect['Information']:
												for string in info['Value']['StringWithMarkup']:
													InChI_ = string['String']
													InChI.append(InChI_)
		if InChI:
			InChI = InChI[0]
		else:
			InChI= ''
		
		InChI_Key = []
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for secs in sections['Section']:
					if 'Section' in secs:
						for (key, value) in secs.items():
							if 'Computed Descriptors' in value:
								for sect in secs['Section']:
									for (key, value) in sect.items():								
										if 'InChI Key' in value:
											for info in sect['Information']:
												for string in info['Value']['StringWithMarkup']:
													InChIKey = string['String']
													InChI_Key.append(InChIKey)
		if InChI_Key:
			InChI_Key = InChI_Key[0]
		else:
			InChI_Key= ''
			
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for secs in sections['Section']:
					if 'Section' in secs:
						for (key, value) in secs.items():
							if 'Computed Descriptors' in value:
								for sect in secs['Section']:
									for (key, value) in sect.items():								
										if 'Canonical SMILES' in value:
											for info in sect['Information']:
												for string in info['Value']['StringWithMarkup']:
													Canonical_SMILES = string['String']

			
			
		Molecular_Formula = []
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for secs in sections['Section']:
					for (key, value) in secs.items():
						if 'Molecular Formula' in value:
							for sect in secs['Information']:
								for string in sect['Value']['StringWithMarkup']:
									MolecularFormula = string['String']
									Molecular_Formula.append(MolecularFormula)
									
		if Molecular_Formula:
			Molecular_Formula = Molecular_Formula[0]
		else:
			Molecular_Formula= ''
			
		d_cas = []
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for (key, value) in sections.items():
					if 'Names and Identifiers' in value:
						for secs in sections['Section']:
							for (key, value) in secs.items():
								if 'Other Identifiers' in value:
									for sect in secs['Section']:
										for (key, value) in sect.items():
											if 'Deprecated CAS' in value:
												for info in sect['Information']:
													for string in info['Value']['StringWithMarkup']:
														dep_cas = string['String']
														d_cas.append(dep_cas)
		if d_cas:
			d_cas = [d_cas[0]]
		else:
			d_cas = ''
			
		ec = []
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for (key, value) in sections.items():
					if 'Names and Identifiers' in value:
						for secs in sections['Section']:
							for (key, value) in secs.items():
								if 'Other Identifiers' in value:
									for sect in secs['Section']:
										for (key, value) in sect.items():
											if 'European Community (EC) Number' in value:
												for info in sect['Information']:
													for string in info['Value']['StringWithMarkup']:
														ec_num = string['String']
														ec.append(ec_num)
		if ec:
			ec = [ec[0]]
		else:
			ec = ''
			
		cas = []
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for (key, value) in sections.items():
					if 'Names and Identifiers' in value:
						for secs in sections['Section']:
							for (key, value) in secs.items():
								if 'Other Identifiers' in value:
									for sect in secs['Section']:
										for (key, value) in sect.items():								
											if 'Chemical Abstracts Service (CAS)' in value:
												for info in sect['Information']:
													for string in info['Value']['StringWithMarkup']:
														cas_number = string['String']
														cas.append(cas_number)
		if cas:
			cas1 = [cas[0]]
		else:
			cas1 = ''
		if len(cas) >= 2:
			cas2 = [cas[1]]
		else:
			cas2 = ''
		if len(cas) >= 3:
			cas3 = [cas[2]]
		else:
			cas3 = ''	
		if len(cas) >= 4:
			cas4 = [cas[3]]
		else:
			cas4 = ''
			
		IUPAC_Name = []
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for (key, value) in sections.items():
					if 'Names and Identifiers' in value:
						for secs in sections['Section']:
							for (key, value) in secs.items():
								if 'Computed Descriptors' in value:
									for sect in secs['Section']:
										for (key, value) in sect.items():								
											if 'UPAC Name' in value:
												for info in sect['Information']:
													for string in info['Value']['StringWithMarkup']:
														IUPAC = string['String']
														IUPAC_Name.append(IUPAC)
		if IUPAC_Name:
			IUPAC_Name = IUPAC_Name[0]
		else:
			IUPAC_Name= ''
		HSDB = ''												
		for sections in data['Record']['Reference']:
			for (key, value) in sections.items():
				if 'SourceName' in key and 'HSDB' in value:
					HSDB = sections['SourceID']

		
		Wikipedia = []
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for (key, value) in sections.items():
					if 'TOCHeading' in key and 'Names and Identifiers' in value:
						for secs in sections['Section']:
							for (key, value) in secs.items():
								if 'TOCHeading' in key and 'Other Identifiers' in value:
									for sect in secs['Section']:
										for (key, value) in sect.items():								
											if 'TOCHeading' in key and 'Wikipedia' in value:
												for info in sect['Information']:
													wiki = info['URL']
													Wikipedia.append(wiki)
		if Wikipedia:
			Wikipedia1 = Wikipedia[0]
		else:
			Wikipedia1 = ''
		if len(Wikipedia) == 2:
			wikipedia2 = Wikipedia[1]
		else:
			wikipedia2 = ''
			
		ECHA = []	
		for sections in data['Record']['Reference']:
			for (key, value) in sections.items():
				if 'SourceName' in key and 'ECHA' in value:
					ECHA_No = sections['SourceID']
					ECHA.append(ECHA_No)
		if ECHA:
			ECHA1 = [ECHA[0]]
		else:
			ECHA1 = ''
		if len(ECHA) >= 2:
			ECHA2 = [ECHA[1]]
		else:
			ECHA2 = ''
		if len(ECHA) >= 3:
			ECHA3 = [ECHA[2]]
		else:
			ECHA3 = ''	
		if len(ECHA) >= 4:
			ECHA4 = [ECHA[3]]
		else:
			ECHA4 = ''
		
		Signal = []
		for sections in data['Record']['Section']:
			for (key, value) in sections.items():
				if 'TOCHeading' in key and 'Safety and Hazards' in value:
					for secs in sections['Section']:
						for (key, value) in secs.items():
							if 'Hazards Identification' in value:
								for sect in secs['Section']:
									for (key, value) in sect.items():
										if 'GHS Classification' in value:
											for info in sect['Information']:
												for (key, value) in info.items():
													if 'Name' in key and 'Signal' in value:
														for string in info['Value']['StringWithMarkup']:
															Signal = string['String']
		if Signal:
			Signal = Signal
		else:
			Signal = ''
			
		Pictograms = []
		for sections in data['Record']['Section']:
			for (key, value) in sections.items():
				if 'TOCHeading' in key and 'Chemical Safety' in value:
					for info in sections['Information']:
						if 'StringWithMarkup' in info:
							for string in info['Value']['StringWithMarkup']:
								if 'Markup' in string:
									for markup in string['Markup']:
										Pictogram = markup['URL']
										Pictogram = str(Pictogram).replace('https://pubchem.ncbi.nlm.nih.gov/images/ghs/','').replace('.svg','')
										Pictograms.append(Pictogram)
									
		if Pictograms:
			Pictograms = Pictograms
		else:
			Pictograms = ''

		CNMR = set([])
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for secs in sections['Section']:
					if 'Section' in secs:
						for (key, value) in secs.items():
							if '1D NMR Spectra' in value:
								for sect in secs['Section']:
									for (key, value) in sect.items():
										if '13C NMR Spectra' in value:
											for info in sect['Information']:
												if 'URL' in info:
													url = info['URL'].split('/')[-1]
													CNMR.add(url)

		CNMR = '|'.join([str(elem) for elem in list(CNMR)])

		HNMR = set([])
		for sections in data['Record']['Section']:
			if 'Section' in sections:
				for secs in sections['Section']:
					if 'Section' in secs:
						for (key, value) in secs.items():
							if '1D NMR Spectra' in value:
								for sect in secs['Section']:
									for (key, value) in sect.items():
										if '1H NMR Spectra' in value:
											for info in sect['Information']:
												if 'URL' in info:
													url = info['URL'].split('/')[-1]
													HNMR.add(url)

		HNMR = '|'.join([str(elem) for elem in list(HNMR)])	
			
		data = [
			Link,
			name,
			Molecular_Weight,
			InChI,
			InChI_Key,
			Canonical_SMILES,
			Molecular_Formula,
			cas1,
			cas2,
			cas3,
			cas4,
			d_cas,
			ec,
			IUPAC_Name,
			HSDB,
			Wikipedia1,
			wikipedia2,
			Pictograms,
			Signal,
			ECHA1,
			ECHA2,
			ECHA3,
			ECHA4,
			HNMR,
			CNMR
		]

		print ('output data saved into Results.csv => ', data)
		self.csv_wr.writerow(data)

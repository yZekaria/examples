import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt 

years = range(2012,2020)


"""
Burning Glass filters using keyword search:
Education (Minimum Advertised)
Experience
Industries
Job Titles
Occupations (BGTOCCs)
Salary (Advertised)
Skills
Skill Clusters
Skills by Occupation
Skills by Industry
"""


def numPostings(years):
	"""
	Function to read in number of job postings 
	"""
	count = []
	for year in years:
		filename = "SmartEnergy" +str(year) +".xlsx"
		DB = pd.read_excel(filename, sheet_name = 'Filters')
		count.append(DB.iloc[10][1])
	return count




def topOccupations(years):
	"""
	Function to collect top occupations 
	"""
	occs = []
	for year in years:
		filename = "SmartEnergy" +str(year) +".xlsx"
		DB = pd.read_excel(filename, sheet_name= "Report1_Data", usecols =["BGTOCC","Job Postings"])
		# occs.append(DB.head(5))
		occs.append(DB)
		TopOccs =pd.concat(occs, keys = list(years), names =['year'])
	
	# Which occupations appear throughout the years, which are new and which no longer appear?
	
	
	v = TopOccs.BGTOCC.value_counts().sort_index()	
	
	# create list of occupations that are posted each year
	recurringOccs = v[v==8].index.tolist()
	
	return TopOccs
	# emergingOccs = 
	# print(TopOccs.loc[2012,:])




def skills_per_occupation(years):

	frames = []
	for year in years:
		
		filename = "SmartEnergy" +str(year) +".xlsx"
		
		DB = pd.read_excel(filename, sheet_name= "Report10_Data", usecols =["BGTOCC","Job Postings"])
		#skills are listed in same column as occupation. 
		# where number of postings increases, a new occupation is listed.
		# check where occupation occurs by calling occupation function
		topOccs = topOccupations([str(year)])
		
		# print(DB.loc[np.where(DB['BGTOCC'].isin(topOccs['BGTOCC']))])	# DB to have first column as occupation with multi rows for skills for each year in columns
		# from index 1, make an array with the length of each interval as that occupation that many times
		positions = np.where(DB['BGTOCC'].isin(topOccs['BGTOCC']))[0]
		
		occ_index = []

		# add all the occupations to a list occ_index for the number of skills they relate to
		for x in range(len(positions)-1):
			occ_index.append([DB.loc[positions[x]]['BGTOCC'] for ii in range(positions[x],positions[x+1]-1)])

		# add last occupation  --- to avoid index error occuring in loop above
		occ_index.append([DB.loc[positions[-1]]['BGTOCC'] for ii in range(positions[-1],len(DB)-1)])

		# convert list to an array
		occ_index = np.array(sum(occ_index,[]))

		# drop the entries where the occupation is listed in the skills column
		DB=DB.drop(positions)

		# create array with the occupations and skills (skills listed in column titled BGTOCC)
		arrays = [occ_index, DB['BGTOCC'].values]
		tuples = list(zip(*arrays))
		
		index = pd.MultiIndex.from_tuples(tuples,names = ['Occupation','Skill'])
		skills_per_occ = pd.DataFrame(DB['Job Postings'].values, index = index, columns = ['Job Postings'])
	
		frames.append(skills_per_occ)

	skills_per_occ_total =pd.concat(frames, keys = [str(year) for year in years])

	# print(skills_per_occ_total)
	# print(skills_per_occ_total.loc['2012',:])
	

	#we want to find the skills required for relevant occupations and the difference in skills for these occupations generally

def topIndustries(years):
	top_SIC_dict = {}
	code_ref = pd.DataFrame(columns = ['SIC code', 'Industry'])
	for year in years:
		filename = "SmartEnergy" +str(year) +".xlsx"
		DB = pd.read_excel(filename, sheet_name= "Report4_Data", usecols =["SIC code","Industry"])
		# make dictionary of top industry codes for each year
		top_SIC_dict["{0}".format(year)] = DB['SIC code'].values
		code_ref = code_ref.append(DB, ignore_index ='True')

	# creates a list of all industries and their codes over the years
	code_frequency = code_ref.drop_duplicates(ignore_index=True)

	# make dictionary of codes per year into dataframe and fill empty rows with NaN value
	top_SIC = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in top_SIC_dict.items() ]))

	# for each year, for each code in SIC code in code_ref, insert value of 1 if in top_SIC
	for year in years:
		code_frequency[str(year)] = 0
		# read in csv sheet
		filename = "SmartEnergy" + str(year) + ".xlsx"
		DB = pd.read_excel(filename, sheet_name= "Report4_Data", usecols =["SIC code","Industry", "Job Postings"])
		
		# create dictionary of number of postings per code
		mapping = dict(zip(DB["SIC code"],DB["Job Postings"]))

		# add column to dataframe for the year with the relevant number of job postings in each industry
		code_frequency[str(year)] = code_frequency["SIC code"].map(mapping)
		# code_frequency[str(year)] = np.where(code_frequency['SIC code'].isin(top_SIC[str(year)]), True, False)
	
	code_frequency = code_frequency.fillna(0)
	# code_frequency.to_csv('top_industries.csv')




def skillClusters(years):
	skill_frequency = pd.DataFrame(columns = ['Cluster']+list(years))
	top_clusters_list = []	
	
	for year in years:
		filename = "SmartEnergy" +str(year) +".xlsx"
		DB = pd.read_excel(filename, sheet_name= "Report7_Data", usecols =["Skill Cluster","Job Postings"])
		top_clusters_list.extend(DB['Skill Cluster'].values)
	
	#remove duplicates and make into dataframe
	top_clusters = pd.DataFrame(list(dict.fromkeys(top_clusters_list)), columns = ['Skill Cluster'])
	
	# record how many postings for each skill over the years
	for year in years:
		top_clusters[str(year)] = 0
		filename = "SmartEnergy" +str(year) +".xlsx"
		DB = pd.read_excel(filename, sheet_name= "Report7_Data", usecols =["Skill Cluster","Job Postings"])
		# top_clusters[year] = np.where(top_clusters['Skill Cluster'].isin(DB['Skill Cluster']), True, 0)
		# top_clusters[str(year)].loc[(top_clusters['Skill Cluster'].isin(DB['Skill Cluster']))] = 'x'

		#where skill cluster from DB == skill cluster from top_clusters, add job posting from db, else add 0
		mapping = dict(zip(DB['Skill Cluster'], DB['Job Postings']))
		top_clusters[str(year)] = top_clusters['Skill Cluster'].map(mapping)
	top_clusters.to_csv('skill_clusters.csv')




skills_per_occupation(years)

# skillClusters(years)

# topIndustries(years)


# topOccupations(years)





# count = numPostings(years)
# plt.plot(years,count)
# plt.grid(b=True)
# plt.title('Number of postings under Smart Energy keyword')
# plt.xlabel('Year')
# plt. ylabel('Number of postings')
# plt.show()

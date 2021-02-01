features_translations = {
	'__class__': ['класс', 'классa', 'классов'],
	'contrast': ['контраст', 'контраста', 'контрастов']
}
def presentFilter(f):
	result = []
	for feature in f:
		feature_result = features_translations[feature][1 if len(f[feature]) == 1 else 2] + ' '
		feature_subresults = []
		for v in f[feature]:
			if isinstance(v, dict):
				if ('from' in v) and ('to' in v):
					feature_subresults.append('от ' + str(v['from']) + ' до ' + str(v['to']))
				else:
					if 'from' in v:
						feature_subresults.append('от ' + str(v['from']))
					if 'to' in v:
						feature_subresults.append('до ' + str(v['to']))
			else:
				feature_subresults.append(str(v))
		feature_result += ' или '.join(feature_subresults)
		result.append(feature_result)
	result = ', '.join(result)
	if result == '':
		return 'с любыми аннотациями'
	else:
		return result
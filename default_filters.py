def filters(classes):
	return [{
		'__class__': [[c] for c in classes]
	}]
with open('D:\\datasets\\CelebA\\list_attr_celeba.csv') as f:
	f.readline()
	print(f.readline())
	for line in f:
		print(line)
		exit()
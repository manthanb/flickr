from sklearn.cluster import KMeans
import sklearn.metrics as metrics

# calculate dot product of two vectors
def dot_product(v1, v2):

	# return error if the vectors are empty
	if (len(v1) <= 0) or (len(v2) <= 0):
		return "one or both vectors are empty", None

	# return error if the lengths of vectors are different
	if len(v1) != len(v2):
		return "the lenghts of two vectors are not same", None

	# calculate dot product: x1.y1 + x2.y2 + ... + xn.yn
	element_count = 0
	dot_product = 0
	while element_count < len(v1):
		prod = v1[element_count] * v2[element_count]
		dot_product = dot_product + prod
		element_count = element_count + 1
	return None, dot_product

# calculaye the length of a vector
def length(v):

	# return error if the vector is empty
	if len(v) <= 0: 
		return "vector is empty", None

	# calculate x1^2 + x2^2 + ... + xn^2
	length = 0
	for element in v:
		prod = pow(element, 2)
		length = length + prod

	# take square root (by definition)
	length = pow(length, 1/2)

	return None, length


# calculate euclidean distance between two vectors
def euclidean_distance(v1, v2):
	
	# return error if the vectors are empty
	if (len(v1) <= 0 ) or (len(v2) <= 0):
		return "one or both vectors are empty", None

	# return error if the lengths of vectors are different
	if len(v1) != len(v2):
		return "the lenghts of two vectors are not same", None

	# calculate the sum of sqaures of the difference of all corresponding features
	# (x1 - y1)^2 + (x2 - y2)^2 .... + (xn - yn)^2
	element_count = 0
	distance = 0
	while element_count < len(v1):
		difference = pow(v1[element_count] - v2[element_count], 2)
		distance = distance + difference
		element_count = element_count + 1

	# calculate square root of the sum. this is our distance
	distance = pow(distance, 1/2)

	return None, distance


# calculate cosine similarity between two vectors
def cosine_similarity(v1, v2):

	# return error if the vectors are empty
	if (len(v1) <= 0) or (len(v2) <= 0):
		return "one or both vectors are empty", None

	# return error if the lengths of vectors are different
	if len(v1) != len(v2):
		return "the lenghts of two vectors are not same", None

	# calculate cosine similarity
	# (v1.v2) / (|v1|*|v2|)
	error, numerator = dot_product(v1, v2)
	error, length_v1 = length(v1)
	error, length_v2 = length(v2)
	denominator = length_v1 * length_v2
	similarity = numerator / denominator

	return None, similarity

# clusters given vectors into 'k' clusters
def kmeans(vectors):

	# return error if the vectors are empty
	if (len(vectors) <= 0):
		return "no vectors found", None

	# calculte the minimum silhoutte score for k: [2, 99]
	min = 10
	k = -1
	for i in range(2, 100):
		kmeans_model = KMeans(n_clusters=i, random_state=1).fit(vectors)
		labels = kmeans_model.labels_
		silhouette_score = metrics.silhouette_score(vectors, labels, metric='euclidean')
		if silhouette_score < min:
			min = silhouette_score
			k = i

	# create and return clusters
	kmeans = KMeans(n_clusters=k, random_state=0).fit(vectors)
	return None, list(kmeans.cluster_centers_)



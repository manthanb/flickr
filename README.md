# flickr

<b>1. Problem Specification</b>

Informal definitions often build intuitions more easily. Hence, we first look at an informal description of our goal and then define it more formally later.

<I>Given a set of documents D, a new document d, and a number k, find the k most similar documents to d from set D.</I>

One read of the above definition is enough to comprehend that the given task is of information retrieval wherein we need to ‘compare’ document d with all the documents in set D and ‘measure' the ‘similarity’ of each comparison. The formal problem specification will extend this idea and outline the goals in greater detail.

More formally, there are five goals(tasks) that are implemented in the proposed solution, each of which can be described as follows
  1. Implement a program which, given a user ID, a model (TF, DF, TF-IDF), and value “k”, returns the most similar k users based on textual descriptors. For each match, also list the overall matching score as well as the 3 terms that have the highest similarity contribution.
  2. Implement a program which, given an image ID, a model (TF, DF, TF-IDF), and value “k”, returns the most similar k images based on textual descriptors. For each match, also list the overall matching score as well as the 3 terms that have the highest similarity contribution.
  3. Implement a program which, given a location ID, a model (TF, DF, TF-IDF), and value “k”, returns the most similar k locations based on textual descriptors. For each match, also list the overall matching score as well as the 3 terms that have the highest similarity contribution.
  4. Implement a program which, given a location ID, a model (CM, CM3x3, CN, CN3x3,CSD,GLRLM, GLRLM3x3, HOG,LBP, LBP3x3), and value “k”, returns the most similar k locations based on the corresponding visual descriptors of the images as specified in the “img” folder. For each match, also list the overall matching score as well as the 3 image pairs that have the highest similarity contribution.
  5. Implement a program which, given a location ID and value “k”, returns the most similar k locations based on the corresponding visual descriptors of the images as specified in the “img” folder. For each match, also list the overall matching score and the individual contributions of the 10 visual model

Here, the different models are examples of different feature calculation measures.

<b>2. Data Preprocessing</b>

To make document matching faster, it is sometimes helpful to preprocess the raw data and store it in a format that can be queried quickly. Following are the data-schemas that are used to store pre-processed data:

• The data for users, images and locations are stored in the following format. Each document has an ID and a features associated with it. Each feature in turn has a global index and TF, DF and TF-IDF weights. Also each document has a feature vector for all the models.

The decision for making such a structure comes from the fact that if we have available the feature vector for each document, computing similarities during querying becomes as simple as computing similarity between two feature vectors(for all documents)

• A similar kind of structure is followed for visual descriptors. However, as the visual descriptors already have been vectorised, the vectors are directly stored into database.
• To reduce the computation complexity during querying, for each location in each model, documents are clustered. To better understand how clustering will help reduce computation time, given below is an example:

Let number of images in location1 = m Let number of images in location2 = n
Therefore, the number of computations required = m * n
However, if the documents in location1 are clustered to form k(<m) cluster centres and the documents in location2 are clustered to from l(<n) cluster centres,

  <i>The number of computations(between centres) = k * l ( < m*n )</i>

• This gives us yet another collection - a collection of cluster centres. The cluster centres are stored model wise i.e. in a collection of model CM, each document will be a location and will have its corresponding cluster centres. The structure of a document in this collection is shown in Fig3.
• Silhouette analysis: While clustering documents, choosing the optimum number of clusters is of utmost importance. Silhouette analysis can be used to study the separation distance between the resulting clusters. The silhouette plot displays a measure of how close each point in one cluster is to points in the neighbouring clusters and thus provides a way to assess parameters like number of clusters visually. This measure has a range of [-1, 1]
• The silhouette score can be calculated using the following formula

  <i>S(i) = (b(i) − a(i)) ÷ max{a(i),b(i)}</i>

Where a(i) is the average distance between i and all other data points in the cluster and
b(i) is the smallest average distance of i to all points in any other cluster. 2.2 Calculating similarity and ranks

The algorithms that this solution uses to rank using textual and visual descriptors are different. Hence, in this sub-section, they are both explained separately.

<b> 3. Similarity Calculation </b>

<b>Textual Descriptors</b>

As noted in the previous section, we are already storing feature vectors in each document and for each textual descriptor. Hence, when a query document and a textual descriptor(model) is given, the feature vector of query document is compared with the feature vector of all other documents in the database, and a similarity score is assigned for each comparison.

For assigning this similarity score, we are using cosine similarity measure. The reasons behind this choice are listed as follows:
• Consider a two-class classification problem where the classes are “Phoenix” and “New York City”. Web pages related to Phoenix fall under the first class and the same can be said for New York City. When a new document arrives and it has keywords like “Empire State building” and “Brooklyn bridge”, the ideal case will be to classify it as of class 2. Cosine similarity performs better in this case as it checks how generally “inclined” a document is towards each class
• The other advantage of cosine similarity is that the features that have a value of 0 do not contribute in overall similarity contribution. Hence, these terms can be ignored. This property can be very helpful in compressing sparse matrices.

After the similarity of each document pair is calculated, the top ‘k’ documents with maximum similarity are returned. Furthermore, the contribution of each individual feature pair will be the product of their feature values.

<b>Visual Descriptors</b>

In the case of calculating similarity using visual descriptors, there are two different cases(task 4 and task 5). As each of them use a slightly different technique, they are both described separately.

<b>Case 1 - Given location ID and model:</b>

In this case, the computation is similar to that of textual descriptors. The cluster centres of given location are compared with the cluster centres of all other locations and a similarity score is calculated. The location pairs are ordered by their similarity scores and the top ‘k’ are selected.

However, there is one major difference. Instead of using a similarity measure, we are using a distance measure - the Euclidean distance - to rank location pairs. As the feature vectors are not sparse and already normalised, the use of Euclidean distance is justified. Therefore, the location pairs with least distance are considered to be most similar.

After top ‘k’ most similar documents are retrieved, each of their images are compared with the query document’s image to get the highest contributing images for each comparison. In this way, the loss in data due to clustering is partially compensated.

<b>Case 2 - Given only location ID:</b>

As we do not have a model for this case, computing similarities(distances) for each model follows intuition. However, the number of ways to rank these documents are many.
After each location pair for each model has a distance score, we sort the locations in each model.

The total similarity of each document is calculated as the sum of each of their ranks. Therefore, similarity(doc_1) = 3 and similarity(doc_2) = 3
The top ‘k’ most similar documents are then returned.

<b>4. Installation</b>

Install Python3 from: https://realpython.com/installing-python/

Install MongoDB from: https://docs.mongodb.com/manual/installation/
	
Installing Dependencies and starting database server: Run the following commands in terminal

	mongod
	pip3 install scipy
	pip3 install sklearn
	pip3 install numpy
	export PYTHONPATH=“${PYTHONPATH}:/path/to/project“

Configuration: 

	1. In the project folder, open /path/to/project/config/config.ini
	2. Change the values of keys under [Data] section and point them to absolute paths where actual data files are 

--------------------------------------------------------------------------------------------------------------------------------

<b>5. Running the file</b>

	python3 init.py
	python3 main.py

--------------------------------------------------------------------------------------------------------------------------------

<b>6. Project Structure</b>

	(i) init.py file is used to read dataset from text file and load it to mongoDB

	(ii) main.py file runs the interactive interface that can take input and displace output

	(iii) config directory has a config.ini file for app wide configuration and a config-parser.ini file that has functions to read value from config file. Onlye the config-parser is to be imported

	(iv) lib directory contains the libraries - math.py and db.py

	(v) similarity directory is where files that calculate similarity are. similarity/textual_similarity.py has functions to calculate similarity for the first three tasks and similarity/visual_similarity.py has functions to calculate similarities for tasks 4 and 5. both these files can be individually tested by calling runner() function in them

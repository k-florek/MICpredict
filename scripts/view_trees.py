from sklearn.tree import export_graphviz
import pickle
import os
import pydotplus
from IPython.display import Image  

with open("/home/floreknx/Documents/SaloMic/app/rf_model.sav",'rb') as model_file:
	clf = pickle.load(model_file)

c=0
for tree in clf.estimators_:
	dot_data = export_graphviz(tree,
				out_file = None,
class_names=["AMOC","AMOC_MIC","AMP","AMP_MIC","AZIT","AZIT_MIC","CEFO","CEFO_MIC","CEFTR","CEFTR_MIC","CEFTX","CEFTX_MIC","CHLOR","CHLOR_MIC","CIP","CIP_MIC","GENT","GENT_MIC","NAL","NAL_MIC","STREP","STREP_MIC","SULF","SULF_MIC","TETR","TETR_MIC","TRIM","TRIM_MIC"],
                filled=True,
                rounded=True)
	graph = pydotplus.graph_from_dot_data(dot_data)
	Image(graph.create_png())
	graph.write_pdf(f"tree{c}.pdf")
	c += 1

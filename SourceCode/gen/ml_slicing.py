import os
import numpy as np
import pandas as pd
import heapq
from collections import Counter
import sklearn.gaussian_process as gp
from scipy.stats import norm
from scipy.optimize import minimize
import sklearn

from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
#from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.neighbors import KNeighborsClassifier
#from sklearn.gaussian_process.kernels import RBF
#from sklearn.gaussian_process.kernels import Matern
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.metrics.pairwise import cosine_similarity
from nltk.classify.scikitlearn import SklearnClassifier
import matplotlib.pyplot as plt

data=pd.read_csv("../input/slicing_svc_data_half_new.txt", header=None, delimiter="\t")
xtrain = data.iloc[0:1897224, 3:32]
ytrain = data.iloc[0:1897224, 32]
xtest = data.iloc[1897225:, 3:32]
ytest = data.iloc[1897225:, 32]


############################## BERNOULLI NAIVE BAYES ##########################

bnb = BernoulliNB(binarize=0.0)
bnb.fit(xtrain,ytrain)
pred11=bnb.predict(xtest)
bnb_accuracy = accuracy_score(ytest,pred11)
print(bnb_accuracy)

y_pred_proba = bnb.predict_proba(xtest)[::,1]

fpr, tpr, _ = sklearn.metrics.roc_curve(ytest,  y_pred_proba)

auc = sklearn.metrics.roc_auc_score(ytest, y_pred_proba)
plt.plot(fpr,tpr,label="auc="+str(auc))
plt.legend(loc=4)
plt.show()




############################# LINEAR SVC ######################################
clf_linear_svc = LinearSVC(random_state=0, tol=1e-5)
clf_linear_svc.fit(xtrain,ytrain)
pred12=clf_linear_svc.predict(xtest)
linear_svc_accuracy = accuracy_score(ytest,pred12)
print(linear_svc_accuracy)


# lsc = SklearnClassifier(SVC(kernel='linear',probability=True))
# y_pred_proba = lsc.predict_proba(xtest)[::,1]

# fpr, tpr, _ = sklearn.metrics.roc_curve(ytest,  y_pred_proba)

# auc = sklearn.metrics.roc_auc_score(ytest, y_pred_proba)
# plt.plot(fpr,tpr,label="auc="+str(auc))
# plt.legend(loc=4)
# plt.show()



#######################      LINEAR DISCRIMINANT ANALYSIS                   ################################################

ldac = LinearDiscriminantAnalysis()
ldac.fit(xtrain,ytrain)
pred13 = ldac.predict(xtest)
lda_accuracy = accuracy_score(ytest,pred13)
print("linear DISCRIMINANT ANALYSIS ACCURACY IS ",lda_accuracy)



y_pred_proba = ldac.predict_proba(xtest)[::,1]

fpr, tpr, _ = sklearn.metrics.roc_curve(ytest,  y_pred_proba)

auc = sklearn.metrics.roc_auc_score(ytest, y_pred_proba)
plt.plot(fpr,tpr,label="auc="+str(auc))
plt.legend(loc=4)
plt.show()




########################################################################




# #################################################### SUPPORT VECTOR CLASSIFIER(NON-LINEAR) #################################
#
#clf_svc = SVC(gamma='auto')
#clf_svc.fit(xtrain, ytrain)
#pred1 = clf_svc.predict(xtest)
#svc_accuracy = accuracy_score(ytest, pred1)
#print("SVC ACCURACY IS : ",svc_accuracy)
#
#
# ################################################### RANDOM FOREST CLASSIFIER ###################################
#
clf_rfc = RandomForestClassifier(n_estimators=100, max_depth=2, random_state=0)
clf_rfc.fit(xtrain, ytrain)
pred2 = clf_rfc.predict(xtest)
rfc_accuracy = accuracy_score(ytest, pred2)
print("RANDOM FOREST ACCURACY IS: ",rfc_accuracy)



y_pred_proba = clf_rfc.predict_proba(xtest)[::,1]

fpr, tpr, _ = sklearn.metrics.roc_curve(ytest,  y_pred_proba)

auc = sklearn.metrics.roc_auc_score(ytest, y_pred_proba)
plt.plot(fpr,tpr,label="auc="+str(auc))
plt.legend(loc=4)
plt.show()

#
#
# #################################################### DECISION TREE CLASSIFIER ######################################
clf_dtc =  DecisionTreeClassifier(max_depth=5)
clf_dtc.fit(xtrain,ytrain)
pred3 = clf_dtc.predict(xtest)
dtc_accuracy = accuracy_score(ytest,pred3)
print("DECISION TREE ACCURACY IS: ",dtc_accuracy)





y_pred_proba = clf_dtc.predict_proba(xtest)[::,1]

fpr, tpr, _ = sklearn.metrics.roc_curve(ytest,  y_pred_proba)

auc = sklearn.metrics.roc_auc_score(ytest, y_pred_proba)
plt.plot(fpr,tpr,label="auc="+str(auc))
plt.legend(loc=4)
plt.show()

#
#
# ################################################## GAUSSIAN PROCESS RBF CLASSIFIER #################################
#
# # clf_gpc =  GaussianProcessClassifier(1.0 * RBF(1.0))
# # clf_gpc.fit(xtrain,ytrain)
# # pred4 = clf_gpc.predict(xtest)
# # gpc_accuracy = accuracy_score(ytest,pred4)
# # print("GAUSSIAN PROCESS ACCURACY IS: ",gpc_accuracy)
#
# ################################################ GAUSSIAN NAIVE BAYES CLASSIFIER ###################################
#
clf_gnb = GaussianNB()
clf_gnb.fit(xtrain,ytrain)
pred5 = clf_gnb.predict(xtest)
gnb_accuracy = accuracy_score(ytest,pred5)
print("GAUSSIAN NAIVE BAYES ACCURACY IS: ",gnb_accuracy)




y_pred_proba = clf_gnb.predict_proba(xtest)[::,1]

fpr, tpr, _ = sklearn.metrics.roc_curve(ytest,  y_pred_proba)

auc = sklearn.metrics.roc_auc_score(ytest, y_pred_proba)
plt.plot(fpr,tpr,label="auc="+str(auc))
plt.legend(loc=4)
plt.show()

#
# ################################################# ADABOOST CLASSIFIER ##############################################
clf_abc = AdaBoostClassifier()
clf_abc.fit(xtrain,ytrain)
pred6 = clf_abc.predict(xtest)
abc_accuracy = accuracy_score(ytest,pred6)
print("ADABOOST ACCURACY IS: ",abc_accuracy)




y_pred_proba = clf_abc.predict_proba(xtest)[::,1]

fpr, tpr, _ = sklearn.metrics.roc_curve(ytest,  y_pred_proba)

auc = sklearn.metrics.roc_auc_score(ytest, y_pred_proba)
plt.plot(fpr,tpr,label="auc="+str(auc))
plt.legend(loc=4)
plt.show()

#
#
# #################################################### XGBOOST CLASSIFIER   ##########################################
#
xgbc = XGBClassifier()
xgbc.fit(xtrain, ytrain)
pred7 = xgbc.predict(xtest)
xgb_accuracy= accuracy_score(ytest, pred7)
print("XGBOOST ACCURACY IS: ",xgb_accuracy)



y_pred_proba = xgbc.predict_proba(xtest)[::,1]

fpr, tpr, _ = sklearn.metrics.roc_curve(ytest,  y_pred_proba)

auc = sklearn.metrics.roc_auc_score(ytest, y_pred_proba)
plt.plot(fpr,tpr,label="auc="+str(auc))
plt.legend(loc=4)
plt.show()

#
# # #################################################  QUADRATIC DISCRIMINANT ANALYSIS CLASSIFIER  #####################
# #
qdac = QuadraticDiscriminantAnalysis()
qdac.fit(xtrain,ytrain)
pred8 = qdac.predict(xtest)
qda_accuracy = accuracy_score(ytest,pred8)
print("QUADRATIC DISCRIMINANT ANALYSIS ACCURACY IS ",qda_accuracy)



y_pred_proba = qdac.predict_proba(xtest)[::,1]

fpr, tpr, _ = sklearn.metrics.roc_curve(ytest,  y_pred_proba)

auc = sklearn.metrics.roc_auc_score(ytest, y_pred_proba)
plt.plot(fpr,tpr,label="auc="+str(auc))
plt.legend(loc=4)
plt.show()

#
# ##############################################  LOGISTIC REGRESSION AS CLASSIFIER ##################################
clf_lrc = LogisticRegression(random_state=0, solver='lbfgs',multi_class = 'multinomial')
clf_lrc.fit(xtrain,ytrain)
pred9 = clf_lrc.predict(xtest)
lrc_accuracy = accuracy_score(ytest,pred9)
print("LOGISTIC REGRESSION ACCURACY IS: ",lrc_accuracy)


y_pred_proba = clf_lrc.predict_proba(xtest)[::,1]

fpr, tpr, _ = sklearn.metrics.roc_curve(ytest,  y_pred_proba)

auc = sklearn.metrics.roc_auc_score(ytest, y_pred_proba)
plt.plot(fpr,tpr,label="auc="+str(auc))
plt.legend(loc=4)
plt.show()

#
# ########################################## K- NEAREST NEIGHBOURS CLASSIFICATION(VERY SLOW ) ####################################
#
#clf_knnc =  KNeighborsClassifier(2)
#clf_knnc.fit(xtrain,ytrain)
#pred10 = clf_knnc.predict(xtest)
#knnc_accuracy = accuracy_score(ytest,pred10)
#print("K NEAREST NEIGHBOURS ACCURACY IS: ",knnc_accuracy)

######################################     K- NEAREST NEIGHBOURS CLASSIFICATION(USING COSINE SIMILARITY) ###########################

#cosine_values = cosine_similarity(ytrain, xtrain)
#top = [(heapq.nlargest((k), range(len(i)), i.take)) for i in cosine_values]
#top = [[xtest[j] for j in i[:k]] for i in top]
#pred14 = [max(set(i), key=i.count) for i in top]
#pred15 = np.array(pred14)
#knn_accuracy = accuracy_score(ytest,pred15)
#print(knn_accuracy)



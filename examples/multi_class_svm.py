from time import time
import numpy as np

from sklearn.datasets import fetch_mldata
#from sklearn.datasets import load_digits
from sklearn.cross_validation import train_test_split
#from sklearn.svm import LinearSVC

from pystruct.problems import CrammerSingerSVMProblem
from pystruct.learners import (StructuredSVM, OneSlackSSVM,
                               SubgradientStructuredSVM)

# do a binary digit classification
digits = fetch_mldata("MNIST original")
#digits = load_digits()
X, y = digits.data, digits.target
y = y.astype(np.int)
X_train, X_test, y_train, y_test = train_test_split(X, y)

X = X / 255.
#X = X / 16.

# we add a constant 1 feature for the bias
X_train_bias = np.hstack([X_train, np.ones((X_train.shape[0], 1))])
X_test_bias = np.hstack([X_test, np.ones((X_test.shape[0], 1))])

pbl = CrammerSingerSVMProblem(n_features=X_train_bias.shape[1], n_classes=10)
n_slack_svm = StructuredSVM(pbl, verbose=1, check_constraints=False, C=20,
                            batch_size=-1, tol=1e-2)
one_slack_svm = OneSlackSSVM(pbl, verbose=3, check_constraints=False, C=20,
                             max_iter=10, tol=1e-2)
subgradient_svm = SubgradientStructuredSVM(pbl, C=20, learning_rate=0.0001,
                                           max_iter=1, verbose=10,
                                           show_loss='true')

# n-slack cutting plane ssvm
#start = time()
#n_slack_svm.fit(X_train_bias, y_train)
#time_n_slack_svm = time() - start
#y_pred = np.hstack(n_slack_svm.predict(X_test_bias))
#print("Score with pystruct n-slack ssvm: %f (took %f seconds)"
      #% (np.mean(y_pred == y_test), time_n_slack_svm))

## 1-slack cutting plane ssvm
start = time()
one_slack_svm.fit(X_train_bias, y_train)
time_one_slack_svm = time() - start
y_pred = np.hstack(one_slack_svm.predict(X_test_bias))
print("Score with pystruct 1-slack ssvm: %f (took %f seconds)"
      % (np.mean(y_pred == y_test), time_one_slack_svm))
#import matplotlib.pyplot as plt

#plt.plot(one_slack_svm.objective_curve_)
#plt.show()

#online subgradient ssvm
#start = time()
#subgradient_svm.fit(X_train_bias, y_train)
#time_subgradient_svm = time() - start
#y_pred = np.hstack(subgradient_svm.predict(X_test_bias))

#print("Score with pystruct subgradient ssvm: %f (took %f seconds)"
      #% (np.mean(y_pred == y_test), time_subgradient_svm))

# because of the way I construct psi, we use half the C
# the standard one-vs-rest multi-class would probably be as good and faster
# but solving a different problem
#libsvm = LinearSVC(multi_class='crammer_singer', C=10)
#start = time()
#libsvm.fit(X_train, y_train)
#time_libsvm = time() - start
#print("Score with sklearn and libsvm: %f (took %f seconds)"
      #% (libsvm.score(X_test, y_test), time_libsvm))

import numpy as np
from numpy.testing import assert_array_equal

from pystruct.problems import LatentGridCRF, LatentDirectionalGridCRF
from pystruct.learners import LatentSSVM

import pystruct.toy_datasets as toy


def test_with_crosses():
    # very simple dataset. k-means init is perfect
    for n_states_per_label in [2, [1, 2]]:
        # test with 2 states for both foreground and background,
        # as well as with single background state
        #for inference_method in ['ad3', 'qpbo', 'lp']:
        for inference_method in ['lp']:
            X, Y = toy.generate_crosses(n_samples=10, noise=5, n_crosses=1,
                                        total_size=8)
            n_labels = 2
            crf = LatentGridCRF(n_labels=n_labels,
                                n_states_per_label=n_states_per_label,
                                inference_method=inference_method)
            clf = LatentSSVM(problem=crf, max_iter=50, C=10. ** 5, verbose=2,
                             check_constraints=True, n_jobs=-1,
                             break_on_bad=True)
            clf.fit(X, Y)
            Y_pred = clf.predict(X)
            assert_array_equal(np.array(Y_pred), Y)


def test_with_crosses_base_svms():
    # very simple dataset. k-means init is perfect
    for base_svm in ['1-slack', 'n-slack', 'subgradient']:
        X, Y = toy.generate_crosses(n_samples=10, noise=5, n_crosses=1,
                                    total_size=8)
        n_labels = 2
        crf = LatentGridCRF(n_labels=n_labels, n_states_per_label=[1, 2],
                            inference_method='lp')
        clf = LatentSSVM(problem=crf, max_iter=150, C=10. ** 5, verbose=2,
                         check_constraints=True, n_jobs=-1, break_on_bad=True,
                         base_svm=base_svm, learning_rate=5)
        clf.fit(X, Y)
        Y_pred = clf.predict(X)
        assert_array_equal(np.array(Y_pred), Y)


def test_with_crosses_bad_init():
    # use less perfect initialization
    X, Y = toy.generate_crosses(n_samples=10, noise=5, n_crosses=1,
                                total_size=8)
    n_labels = 2
    crf = LatentGridCRF(n_labels=n_labels, n_states_per_label=2,
                        inference_method='lp')
    clf = LatentSSVM(problem=crf, max_iter=50, C=10. ** 3, verbose=2,
                     check_constraints=True, n_jobs=-1, break_on_bad=True)
    H_init = crf.init_latent(X, Y)

    mask = np.random.uniform(size=H_init.shape) > .7
    H_init[mask] = 2 * (H_init[mask] / 2)
    clf.fit(X, Y, H_init=H_init)
    Y_pred = clf.predict(X)

    assert_array_equal(np.array(Y_pred), Y)


def test_directional_bars():
    for inference_method in ['lp']:
        X, Y = toy.generate_easy(n_samples=10, noise=5, box_size=2,
                                 total_size=6, seed=1)
        n_labels = 2
        crf = LatentDirectionalGridCRF(n_labels=n_labels,
                                       n_states_per_label=[1, 4],
                                       inference_method=inference_method)
        clf = LatentSSVM(problem=crf, max_iter=500, C=10. ** 5, verbose=2,
                         check_constraints=True, n_jobs=-1, break_on_bad=True,
                         base_svm='1-slack')
        clf.fit(X, Y)
        Y_pred = clf.predict(X)

        assert_array_equal(np.array(Y_pred), Y)

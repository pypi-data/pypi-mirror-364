# @file findcorrelations.py
#  Automated correlation analysis module
#
#   Written by JP Janet for HJK Group
#
#  Dpt of Chemical Engineering, MIT

import os
import sys
import numpy as np
from molSimplify.Classes.dft_obs import (dft_observation)
from sklearn import linear_model, preprocessing, metrics, feature_selection, model_selection


def analysis_supervisor(args, rootdir):
    status = True
    print('looking for scikit-learn')

    if not args.correlate:
        print("Error, correlation path not given")
        status = False
    print(f'looking for file at {args.correlate}')
    if not args.correlate:
        print("Error, correlation path not given")
        status = False
    if not os.path.exists(args.correlate) and status:
        print(f"Error, correlation file not found at {args.correlate}")
        status = False
    if not status:
        print('correlation cannot begin! Exiting...')
        sys.exit()
    if args.lig_only:
        print('using ligand-only descriptors (assuming all metals are the same)')
    if args.simple:
        print('using simple autocorrelation descriptors only')
    if args.max_descriptors:
        print(f'using a max of {args.max_descriptors} only')
    correlation_supervisor(
        args.correlate, rootdir, args.simple, args.lig_only, args.max_descriptors)


def accquire_file(path):
    # set display options
    np.set_printoptions(precision=3)
    # this function reads in values from a correctly formatted path
    # [name],[y],[folder_name]
    file_dict = dict()
    fail_dict = dict()
    counter = 0  # number of added paths
    ncounter = 0  # number of skipped paths
    if os.path.exists(path):
        print('found file, opening...')
        with open(path, 'r') as f:
            # expects csv fomart,
            ### value | path
            for i, lines in enumerate(f):
                print(f'read line: {i}')
                ll = lines.strip('\n\r').split(",")
                name = ll[0]
                if i == 0:
                    if len(ll) > 3:
                        print('custom descriptors found!')
                        custom_names = [ll[i] for i in range(4, len(ll))]

                else:
                    y_value = ll[1]
                    # check if path exists:
                    this_path = '/'+ll[2].strip('/') + '/'+name+'.xyz'
                    this_obs = dft_observation(name, this_path)
                    this_obs.sety(y_value)
                    if os.path.isfile(this_path):
                        this_obs.obtain_mol3d()
                        if this_obs.health:
                            counter += 1
                            file_dict.update({counter: this_obs})
                            if len(ll) > 3:
                                print(
                                    ('custom descriptors found for job ' + str(name)))
                                custom_descriptors = float(
                                    [ll[i] for i in range(4, len(ll))])
                                this_obs.append_descriptors(
                                    custom_names, custom_descriptors, '', '')
                        else:  # bad geo
                            this_obs.comments.append(
                                ' geo is not healthy, culling ' + str(this_path))
                            ncounter += 1
                            fail_dict.update({counter: this_obs})
                    else:  # no geo file found
                        this_obs.comments.append(
                            ' geo could not be found: ' + str(this_path))
                        ncounter += 1
                        fail_dict.update({counter: this_obs})
    if counter > 0:
        print(f'file import successful, {counter} geos loaded')
    len_fail = len(list(fail_dict.keys()))
    if len_fail > 0:
        print(f'{len_fail} unsuccessful imports :')
        for keys in list(fail_dict.keys()):
            print(f'failed at line {keys} for job {fail_dict[keys].name}')
    return(file_dict, fail_dict)


def correlation_supervisor(path, rootdir, simple=False, lig_only=False, max_descriptors=False):
    # load the files from the given input file
    file_dict, fail_dict = accquire_file(path)
    # loop over sucessful imports to get descriptors:
    big_mat = list()
    col_names = list()
    for i, keyv in enumerate(file_dict.keys()):
        file_dict[keyv].get_descriptor_vector(
            lig_only, simple, name=False, loud=False)
        if i == 0:
            col_names = file_dict[keyv].descriptor_names
        # reorganize the data
        this_row = list()
        this_row.append(float(file_dict[keyv].yvalue))
        this_row.extend(file_dict[keyv].descriptors)
        big_mat.append(this_row)
    big_mat = np.array(big_mat)
    # let's do some regression
    # standardize model:
    col_array = np.array(col_names)
    print(f'length of col array is {len(col_array)}')
    n_tot = len(col_array)
    X = big_mat[:, 1:]
    print(f'dimension of data matrix is {big_mat.shape}')
    n_obs = len(X[:, 1])
    Scaler = preprocessing.StandardScaler().fit(X)
    Xs = Scaler.transform(X)
    Y = big_mat[:, 0]
    # find baseline model (all descriptors)
    Reg = linear_model.LinearRegression()
    Reg.fit(Xs, Y)
    Ypred_all_all = Reg.predict(Xs)
    rs_all_all = metrics.r2_score(Y, Ypred_all_all)
    loo = model_selection.LeaveOneOut()
    r_reduce = list()
    mse_reduce = list()
    # stepwise reduce the feature set until only one is left
    for n in range(0, n_tot):
        reductor = feature_selection.RFE(Reg, n_features_to_select=n_tot-n,
                                         step=1, verbose=0)
        reductor.fit(Xs, Y)
        Ypred_all = reductor.predict(Xs)
        rs_all = metrics.r2_score(Y, Ypred_all)
        mse_all = metrics.mean_squared_error(Y, Ypred_all)
    r_reduce.append(rs_all)
    mse_reduce.append(mse_all)
    # reduce to one feature

    reductor_features = list()
    for i, ranks in enumerate(reductor.ranking_):
        reductor_features.append([col_array[i], ranks])
    reductor_features = sorted(reductor_features, key=lambda x: x[1])
    print('****************************************')
    # select best number using cv
    selector = feature_selection.RFECV(
        Reg, step=1, cv=loo, verbose=0, scoring='neg_mean_squared_error')
    selector.fit(Xs, Y)
    select_mse = selector.grid_scores_
    Ypred = selector.predict(Xs)
    rs = metrics.r2_score(Y, Ypred)
    n_opt = selector.n_features_
    opt_features = col_array[selector.support_]
    ranked_features = list()
    for i, ranks in enumerate(selector.ranking_):
        ranked_features.append([col_array[i], ranks])
    ranked_features = sorted(ranked_features, key=lambda x: x[1])
    print(ranked_features)
    if max_descriptors:  # check if we need to reduce further
        print(f'a max of {max_descriptors} were requested')
        n_max = int(max_descriptors)
        if n_opt > n_max:
            print(f'the RFE process selected {n_opt} variables as optimal')
            print(f'discarding an additional {n_max-n_opt} variables')
            new_variables = list()
            for i in range(0, n_max):
                new_variables.append(ranked_features[i])
    # report results to user
    print(f'analyzed {n_obs} molecules')
    print(f'the full-space R2 is {rs_all_all:0.2f} with {n_tot} features')
    print(f'optimal number of features is {n_opt} of total {n_tot}')
    print(f'the opt R2 is {rs:0.2f}')

    X_r = selector.transform(Xs)
    reg_red = linear_model.LinearRegression()
    reg_red.fit(X_r, Y)
    Ypred_r = reg_red.predict(X_r)
    coefs = reg_red.coef_
    intercept = reg_red.intercept_
    mse_all = metrics.mean_squared_error(Y, Ypred_all_all)
    mse_r = metrics.mean_squared_error(Y, Ypred_r)
    if n_opt < 30:
        print(f'the optimal variables are: {opt_features}')
        print(f'the coefficients are {coefs}')
    else:
        print(f'the (first 30) optimal variables are: {opt_features[0:29]}')
        print(f'the (first 30) coefficients are: {coefs[0:29]}')
    print(f'the intercept is {intercept:0.2f}')
    print(f'the training MSE with the best feature set is {mse_r:0.2f}')
    print(f'the MSE with all features is {mse_all:0.2f}')
    print(f'by eliminating {n_tot - n_opt} features,' +
           f' CV-prediction MSE decreased from {abs(select_mse[0]):0.2f} to {abs(select_mse[n_tot - n_opt]):0.2f}')
    with open(rootdir+'RFECV_rankings.csv', 'w') as f:
        f.write('RFE_rank,RFE_col,RFECV_rank,RFECV_col, \n')
        for i, items in enumerate(reductor_features):
            f.write(str(items[0]) + ',' + str(items[1]) + ',' +
                    str(ranked_features[i][0]) + ',' + str(ranked_features[i][1]) + '\n')
    with open(rootdir + 'y_data.csv', 'w') as f:
        for items in Y:
            f.write(str(items) + '\n')
    with open(rootdir + 'y_pred_r.csv', 'w') as f:
        for items in Ypred_r:
            f.write(str(items) + '\n')
    with open(rootdir+'optimal_decriptor_space.csv', 'w') as f:
        for i in range(0, n_obs):
            for j in range(0, n_opt):
                if j == (n_opt-1):
                    f.write(str(X_r[i][j])+'\n')
                else:
                    f.write(str(X_r[i][j])+',')
    with open(rootdir+'full_descriptor_space.csv', 'w') as f:
        for names in col_names:
            f.write(names+',')
        f.write('\n')
        for i in range(0, n_obs):
            for j in range(0, n_tot):
                if j == (n_tot-1):
                    f.write(str(Xs[i][j])+'\n')
                else:
                    f.write(str(Xs[i][j])+',')
    with open(rootdir+'scaling.csv', 'w') as f:
        means = Scaler.mean_
        var = Scaler.var_
        f.write('name, mean,variance \n')
        for i in range(0, n_tot):
            f.write(str(col_names[i])+','+str(means[i]) + ',' +
                    str(var[i])+','+str(selector.ranking_[i])+'\n')
    with open(rootdir+'coeficients.csv', 'w') as f:
        f.write('intercept,'+str(intercept) + '\n')
        for i in range(0, n_opt):
            f.write(str(opt_features[i])+','+str(coefs[i])+'\n')
    with open(rootdir + 'rfe_mse.csv', 'w') as f:
        f.write('features removed,mean CV error,'+str(intercept) + '\n')
        count = 0
        for items in mse_reduce:
            f.write(str(count)+','+str(items) + '\n')
            count += 1

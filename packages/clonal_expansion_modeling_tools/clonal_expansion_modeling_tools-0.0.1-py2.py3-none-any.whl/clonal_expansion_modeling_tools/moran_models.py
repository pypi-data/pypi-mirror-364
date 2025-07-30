import numpy as np
import scipy as sp
from scipy import stats
import statsmodels.api as sm
import numba
from numba import njit, prange, vectorize
from numba.typed import List

"""
functions for simulation
"""

@njit
def moran_step_biased_inplace(i, N, f=1):
    # takes a step according to a biased moran process
    Pminus = i*(N-i)/(N*(f*i+N-i))
    r = np.random.rand(*i.shape)
    di = np.zeros_like(i, dtype=numba.int32)
    di[r < Pminus] = -1
    di[r > 1 - f * Pminus] = 1
    i+=di
    return

@njit
def moran_step_biased(i, N, f=1):
    # takes a step according to a biased moran process
    Pminus = i*(N-i)/(N*(f*i+N-i))
    r = np.random.rand(*i.shape)
    di = np.zeros_like(i, dtype=numba.int32)
    di[r < Pminus] = -1
    di[r > 1 - f * Pminus] = 1
    return i+di

@njit(parallel=True)
def moran_step_biased_pl(i, N, f=1):
    # takes a step according to a biased moran process
    m, = i.shape
    Pminus = i*(N-i)/(N*(f*i+N-i))
    r = np.random.rand(m)
    di = np.zeros_like(i, dtype=numba.int32)
    di[r < Pminus] = -1
    di[r > 1 - f * Pminus] = 1
    return i+di
        
@njit(parallel=True)
def moran_step_biased_inplace_pl(i, N, f=1):
    # takes a step according to a biased moran process
    m, = i.shape
    Pminus = i*(N-i)/(N*(f*i+N-i))
    r = np.random.rand(m)
    di = np.zeros_like(i, dtype=numba.int32)
    di[r < Pminus] = -1
    di[r > 1 - f * Pminus] = 1
    i+=di
    return

def get_moran_trajectory_ensemble(i0, N, T, f=1, stride=1):
    T_eval = List([t*stride for t in range(T//stride+1)])
    return get_moran_trajectory_ensemble_t_eval(i0, N, T_eval, f=f)


def get_moran_trajectory_ensemble_pl(i0, N, T, f=1, stride=1):
    T_eval = List([t*stride for t in range(T//stride+1)])
    return get_moran_trajectory_ensemble_t_eval_pl(i0, N, T_eval, f=f)


@njit
def get_moran_trajectory_ensemble_t_eval(i0, N, T_eval, f=1):
    """
    T_eval must be a list that starts with zero and is strictly increasing
    """
    trajectory = np.zeros((len(T_eval), len(i0)), dtype=numba.int32)
    trajectory[0, :] = i0
    i = i0
    for t in range(len(T_eval)-1):
        for _ in range(T_eval[t+1]-T_eval[t]):
            moran_step_biased_inplace(i, N, f)
        trajectory[t+1, :] = i
    return trajectory.T

def get_moran_trajectory_ensemble_from_t0(t0, f, N, T, stride=1, parallel=False):
    """
    t0 is given in units of simulation steps, not days
    """
    T_eval = List([t*stride for t in range(T//stride+1)])
    t0 = t0.astype(np.int32)
    f = f.astype(np.float32)
    if not parallel:
        return get_moran_trajectory_ensemble_from_t0_t_eval(t0, f, N, T_eval)
    else:
        return get_moran_trajectory_ensemble_from_t0_t_eval_parallel(t0, f, N, T_eval)

@njit
def get_moran_trajectory_ensemble_from_t0_t_eval(t0, f, N, T_eval, skip_zeros = True):
    """
    t0 is given in units of simulation steps, not days
    """
    t0 = t0.astype(np.int32)
    f = f.astype(np.float32)
    m = len(T_eval)
    n = len(t0)
    trajectory = np.zeros((m, n), dtype=numba.int32)
    i = np.zeros(n, dtype=numba.int32)
    one = numba.int32(1)
    i = np.where(t0==0, one, i)
    j = 0   # index in trajectory corresponding to current time point
    for t in range(0, max(T_eval)+1):
        i = np.where(t0==t, one, i)
        if t in T_eval:
            trajectory[j, :] = i
            j += 1
        # take a step, ingoring those trajectories that have zero mutants (not worth drawing a random number for them)
        # (remains to be seen if this actually gives a meaningful efficiency gain)
        if skip_zeros:
            idx = np.argwhere(i!=0).flatten()
            new_i_values = moran_step_biased(np.take(i, idx), N, np.take(f, idx))
            for id, ival in zip(idx, new_i_values):
                i[id] = ival
        else:
            i = moran_step_biased(i, N, f)
    return trajectory.T

@njit
def get_moran_trajectory_ensemble_from_t0_i0_t_eval(t0, i0, f, N, T_eval, skip_zeros = True):
    """
    t0 is given in units of simulation steps, not days
    """
    t0 = t0.astype(np.int32)
    i0 = i0.astype(np.int32)
    f = f.astype(np.float32)
    m = len(T_eval)
    n = len(t0)
    trajectory = np.zeros((m, n), dtype=numba.int32)
    i = np.zeros(n, dtype=numba.int32)
    i = np.where(t0==0, i0, i)
    j = 0   # index in trajectory corresponding to current time point
    for t in range(0, max(T_eval)+1):
        i = np.where(t0==t, i0, i)
        if t in T_eval:
            trajectory[j, :] = i
            j += 1
        # take a step, ingoring those trajectories that have zero mutants (not worth drawing a random number for them)
        # (remains to be seen if this actually gives a meaningful efficiency gain)
        if skip_zeros:
            idx = np.argwhere(i!=0).flatten()
            new_i_values = moran_step_biased(np.take(i, idx), N, np.take(f, idx))
            for id, ival in zip(idx, new_i_values):
                i[id] = ival
        else:
            i = moran_step_biased(i, N, f)
    return trajectory.T

@njit
def get_moran_trajectory_ensemble_from_t0_t_eval_parallel(t0, f, N, T_eval, skip_zeros = True):
    """
    t0 is given in units of simulation steps, not days
    """
    t0 = t0.astype(np.int32)
    f = f.astype(np.float32)
    m = len(T_eval)
    n = len(t0)
    trajectory = np.zeros((m, n), dtype=numba.int32)
    i = np.zeros(n, dtype=numba.int32)
    one = numba.int32(1)
    i = np.where(t0==0, one, i)
    j = 0   # index in trajectory corresponding to current time point
    for t in range(0, max(T_eval)+1):
        i = np.where(t0==t, one, i)
        if t in T_eval:
            trajectory[j, :] = i
            j += 1
        # take a step, ingoring those trajectories that have zero mutants (not worth drawing a random number for them)
        # (remains to be seen if this actually gives a meaningful efficiency gain)
        if skip_zeros:
            idx = np.argwhere(i!=0).flatten()
            new_i_values = moran_step_biased_pl(np.take(i, idx), N, np.take(f, idx))
            for id, ival in zip(idx, new_i_values):
                i[id] = ival
        else:
            i = moran_step_biased(i, N, f)
    return trajectory.T


@njit
def get_moran_trajectory_ensemble_t_eval_batch(i0, N, T_eval, fvals = (1,)):
    m, = i0.shape
    p = len(fvals)
    nt = len(T_eval)
    f = np.zeros(m*p)
    i0_full = np.zeros(m*p)
    for i, fval in enumerate(fvals):
        f[i*m:(i+1)*m] = fval
        i0_full[i*m:(i+1)*m]=i0
    trajectory = np.zeros((nt, m*p), dtype=numba.int32)
    trajectory[0, :] = i0_full
    i = i0_full
    for t in range(nt - 1):
        for _ in range(T_eval[t+1] - T_eval[t]):
            moran_step_biased_inplace(i, N, f)
        trajectory[t+1, :] = i
    return trajectory.T.reshape((p, m, nt))

@njit
def get_moran_trajectory_ensemble_t_eval_pl(i0, N, T_eval, f=1):
    """
    T_eval must be a list that starts with zero and is strictly increasing
    """
    trajectory = np.zeros((len(T_eval), len(i0)), dtype=numba.int32)
    trajectory[0, :] = i0
    i = i0
    for t in range(len(T_eval)-1):
        for _ in range(T_eval[t+1]-T_eval[t]):
            moran_step_biased_inplace_pl(i, N, f)
        trajectory[t+1, :] = i
    return trajectory.T

@njit
def get_moran_trajectory_ensemble_t_eval_batch_pl(i0, N, T_eval, fvals = (1,)):
    m, = i0.shape
    p = len(fvals)
    nt = len(T_eval)
    f = np.zeros(m*p)
    i0_full = np.zeros(m*p)
    for i, fval in enumerate(fvals):
        f[i*m:(i+1)*m] = fval
        i0_full[i*m:(i+1)*m]=i0
    trajectory = np.zeros((nt, m*p), dtype=numba.int32)
    trajectory[0, :] = i0_full
    i = i0_full
    for t in range(nt - 1):
        for _ in range(T_eval[t+1] - T_eval[t]):
            moran_step_biased_inplace_pl(i, N, f)
        trajectory[t+1, :] = i
    return trajectory.T.reshape((p, m, nt))

"""
Functions for analytical approximations
"""

def neutral_moran_variance(i, N, T, auto_switch_to_approx = True):
    """
    i = number of mutant cells (int 0<=i<=N)
    N = total number of cells (int)
    T = number of steps of cell division & death (int)
    """
    N = np.array(N)
    T = np.array(T)
    if auto_switch_to_approx and (N.max()>1e7 or T.max()>1e7):
        return neutral_moran_variance_exponential_approximation(i, N, T)
    else:
        return (2*i/N)*(1-i/N)*(1-(1-2/N**2)**T)/(2/N**2)

def neutral_moran_variance_exponential_approximation(i, N, T):
    return (i)*(N-i)*(1-np.exp(-2*T/N**2))


def neutral_fixation_probability(i, N):
    """
    i = number of mutant cells (int 0<=i<=N)
    N = total number of cells (int)
    """
    return i/N


def neutral_extinction_probability(i, N):
    """
    i = number of mutant cells (int 0<=i<=N)
    N = total number of cells (int)
    """
    return 1 - i/N


def fixation_probability(i, r, N):
    """
    i = number of mutant cells (int 0<=i<=N)
    r = fitness of mutant cells (r=1 is neutral)
    N = total number of cells (int)
    """
    return (1-r**(-i))/(1-r**(-N))


def f_estimate(p0, pT, T, N):
    a = np.log((1-pT)/(1-p0))
    b = np.log(pT/p0)
    return (b-a)/(T/N+a) + 1


def moran_ode_rhs(t, p, s, T_g = 200):
    return (1/T_g) * p * s * (1-p)/(1+p*s)

def fit_to_moran_model(row, N, T_generation = 200, z_cutoff = 1.96):
    """
    Fits a pair of data points to the Moran model

    INPUT:
        row = pandas data frame row with fields:
            p0 = VAF at baseline
            pT = VAF at first followup
            dt = time elapsed in days
        N = assumed total stem cell number
        T_generation = time for one stem cell to divide in days
        z_cutoff = z-score at which to decide significance. Default = 1.96 corresponding to 95% probability

    OUTPUT:
        fhat = estimated drift parameter
    """
    p0, pT = row['baseline']/100, row['followup']/100
    # compute number of moran model steps
    T = row['dt']*N/T_generation
    # compare to neutral moran model
    # first check if the followup measurement is zero; if so, use the fixation probability

    zscore = N*abs(pT - p0)/(neutral_moran_variance(p0*N, N, T))**0.5
    if zscore < z_cutoff:
        return 0
    else:
        return f_estimate(p0, pT, T, N)-1


def f_estimate_vector(t, p, N):
    """
    Gives an estimate of the mutant fitness that minimizes the least-squares residual of the integrated version of the deterministic approximant ODE for the Moran model

    INPUT:
        t = an array of time points
        p = an array of corresponding VAF (between 0 and 1)
        N = assumed number of cells in total

    OUTPUT:
        fhat = estimated drift parameter
        c = constant of integration
    """
    a = t/N + np.log(1-p)
    b = -np.log((1-p)/p)
    A = np.stack([np.ones_like(a), a]).T
    c, s = np.linalg.lstsq(A, b)[0]
    return s+1, c

def get_least_square_estimate(t, N, f, c):
    """
    INPUT:
        t = array of time points
        N = assumed number of cells in total
        f = estimated drift parameter, first output of f_estimate_vector
        c = estimated constant of integration, second output of f_estimate_vector

    OUTPUT:
        phat = estimated VAF according to ODE assumption
    """
    phat = np.zeros_like(t)
    for i, ti in enumerate(t):
        residual = lambda x : np.log(x) - f*np.log((1-x)) - ((f-1)*ti/N + c)
        res = sp.optimize.root_scalar(residual, method='brentq', bracket = (1/N, 1-1/N))
        phat[i] = res.root
    return phat

def fit_OLS(t, p, N, T_generation=200, **kwargs):
    """
    t here is given in days, but in the ODE t should have units of [total cell divisions]
    This means the time in the ODE is T = N*t/T_generation
    And the first term in the integrated ODE is s*T/N, which is s*t*N/N*T_generation = s*t/T_generation
    """
    exog = sm.add_constant(t/T_generation + np.log(1-p))
    endog = -np.log((1-p)/p)
    model = sm.OLS(endog, exog)
    return model.fit()
def fit_WLS(t, p, uncertainty = 1e-2, T_generation=200, **kwargs):
    exog = sm.add_constant(t/T_generation + np.log(1-p))
    endog = -np.log((1-p)/p)
    w = np.ones_like(t) / uncertainty**2
    model = sm.WLS(endog, exog, weights = w)
    return model
def logistic_fit_statsmodels(t, y, y_err = 1e-2, T_generation=200, **kwargs):
    exog = sm.add_constant(t/T_generation)
    endog = np.log(y/(1-y))
    w = ((y*(1-y))/y_err)**2
    return sm.WLS(endog, exog, weights=w)

def logistic_OLS_fit_statsmodels(t, y, T_generation=200, **kwargs):
    exog = sm.add_constant(t/T_generation)
    endog = np.log(y/(1-y))
    return sm.OLS(endog, exog)

def exponential_fit_statsmodels(t, y, y_err = 1e-2, T_generation=200, **kwargs):
    exog = sm.add_constant(t/T_generation)
    endog = np.log(y)
    w = (y/y_err)**2
    return sm.WLS(endog, exog, weights=w)

# prediction based on a model fit

def predict_deterministic(fit, t, N=1e5, T_generation = 200):
    # ok.... here I encounter a bit of an issue. I can't actually get a prediction from this...
    # I solved this problem in visualize_ode_fitting.ipynb
    # Unfortunately I solved this problem incorrectly. In the Moran ODE formulated as linear regression, you need the y-value in the exogenous variable
    # OK actually... I think the way I did it was valid in the end. By passing only time as the exogenous variable, the prediction generated by the stastmodels model is exp(st/T_g + c), which is exactly what I compute here and should be equal to log(p/(1-p)^(1+s))
    c, s = fit.params
    y = s*t/T_generation + c
    phat = np.zeros_like(y)
    for i, yi in enumerate(y):
        residual = lambda p : yi + (s+1)*np.log(1-p) - np.log(p)
        res = sp.optimize.root_scalar(residual, method='brentq', bracket = (1/N, 1-1/N))
        phat[i] = res.root
    return phat


def predict_stochastic(fit, t, N=1e5, T_generation=200, num_sims = 30, num_t_eval = 50):
    # gets samples from the posterior distribution over parameters c, s
    # for each sample of parameters, it generates a stochastic trajectory
    params_estimate = fit.params
    params_cov = fit.cov_params()
    params_rv = sp.stats.multivariate_normal(params_estimate, params_cov)
    params_samples = params_rv.rvs(num_sims)
    i0 = np.zeros(num_sims, dtype=int)
    for i, (c, s) in enumerate(params_samples):
        residual = lambda p : c + s*t[0]/T_generation + (s+1)*np.log(1-p) - np.log(p)
        result = sp.optimize.root_scalar(residual, method='brentq', bracket = (1/N, 1-1/N))
        i0[i] = int(N*result.root)
    simulation_steps_per_eval_time = (N * (t.max() - t.min())/T_generation)/num_t_eval
    t_eval = List(simulation_steps_per_eval_time * np.arange(num_t_eval))
    t_days = np.linspace(t.min(), t.max(), num_t_eval)
    traj = get_moran_trajectory_ensemble_t_eval(i0, N, T_eval = t_eval, f = 1+params_samples[:,1])
    return t_days, traj/N


def stem_cell_vaf_from_mature_cell_vaf(y, km=2, delta=0.017, z=1):
    # infers the VAF at the level of stem cells, given VAF at the level of mature cells
    # assumes that mutant stem cells produce an average of km mature cells per single unmutated mature cell
    # assumes that a fraction z of the cells are heterozygous
    if any(y>1-0.5*z):
        raise ValueError("VAF values contradict assumed zygocity ratio")
    k = km * (1-delta)
    return y/((1-k)*y + (0.5*k*z + (1-z)*k))


def mature_cell_vaf_from_stem_cell_vaf(x, km=2, delta=0.017, z=1):
    k = km*(1-delta)
    return (0.5*k*z + (1-z)*k)*x / (1-(1-k)*x)

# chi squared analysis

def cell_count_deltas(y, N):
    """
    INPUT:
        y = numpy array of sequential VAF measurements, expressed as a fraction (0<=y<=1)
        N = assumed total number of cells

    OUTPUT:
        delta_X = numpy array of sequential changes in cell count
    """
    return np.diff(y)*N

def test_statistic(t, y, N, T_generation = 200):
    """
    computes the test statistic, to be compared with chi squared

    INPUT:
        t = numpy array of observation times in days
        y = numpy array of VAF as a fraction (0<=y<=1)
        N = assumed total number of cells
        T_generation = assumed number of days per stem cell division

    OUTPUT:
        chisquared = test statistic for the observations y
    """
    i0 = (y[:-1]*N).astype(int)
    dts = np.diff(t*N/T_generation)
    di = cell_count_deltas(y, N)
    sigmasquareds = neutral_moran_variance(i0, N, dts)
    return sum(di**2 / sigmasquareds)


def beta_params_from_moments(mean, variance):
    return mean**2*(1-mean)/variance - mean, (1-mean)*(mean*(1-mean)/variance - 1)

def test_statistic_beta(t, y, N, T_generation = 200):
    """
    computes the test statistic, to be compared with chi squared
    this transforms the increments of y such that if the were beta distributed, then they become normally distributed

    INPUT:
        t = numpy array of observation times in days
        y = numpy array of VAF as a fraction (0<=y<=1)
        N = assumed total number of cells
        T_generation = assumed number of days per stem cell division

    OUTPUT:
        chisquared = test statistic for the observations y
    """
    dts = np.diff(t*N/T_generation)
    normalized_variates = np.zeros_like(dts)
    sigmasquareds = neutral_moran_variance(y[:-1]*N, N, dts)
    # now we start to work in [0,1], which requires rescaling the mean by N and variance by N**2
    alpha, beta = beta_params_from_moments(y[:-1], sigmasquareds/N**2)
    for i in range(len(y)-1):
        normalized_variates[i] = stats.norm(0,1).ppf(stats.beta(alpha[i], beta[i]).cdf(y[i+1]))
    return sum(normalized_variates**2)

def quantile_level(dof, pvalue):
    return stats.chi2(dof).ppf(pvalue)

def is_consistent_with_neutral_drift(t, y, N, pvalue=0.95):
    if len(y)<2:
        return True
    teststat = test_statistic(t, y, N)
    qlev = quantile_level(len(y)-1, pvalue)
    return teststat < qlev

def load_smc_results(filename):
    with open(filename, "r") as fobj:
        contents = fobj.readlines()
    separator_index = contents.index("\n")
    particles_array = np.loadtxt(contents[5:separator_index])
    cmd_args = dict()
    for line in contents[separator_index + 1 :]:
        try:
            name, value = line.strip().split(" = ")
            try:
                cmd_args[name] = float(value)
            except ValueError:
                cmd_args[name] = value
        except:
            pass
    abc_data = dict()
    abc_data["number of simulations"] = int(contents[1].strip().split()[-1])
    abc_data["acceptance ratio"] = float(contents[2].strip().split()[-1])
    abc_data["tolerance_schedule"] = np.loadtxt(
        contents[3].strip().split(":")[-1].strip(" ").strip("[").strip("]").split(",")
    )
    return particles_array, abc_data, cmd_args

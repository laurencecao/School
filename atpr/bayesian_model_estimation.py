#!/usr/bin/python
import numpy as np
import matplotlib.pyplot as plot

N = 50.
noise_var = B = .2**2
lower_bound = lb = -5.
upper_bound = ub = 5.
xs = np.matrix(sorted((ub-lb)*np.random.rand(N)+lb)).T
xaxis = np.matrix(np.linspace(lb,ub,num=N)).T
w = np.array([1, -4, 1])
ys = w[0] + w[1]*xaxis + w[2]*np.square(xaxis)
t = w[0] + w[1]*xs + +w[2]*np.square(xs) + np.sqrt(B)*np.random.randn(N,1);

prior_alpha = 0.005 #Low precision initially
prior_beta = 0.005 #Low guess for noise var
max_N = 7 #Upper limit on model order
evidence = E = np.zeros(max_N)
f, axarr = plot.subplots(3)
def gen_polynomial(x, p):
    return x**p

itr_upper_bound = 250
all_y = []
for order in range(1, max_N+1):
    m = np.zeros((order, 1))
    s = np.zeros((order, order))
    poly = np.vectorize(gen_polynomial)
    basis = poly(xs, np.tile(np.arange(order), N).reshape(N, order))
    alpha = a = prior_alpha
    beta = b = prior_beta
    itr = 0
    while not itr < itr_upper_bound:
        itr += 1
        first_part = a*np.eye(order)
        second_part = b*(basis.T*basis)
        s_inv = a*np.eye(order)+b*(basis.T*basis)
        m = b*s_inv.I*basis.T*t
        posterior_alpha = pa = np.matrix(order/(m.T*m))[0,0]
        posterior_beta = pb = np.matrix(N/((t.T-m.T*basis.T)*(t.T-m.T*basis.T).T))[0,0]
        a = pa
        b = pb
    A = a*np.eye(order)+b*(basis.T)*basis
    mn = b*(A.I*(basis.T*t))
    penalty = emn = b/2.*(t.T-mn.T*basis.T)*(t.T-mn.T*basis.T).T+a/2.*mn.T*mn
    E[order-1] = order/2.*np.log(a)+N/2.*np.log(b)-emn-1./(2*np.log(np.linalg.det(A)))-N/2.*np.log(2*np.pi)
    y = (mn.T*basis.T).T
    all_y.append(y)
    axarr[0].plot(xs, y ,"g")

best_model = np.ma.argmax(E)
#print E
x0label = x2label = "Input X"
y0label = y2label = "Output Y"
x1label = "Model Order"
y1label = "Score"
plot.tight_layout()
axarr[0].set_xlabel(x0label)
axarr[0].set_ylabel(y0label)
axarr[1].set_xlabel(x1label)
axarr[1].set_ylabel(y1label)
axarr[2].set_xlabel(x2label)
axarr[2].set_ylabel(y2label)
axarr[0].set_title("Bayesian model estimation using polynomial basis functions")
axarr[0].plot(xaxis, ys, "b")
axarr[0].plot(xs, t, "ro")
axarr[1].set_title("Model Evidence")
axarr[1].plot(E, "b")
axarr[2].set_title("Best model, polynomial order $"+`best_model`+"$")
axarr[2].plot(xs, t, "ro")
axarr[2].plot(xs, all_y[best_model], "g")
plot.show()

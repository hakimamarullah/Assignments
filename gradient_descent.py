import torch

EPOCH = 500
ALPHA = 0.01
xs = [0.] * (EPOCH + 1)
ys = [0.] * (EPOCH + 1)
xs[0], ys[0] = -3.0, 2.0
for t in range(EPOCH):
  x = torch.tensor(xs[t], requires_grad= True)
  y = torch.tensor(ys[t], requires_grad= True)
  f = (x*x) + (y*y) + (2*x) - (4*y) + 5
  f.backward()
  xs[t + 1] = xs[t] - ALPHA * x.grad.item()
  ys[t + 1] = ys[t] - ALPHA * y.grad.item()
  x.grad.zero_()
  y.grad.zero_()


f = (xs[-1]*xs[-1]) + (ys[-1]*ys[-1]) + (2*xs[-1]) - (4*ys[-1]) + 5
print("optimum at x = {}, y = {} dengan nilai f(x,y) = {}".format(xs[-1], ys[-1], f))
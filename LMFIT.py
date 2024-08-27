import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import lmfit as lm
from typing import Callable

def Gaussian(x, amp, cen, wid, off):
	"""Simple model of 1D Gaussian function."""
	# adjusted width to reflect w = I/e^2
	return amp * np.exp(-2*((x-cen)/wid)**2) + off

def Sinusoidal(x, amp, freq, phi, off):
    # C: constant offset
    return amp * np.sin(2*np.pi*freq*(x - phi)) + off

def ComplexExp(x, amp, freq, phi, off):
	return amp * np.exp(2j * np.pi * freq * (x - phi)) + off

def complexSum(x, amp1, amp2, freq1, freq2, phi1, phi2, off):
	return ComplexExp(x, amp1, freq1, phi1, 0) + ComplexExp(x, amp2, freq2, phi2, 0) + off

def realSum(x, amp1, amp2, freq1, freq2, phi1, phi2, off):
	return np.real(complexSum(x, amp1, amp2, freq1, freq2, phi1, phi2, off))

def sineSum(x, amp1, amp2, freq1, freq2, phi1, phi2, off):
	return Sinusoidal(x, amp1, freq1, phi1, 0) + Sinusoidal(x, amp2, freq2, phi2, 0) + off

def lmfit(x: np.ndarray, y: np.ndarray, title: str, dest_dir: str, params: lm.Parameters, func: Callable):
	"""Plot a general fit curve of a set of data"""

	ShowInitialGuess = True

	model  = lm.Model(func)

	# fit the curve to those parameters 
	result = model.fit(y, params, x=x)

	# give a report on the parameters
	print(result.fit_report())
	# write the report into a text file
	with open(f"{dest_dir}\\{title}.txt", "w") as f:
		f.write(result.fit_report())


	fig = plt.figure(figsize=(7,5), constrained_layout=True)
	wratios, hratios = ([1], [1, 3])
	gs  = fig.add_gridspec(nrows=2, ncols=1, width_ratios=wratios, height_ratios=hratios)
	ax1 = fig.add_subplot(gs[1,0])
	ax0 = fig.add_subplot(gs[0,0], sharex=ax1)
	axs = [ax0, ax1]
	plt.setp(ax0.get_xticklabels(), visible=False)

	axs[0].set_ylabel(r'$y - f(x)$')
	axs[1].set_xlabel(r'Position (mm)')
	axs[1].set_ylabel(r'Brightness')

	axs[0].plot(x, y-result.best_fit, color='black', marker='.', linestyle='', label='Residuals')
	axs[1].plot(x, y, color='black', marker='.', linestyle='', label='Data')
	axs[1].plot(x, result.best_fit, color='crimson', marker='', linestyle='-', label='Best fit')

	if ShowInitialGuess:
		axs[1].plot(x, result.init_fit, color='royalblue', marker='', linestyle='-', label='Initial guess')

	for ax in axs:
		ax.legend(loc='best')
		ax.grid()

	plt.title(title)
	plt.savefig(f"{dest_dir}\\{title}.pdf", format="pdf")
	plt.close()

def main():
	df = pd.read_csv(r".\HalfWavePlate\raw_data\aug_27_with_sum.csv").to_numpy()
	df = df[:-2]


	x = df[ : , 1]
	y = df[ : , 2]
	y2 = df[ : , 5]

	params = lm.Parameters()
	params.add(lm.Parameter(name='amp1', value=350., vary=True, min=0., max=np.inf))
	params.add(lm.Parameter(name='freq1', value=5.7107, vary=True, min=0, max=np.inf))
	params.add(lm.Parameter(name='phi1', value=1, vary=True, min=0., max=10))
	params.add(lm.Parameter(name='amp2', value=200., vary=True, min=0., max=np.inf))
	params.add(lm.Parameter(name='freq2', value=6.366, vary=True, min=0, max=np.inf))
	params.add(lm.Parameter(name='phi2', value=1, vary=True, min=0., max=10))
	params.add(lm.Parameter(name='off', value=800, vary=True, min=-np.inf, max=np.inf))

	lmfit(x, y, "title", ".\\", params, sineSum)
	lmfit(x, y2, "title2", ".\\", params, sineSum)

if __name__ == "__main__":
	main()

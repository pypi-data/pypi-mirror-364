from typing import ClassVar

import numpy as np
from numpy.typing import ArrayLike

from . import Covariance


class GaussianCovariance(Covariance):
	_params: ClassVar[dict[str, float]] = {
		"range": 1.0,
		"sill": 1.0,
		"nugget": 0.0,
		"scale": 1.0,
	}

	def __call__(self, lag: ArrayLike) -> ArrayLike:
		# Formula: nugget + sill * (1 - np.exp(-((scale * lag / range) ** 2))
		result = np.divide(self.scale, self.range) * lag
		result *= result
		np.negative(result, out=result)
		np.exp(result, out=result)
		result -= 1.0
		result *= -self.sill
		if self.nugget != 0.0:
			result += self.nugget
		return result

	@classmethod
	def p0(cls, lag, var) -> tuple[float]:
		# default fitting will only fit range and sill (no nugget effect)
		return (
			np.nanmax(lag) / 2,  # naive range = 50% max range
			np.nanmean(var),  # naive sill = average variance
		)

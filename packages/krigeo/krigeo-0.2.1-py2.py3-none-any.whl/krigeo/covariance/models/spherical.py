from typing import ClassVar

import numpy as np
from numpy.typing import ArrayLike

from . import Covariance


class SphericalCovariance(Covariance):
	_params: ClassVar[dict[str, float]] = {
		"range": 1.0,
		"sill": 1.0,
		"nugget": 0.0,
	}

	def __call__(self, lag: ArrayLike) -> ArrayLike:
		# Formula: nugget + sill * (1.5 * lag - 0.5 * lag ** 3) if lag < 1
		#          nugget + sill if lag >= 1
		result = np.ones_like(lag)
		within_range = lag < self.range
		lag = lag[within_range]
		result_in_range = np.divide(1.5, self.range) * lag
		result_in_range += np.divide(-0.5, self.range**3) * lag**3
		result[within_range] = result_in_range
		result *= self.sill
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

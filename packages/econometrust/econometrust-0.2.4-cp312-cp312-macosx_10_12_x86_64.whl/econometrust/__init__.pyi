"""High-performance econometric regression library written in Rust with Python bindings.

EconoMetrust provides optimized implementations of fundamental econometric estimators:
- OLS: Ordinary Least Squares with robust standard errors (HC0)
- WLS: Weighted Least Squares with diagonal weight matrices
- GLS: Generalized Least Squares with Cholesky whitening
- IV: Instrumental Variables for exactly identified models
- TSLS: Two-Stage Least Squares for overidentified models
- FE: Panel data Fixed Effects with clustered standard errors

All estimators feature:
- Memory-optimized implementations with cache-aligned data structures
- Intelligent algorithm selection (Normal equations vs SVD vs Cholesky)
- Numerically stable computations with robust error handling
- Comprehensive statistical inference (standard errors, t-tests, confidence intervals)
- Professional-grade summary output with diagnostic statistics

Performance optimizations include vectorized operations, minimal memory allocation,
and efficient sparse matrix handling for large-scale econometric applications.
"""

import numpy as np
from typing import Optional

class OLS:
    """Ordinary Least Squares regression with robust standard error support.

    High-performance OLS estimator featuring intelligent algorithm selection,
    memory-optimized implementation, and optional heteroskedasticity-robust
    standard errors using the White/HC0 sandwich estimator.

    The estimator automatically selects between Cholesky decomposition, SVD,
    and normal equations based on problem structure for optimal numerical
    stability and computational efficiency.

    Parameters
    ----------
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model. When True, a constant
        term is added to the regression.
    robust : bool, default=False
        Whether to use heteroskedasticity-robust (White/HC0) standard errors.
        Robust standard errors are consistent under heteroskedasticity but
        may have inflated variance in small samples.

    Notes
    -----
    The OLS estimator solves: β̂ = (X'X)⁻¹X'y

    Standard errors:
    - Classical: SE = √(σ̂²(X'X)⁻¹) where σ̂² = RSS/(n-k)
    - Robust HC0: SE = √(diag((X'X)⁻¹X'ΩX(X'X)⁻¹)) where Ω = diag(ê²)

    Memory usage is optimized by not storing design matrices after fitting.
    Algorithm selection ensures numerical stability across problem sizes.

    Examples
    --------
    >>> import numpy as np
    >>> from econometrust import OLS
    >>>
    >>> # Generate sample data
    >>> X = np.random.randn(100, 3)
    >>> y = X @ [1.5, -2.0, 0.5] + np.random.randn(100) * 0.1
    >>>
    >>> # Fit OLS model
    >>> model = OLS(fit_intercept=True, robust=True)
    >>> model.fit(X, y)
    >>> print(model.summary())
    """

    def __init__(self, fit_intercept: bool = True, robust: bool = False) -> None: ...
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit the OLS model using optimized algorithms.

        Automatically selects the most efficient and numerically stable
        algorithm based on problem characteristics:
        - Cholesky decomposition for well-conditioned overdetermined systems
        - SVD for small or ill-conditioned systems
        - Normal equations for large overdetermined systems

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Training data matrix. Each row is a sample, each column a feature.
        y : np.ndarray, shape (n_samples,)
            Target values (dependent variable).

        Raises
        ------
        ValueError
            If X and y have incompatible shapes or insufficient samples.
        RuntimeError
            If the regression system cannot be solved (rank deficiency).

        Notes
        -----
        Requires n_samples > n_features + fit_intercept for identification.
        Handles multicollinearity through SVD fallback for singular systems.
        """
        ...

    def is_fitted(self) -> bool:
        """Check if the model has been fitted to data.

        Returns
        -------
        bool
            True if fit() has been called successfully, False otherwise.
        """
        ...

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """Regression coefficients excluding intercept.

        Returns
        -------
        np.ndarray or None
            Array of shape (n_features,) containing fitted coefficients.
            None if model not fitted.
        """
        ...

    @property
    def intercept(self) -> Optional[float]:
        """Regression intercept term.

        Returns
        -------
        float or None
            Fitted intercept value. None if not fitted or fit_intercept=False.
        """
        ...

    @property
    def fit_intercept(self) -> bool:
        """Whether the model includes an intercept term.

        Returns
        -------
        bool
            Configuration parameter set during initialization.
        """
        ...

    @property
    def robust(self) -> bool:
        """Whether robust standard errors are computed.

        Returns
        -------
        bool
            Configuration parameter set during initialization.
        """
        ...

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions using the fitted model.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Input data for prediction. Must have same number of features
            as training data.

        Returns
        -------
        np.ndarray, shape (n_samples,)
            Predicted values: ŷ = Xβ̂ + intercept

        Raises
        ------
        ValueError
            If model not fitted or X has wrong number of features.
        """
        ...

    def standard_errors(self) -> Optional[np.ndarray]:
        """Standard errors of regression coefficients.

        Returns
        -------
        np.ndarray or None
            Standard errors of coefficients. Uses robust (HC0) estimator
            if robust=True, classical estimator otherwise.
        """
        ...

    def t_statistics(self) -> Optional[np.ndarray]:
        """T-statistics for coefficient significance tests.

        Returns
        -------
        np.ndarray or None
            T-statistics: t = β̂ / SE(β̂) for testing H₀: β = 0
        """
        ...

    def p_values(self) -> Optional[np.ndarray]:
        """P-values for two-sided coefficient significance tests.

        Returns
        -------
        np.ndarray or None
            P-values for H₀: βⱼ = 0 vs H₁: βⱼ ≠ 0. Uses t-distribution
            with appropriate degrees of freedom.
        """
        ...

    def confidence_intervals(self, alpha: float = 0.05) -> Optional[np.ndarray]:
        """Confidence intervals for regression coefficients.

        Parameters
        ----------
        alpha : float, default=0.05
            Significance level. Confidence level = 1 - alpha.

        Returns
        -------
        np.ndarray or None
            Array of shape (n_features, 2) containing [lower, upper] bounds
            for each coefficient at the specified confidence level.
        """
        ...

    def summary(self) -> str:
        """Generate comprehensive regression summary.

        Returns
        -------
        str
            Formatted summary including coefficients, standard errors,
            t-statistics, p-values, R², F-statistic, and diagnostic tests.
        """
        ...

    def covariance_matrix(self) -> Optional[np.ndarray]:
        """Covariance matrix of coefficient estimates.

        Returns
        -------
        np.ndarray or None
            Covariance matrix Var(β̂). Classical or robust depending on
            configuration. Shape (n_features, n_features).
        """
        ...

    @property
    def mse(self) -> Optional[float]:
        """Mean squared error of residuals.

        Returns
        -------
        float or None
            MSE = RSS / (n - k) where RSS is residual sum of squares
            and k is number of parameters including intercept.
        """
        ...

    @property
    def r_squared(self) -> Optional[float]:
        """Coefficient of determination (R-squared).

        Returns
        -------
        float or None
            R² = 1 - RSS/TSS measuring fraction of variance explained.
            Range [0, 1] where 1 indicates perfect fit.
        """
        ...

    @property
    def r_squared_adj(self) -> Optional[float]:
        """Adjusted R-squared accounting for degrees of freedom.

        Returns
        -------
        float or None
            Adjusted R² = 1 - (1-R²)*(n-1)/(n-k-1) where n is sample size
            and k is number of parameters. Penalizes model complexity.
        """
        ...

    @property
    def residuals(self) -> Optional[np.ndarray]:
        """Regression residuals.

        Returns
        -------
        np.ndarray or None
            Residuals: ê = y - Xβ̂. Shape (n_samples,).
        """
        ...

    @property
    def n_samples(self) -> Optional[int]:
        """Number of samples used in fitting.

        Returns
        -------
        int or None
            Sample size n.
        """
        ...

    @property
    def n_features(self) -> Optional[int]:
        """Number of features (excluding intercept).

        Returns
        -------
        int or None
            Number of regressors k.
        """
        ...

    def __repr__(self) -> str: ...

class WLS:
    """Weighted Least Squares regression with diagonal weight matrices.

    Memory-optimized WLS estimator using sqrt(weights) transformation for
    numerical stability. Efficient implementation for heteroskedastic models
    where the error variance is known up to a proportionality constant.

    The estimator transforms the regression using sqrt(weights) and applies
    OLS to the transformed data, ensuring optimal statistical properties
    while maintaining computational efficiency.

    Parameters
    ----------
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model.

    Notes
    -----
    WLS assumes: Var(εᵢ) = σ²/wᵢ where wᵢ are known weights.

    The weighted regression minimizes: Σᵢ wᵢ(yᵢ - xᵢ'β)²

    Implementation uses transformation: √wᵢyᵢ = √wᵢxᵢ'β + √wᵢεᵢ*
    where εᵢ* ~ iid(0, σ²), enabling efficient OLS solution.

    R² calculation uses weighted sums of squares for proper interpretation.
    MSE uses original scale residuals for unbiased error variance estimation.

    Examples
    --------
    >>> import numpy as np
    >>> from econometrust import WLS
    >>>
    >>> # Generate heteroskedastic data
    >>> X = np.random.randn(100, 2)
    >>> weights = np.exp(X[:, 0])  # Heteroskedasticity
    >>> y = X @ [1.0, -0.5] + np.random.randn(100) / np.sqrt(weights)
    >>>
    >>> # Fit WLS model
    >>> model = WLS(fit_intercept=True)
    >>> model.fit(X, y, weights)
    >>> print(model.summary())
    """

    def __init__(self, fit_intercept: bool = True) -> None: ...
    def fit(self, X: np.ndarray, y: np.ndarray, weights: np.ndarray) -> None:
        """Fit the WLS model using weighted transformation.

        Uses sqrt(weights) transformation for numerical stability and
        automatic algorithm selection for optimal performance.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Training data matrix.
        y : np.ndarray, shape (n_samples,)
            Target values.
        weights : np.ndarray, shape (n_samples,)
            Sample weights. Must be positive and finite. Higher weights
            indicate lower variance observations.

        Raises
        ------
        ValueError
            If weights are non-positive, infinite, or arrays have
            incompatible dimensions.
        RuntimeError
            If the weighted regression system cannot be solved.

        Notes
        -----
        Weights are typically inverse variance weights: wᵢ = 1/Var(εᵢ).
        For efficiency, weights are not stored after fitting.
        """
        ...

    def is_fitted(self) -> bool:
        """Check if the model has been fitted."""
        ...

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """WLS regression coefficients."""
        ...

    @property
    def intercept(self) -> Optional[float]:
        """WLS regression intercept."""
        ...

    @property
    def fit_intercept(self) -> bool:
        """Whether the model includes an intercept."""
        ...

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions using the fitted WLS model.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Input data for prediction.

        Returns
        -------
        np.ndarray
            Predicted values: ŷ = Xβ̂ + intercept
        """
        ...

    def standard_errors(self) -> Optional[np.ndarray]:
        """Standard errors of WLS coefficients.

        Returns
        -------
        np.ndarray or None
            Standard errors from weighted covariance matrix.
        """
        ...

    def t_statistics(self) -> Optional[np.ndarray]:
        """T-statistics for WLS coefficients."""
        ...

    def p_values(self) -> Optional[np.ndarray]:
        """P-values for WLS coefficient significance tests."""
        ...

    def confidence_intervals(self, alpha: float = 0.05) -> Optional[np.ndarray]:
        """Confidence intervals for WLS coefficients."""
        ...

    def summary(self) -> str:
        """Generate WLS regression summary."""
        ...

    @property
    def mse(self) -> Optional[float]:
        """Mean squared error (original scale).

        Returns
        -------
        float or None
            MSE computed using original scale residuals for unbiased
            error variance estimation.
        """
        ...

    @property
    def r_squared(self) -> Optional[float]:
        """Weighted R-squared.

        Returns
        -------
        float or None
            R² = 1 - (weighted RSS)/(weighted TSS) using consistent
            weighting in numerator and denominator.
        """
        ...

    @property
    def r_squared_adj(self) -> Optional[float]:
        """Adjusted R-squared accounting for degrees of freedom.

        Returns
        -------
        float or None
            Adjusted R² = 1 - (1-R²)*(n-1)/(n-k-1) where n is sample size
            and k is number of parameters. Penalizes model complexity.
        """
        ...

    @property
    def residuals(self) -> Optional[np.ndarray]:
        """Original scale residuals.

        Returns
        -------
        np.ndarray or None
            Residuals on original (unweighted) scale: ê = y - Xβ̂
        """
        ...

    @property
    def n_samples(self) -> Optional[int]:
        """Number of samples used in fitting."""
        ...

    @property
    def n_features(self) -> Optional[int]:
        """Number of features (excluding intercept)."""
        ...

    def __repr__(self) -> str: ...

class GLS:
    """Generalized Least Squares regression with Cholesky whitening.

    High-performance GLS estimator for models with known error covariance
    structure. Uses Cholesky decomposition for efficient whitening
    transformation and automatic algorithm selection for numerical stability.

    The implementation efficiently handles the transformation y* = L⁻¹y and
    X* = L⁻¹X where Σ = LL' is the Cholesky decomposition of the error
    covariance matrix.

    Parameters
    ----------
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model.

    Notes
    -----
    GLS assumes: ε ~ N(0, σ²Σ) where Σ is a known positive definite matrix.

    The GLS estimator: β̂ = (X'Σ⁻¹X)⁻¹X'Σ⁻¹y

    Implementation uses Cholesky whitening: Σ = LL' where L is lower triangular.
    Transformed regression: L⁻¹y = L⁻¹Xβ + L⁻¹ε where L⁻¹ε ~ N(0, σ²I).

    Memory optimized by not storing large matrices after fitting.
    Numerically stable through efficient in-place Cholesky operations.

    Examples
    --------
    >>> import numpy as np
    >>> from econometrust import GLS
    >>>
    >>> # Generate data with correlated errors
    >>> n = 100
    >>> X = np.random.randn(n, 2)
    >>>
    >>> # AR(1) error structure
    >>> rho = 0.7
    >>> Sigma = np.array([[rho**abs(i-j) for j in range(n)] for i in range(n)])
    >>>
    >>> eps = np.random.multivariate_normal(np.zeros(n), Sigma)
    >>> y = X @ [1.0, -0.5] + eps
    >>>
    >>> # Fit GLS model
    >>> model = GLS(fit_intercept=True)
    >>> model.fit(X, y, Sigma)
    >>> print(model.summary())
    """

    def __init__(self, fit_intercept: bool = True) -> None: ...
    def fit(self, X: np.ndarray, y: np.ndarray, sigma: np.ndarray) -> None:
        """Fit the GLS model using Cholesky whitening.

        Efficiently transforms the regression using Cholesky decomposition
        of the error covariance matrix, then applies OLS to whitened data.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Training data matrix.
        y : np.ndarray, shape (n_samples,)
            Target values.
        sigma : np.ndarray, shape (n_samples, n_samples)
            Error covariance matrix. Must be positive definite and symmetric.

        Raises
        ------
        ValueError
            If sigma is not positive definite, not symmetric, or arrays
            have incompatible dimensions.
        RuntimeError
            If Cholesky decomposition fails or regression cannot be solved.

        Notes
        -----
        The covariance matrix sigma represents Var(ε) up to scale σ².
        For efficiency, sigma is not stored after Cholesky decomposition.
        """
        ...

    def is_fitted(self) -> bool:
        """Check if the model has been fitted."""
        ...

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """GLS regression coefficients."""
        ...

    @property
    def intercept(self) -> Optional[float]:
        """GLS regression intercept."""
        ...

    @property
    def fit_intercept(self) -> bool:
        """Whether the model includes an intercept."""
        ...

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Generate predictions using the fitted GLS model.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Input data for prediction.

        Returns
        -------
        np.ndarray
            Predicted values: ŷ = Xβ̂ + intercept
        """
        ...

    def standard_errors(self) -> Optional[np.ndarray]:
        """Standard errors of GLS coefficients.

        Returns
        -------
        np.ndarray or None
            Standard errors from GLS covariance matrix: σ²(X'Σ⁻¹X)⁻¹
        """
        ...

    def t_statistics(self) -> Optional[np.ndarray]:
        """T-statistics for GLS coefficients."""
        ...

    def p_values(self) -> Optional[np.ndarray]:
        """P-values for GLS coefficient significance tests."""
        ...

    def confidence_intervals(self, alpha: float = 0.05) -> Optional[np.ndarray]:
        """Confidence intervals for GLS coefficients."""
        ...

    def summary(self) -> str:
        """Generate GLS regression summary."""
        ...

    @property
    def mse(self) -> Optional[float]:
        """Mean squared error of whitened residuals.

        Returns
        -------
        float or None
            MSE from the whitened regression: ê*'ê*/(n-k)
        """
        ...

    @property
    def r_squared(self) -> Optional[float]:
        """R-squared from whitened regression.

        Returns
        -------
        float or None
            R² from the transformed model: 1 - RSS*/TSS*
        """
        ...

    @property
    def r_squared_adj(self) -> Optional[float]:
        """Adjusted R-squared accounting for degrees of freedom.

        Returns
        -------
        float or None
            Adjusted R² = 1 - (1-R²)*(n-1)/(n-k-1) where n is sample size
            and k is number of parameters. Penalizes model complexity.
        """
        ...

    @property
    def residuals(self) -> Optional[np.ndarray]:
        """Original scale residuals.

        Returns
        -------
        np.ndarray or None
            Residuals on original scale: ê = y - Xβ̂
        """
        ...

    @property
    def n_samples(self) -> Optional[int]:
        """Number of samples used in fitting."""
        ...

    @property
    def n_features(self) -> Optional[int]:
        """Number of features (excluding intercept)."""
        ...

    def __repr__(self) -> str: ...

class IV:
    """Instrumental Variables regression for exactly identified models.

    High-performance IV estimator for exactly identified systems where
    regressors are endogenous (correlated with error term). Uses instrumental
    variables to obtain consistent parameter estimates with optimized
    numerical algorithms.

    This implementation is specifically designed for exactly identified models
    where the number of instruments equals the number of regressors. For
    overidentified cases, use the TSLS estimator instead.

    Parameters
    ----------
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model.

    Notes
    -----
    IV estimation for exactly identified models:
    β̂ = (Z'X)⁻¹Z'y where Z are instruments, X are regressors

    Assumptions:
    - Instrument relevance: Cov(Z, X) ≠ 0 (instruments predict regressors)
    - Instrument exogeneity: Cov(Z, ε) = 0 (instruments uncorrelated with errors)
    - Exact identification: dim(Z) = dim(X) (number instruments = regressors)

    Covariance matrix: Var(β̂) = σ²(Z'X)⁻¹(Z'Z)(Z'X)⁻¹'

    IV estimates generally have higher variance than OLS but are consistent
    under endogeneity, while OLS is inconsistent but more efficient under
    exogeneity.

    Examples
    --------
    >>> import numpy as np
    >>> from econometrust import IV
    >>>
    >>> # Generate data with endogenous regressor
    >>> n = 200
    >>> Z = np.random.randn(n, 2)  # Instruments
    >>> u = np.random.randn(n)     # Unobserved factor
    >>>
    >>> # X correlated with error through u (endogeneity)
    >>> X = Z @ [0.8, 0.6] + 0.5 * u + np.random.randn(n, 2) * 0.1
    >>> y = X @ [1.0, -0.5] + u + np.random.randn(n) * 0.1
    >>>
    >>> # Fit IV model
    >>> model = IV(fit_intercept=True)
    >>> model.fit(Z, X, y)
    >>> print(model.summary())
    """

    def __init__(self, fit_intercept: bool = True) -> None: ...
    def fit(
        self, instruments: np.ndarray, regressors: np.ndarray, targets: np.ndarray
    ) -> None:
        """Fit the IV model for exactly identified case.

        Computes IV estimates using the closed-form solution for exactly
        identified systems with robust numerical algorithms.

        Parameters
        ----------
        instruments : np.ndarray, shape (n_samples, n_instruments)
            Instrumental variables matrix Z. Must have same number of columns
            as regressors for exact identification.
        regressors : np.ndarray, shape (n_samples, n_features)
            Endogenous regressors matrix X. Variables suspected of being
            correlated with the error term.
        targets : np.ndarray, shape (n_samples,)
            Target values (dependent variable) y.

        Raises
        ------
        ValueError
            If number of instruments ≠ number of regressors (not exactly identified),
            insufficient samples, or mismatched array dimensions.
        RuntimeError
            If Z'X matrix is singular (weak instruments) or system cannot be solved.

        Notes
        -----
        Requires n_samples > n_features + fit_intercept for identification.
        The Z'X matrix must be invertible (instruments must be relevant).

        For overidentified models (more instruments than regressors), use TSLS.
        For underidentified models (fewer instruments), the model is not identified.
        """
        ...

    def is_fitted(self) -> bool:
        """Check if the model has been fitted."""
        ...

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """IV regression coefficients.

        Returns
        -------
        np.ndarray or None
            Consistent estimates β̂ᴵⱽ for endogenous regressors.
        """
        ...

    @property
    def intercept(self) -> Optional[float]:
        """IV regression intercept."""
        ...

    @property
    def fit_intercept(self) -> bool:
        """Whether the model includes an intercept."""
        ...

    def predict(self, regressors: np.ndarray) -> np.ndarray:
        """Generate predictions using fitted IV coefficients.

        Parameters
        ----------
        regressors : np.ndarray, shape (n_samples, n_features)
            Regressor values for prediction. Note: these should be the
            actual regressor values, not instrumental variables.

        Returns
        -------
        np.ndarray
            Predicted values: ŷ = Xβ̂ᴵⱽ + intercept

        Notes
        -----
        Predictions use the original regressors X, not instruments Z.
        For out-of-sample prediction, exogeneity of regressors is assumed.
        """
        ...

    def standard_errors(self) -> Optional[np.ndarray]:
        """Standard errors of IV coefficients.

        Returns
        -------
        np.ndarray or None
            Standard errors computed from IV covariance matrix:
            SE = √(diag(σ²(Z'X)⁻¹(Z'Z)(Z'X)⁻¹'))
        """
        ...

    def t_statistics(self) -> Optional[np.ndarray]:
        """T-statistics for IV coefficient significance tests."""
        ...

    def p_values(self) -> Optional[np.ndarray]:
        """P-values for IV coefficient significance tests."""
        ...

    def confidence_intervals(self, alpha: float = 0.05) -> Optional[np.ndarray]:
        """Confidence intervals for IV coefficients."""
        ...

    def summary(self) -> str:
        """Generate comprehensive IV regression summary.

        Returns
        -------
        str
            Formatted summary including IV estimates, standard errors,
            significance tests, and diagnostic information about
            instrument strength and model specification.
        """
        ...

    def covariance_matrix(self) -> Optional[np.ndarray]:
        """Covariance matrix of IV coefficient estimates.

        Returns
        -------
        np.ndarray or None
            IV covariance matrix: σ²(Z'X)⁻¹(Z'Z)(Z'X)⁻¹'
            Shape (n_features, n_features).
        """
        ...

    @property
    def mse(self) -> Optional[float]:
        """Mean squared error of IV residuals.

        Returns
        -------
        float or None
            MSE = ê'ê/(n-k) where ê = y - Xβ̂ᴵⱽ
        """
        ...

    @property
    def r_squared(self) -> Optional[float]:
        """R-squared (with caution for IV models).

        Returns
        -------
        float or None
            R² = 1 - RSS/TSS. Note: R² can be negative for IV models
            and should be interpreted carefully due to endogeneity.
        """
        ...

    @property
    def r_squared_adj(self) -> Optional[float]:
        """Adjusted R-squared accounting for degrees of freedom.

        Returns
        -------
        float or None
            Adjusted R² = 1 - (1-R²)*(n-1)/(n-k-1) where n is sample size
            and k is number of parameters. Penalizes model complexity.
            Note: Can be negative for IV models due to endogeneity.
        """
        ...

    @property
    def residuals(self) -> Optional[np.ndarray]:
        """IV regression residuals.

        Returns
        -------
        np.ndarray or None
            Residuals: ê = y - Xβ̂ᴵⱽ
        """
        ...

    @property
    def n_samples(self) -> Optional[int]:
        """Number of samples used in fitting."""
        ...

    @property
    def n_features(self) -> Optional[int]:
        """Number of features (excluding intercept)."""
        ...

    def __repr__(self) -> str: ...

class TSLS:
    """Two-Stage Least Squares regression for overidentified models.

    High-performance TSLS estimator for overidentified instrumental variables
    models where the number of instruments exceeds the number of regressors.
    Features optimized two-stage algorithm with intelligent numerical methods
    and memory-efficient implementation.

    TSLS provides consistent estimates when regressors are endogenous by using
    a two-stage procedure: first stage predicts endogenous regressors using
    instruments, second stage regresses outcome on predicted values.

    Parameters
    ----------
    fit_intercept : bool, default=True
        Whether to calculate the intercept for this model.

    Notes
    -----
    Two-Stage Least Squares procedure:

    Stage 1: X̂ = Z(Z'Z)⁻¹Z'X  (predict regressors using instruments)
    Stage 2: β̂ = (X̂'X̂)⁻¹X̂'y  (regress outcome on predicted regressors)

    TSLS covariance matrix: Var(β̂) = σ²(X̂'X̂)⁻¹ where σ² = ê'ê/(n-k)

    Requirements:
    - Overidentification: number of instruments ≥ number of regressors
    - Instrument relevance: instruments must predict regressors (strong first stage)
    - Instrument exogeneity: instruments uncorrelated with structural error

    TSLS is consistent and asymptotically normal under these conditions.
    Standard errors account for the two-stage estimation procedure.

    The implementation uses intelligent algorithm selection (Normal equations vs SVD)
    in both stages for optimal numerical stability and computational efficiency.

    Examples
    --------
    >>> import numpy as np
    >>> from econometrust import TSLS
    >>>
    >>> # Generate overidentified IV model
    >>> n = 300
    >>> Z = np.random.randn(n, 4)  # 4 instruments
    >>> u = np.random.randn(n)     # Unobserved factor
    >>>
    >>> # 2 endogenous regressors (overidentified: 4 > 2)
    >>> X = Z @ [0.7, 0.5, 0.4, 0.3] + 0.6 * u + np.random.randn(n, 2) * 0.1
    >>> y = X @ [1.2, -0.8] + u + np.random.randn(n) * 0.1
    >>>
    >>> # Fit TSLS model
    >>> model = TSLS(fit_intercept=True)
    >>> model.fit(Z, X, y)
    >>> print(model.summary())
    """

    def __init__(self, fit_intercept: bool = True) -> None: ...
    def fit(
        self, instruments: np.ndarray, regressors: np.ndarray, targets: np.ndarray
    ) -> None:
        """Fit the TSLS model using optimized two-stage procedure.

        Implements efficient TSLS algorithm with automatic algorithm selection
        in both stages for optimal numerical stability and performance.

        Parameters
        ----------
        instruments : np.ndarray, shape (n_samples, n_instruments)
            Instrumental variables matrix Z. Must have at least as many
            columns as regressors for identification.
        regressors : np.ndarray, shape (n_samples, n_features)
            Endogenous regressors matrix X. Variables suspected of being
            correlated with the error term.
        targets : np.ndarray, shape (n_samples,)
            Target values (dependent variable) y.

        Raises
        ------
        ValueError
            If number of instruments < number of regressors (underidentified),
            insufficient samples, or mismatched array dimensions.
        RuntimeError
            If first stage regression fails (weak instruments) or second
            stage cannot be solved.

        Notes
        -----
        Requires:
        - n_instruments ≥ n_features (identification condition)
        - n_samples > n_features + fit_intercept (degrees of freedom)
        - Strong first stage: F-statistic typically > 10 for reliable inference

        Algorithm automatically selects between Normal equations and SVD
        based on problem size and conditioning for numerical stability.

        Memory optimized: does not store large intermediate matrices after fitting.
        """
        ...

    def is_fitted(self) -> bool:
        """Check if the model has been fitted."""
        ...

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """TSLS regression coefficients.

        Returns
        -------
        np.ndarray or None
            Consistent estimates β̂ᵀˢᴸˢ from two-stage procedure.
        """
        ...

    @property
    def intercept(self) -> Optional[float]:
        """TSLS regression intercept."""
        ...

    @property
    def fit_intercept(self) -> bool:
        """Whether the model includes an intercept."""
        ...

    def predict(self, regressors: np.ndarray) -> np.ndarray:
        """Generate predictions using fitted TSLS coefficients.

        Parameters
        ----------
        regressors : np.ndarray, shape (n_samples, n_features)
            Regressor values for prediction. These should be the actual
            regressor values, not instrumental variables.

        Returns
        -------
        np.ndarray
            Predicted values: ŷ = Xβ̂ᵀˢᴸˢ + intercept

        Notes
        -----
        Predictions use original regressors X, not instruments Z or
        fitted values X̂. For out-of-sample prediction, exogeneity
        of regressors is assumed.
        """
        ...

    def standard_errors(self) -> Optional[np.ndarray]:
        """Standard errors of TSLS coefficients.

        Returns
        -------
        np.ndarray or None
            Standard errors from TSLS covariance matrix accounting
            for two-stage estimation uncertainty.
        """
        ...

    def t_statistics(self) -> Optional[np.ndarray]:
        """T-statistics for TSLS coefficient significance tests."""
        ...

    def p_values(self) -> Optional[np.ndarray]:
        """P-values for TSLS coefficient significance tests."""
        ...

    def confidence_intervals(self, alpha: float = 0.05) -> Optional[np.ndarray]:
        """Confidence intervals for TSLS coefficients."""
        ...

    def summary(self) -> str:
        """Generate comprehensive TSLS regression summary.

        Returns
        -------
        str
            Formatted summary including TSLS estimates, standard errors,
            significance tests, overidentification information, and
            first-stage diagnostics.
        """
        ...

    def covariance_matrix(self) -> Optional[np.ndarray]:
        """Covariance matrix of TSLS coefficient estimates.

        Returns
        -------
        np.ndarray or None
            TSLS covariance matrix: σ²(X̂'X̂)⁻¹ where X̂ are predicted
            regressors from first stage. Shape (n_features, n_features).
        """
        ...

    @property
    def mse(self) -> Optional[float]:
        """Mean squared error of TSLS residuals.

        Returns
        -------
        float or None
            MSE = ê'ê/(n-k) where ê = y - Xβ̂ᵀˢᴸˢ
        """
        ...

    @property
    def r_squared(self) -> Optional[float]:
        """R-squared (with caution for TSLS models).

        Returns
        -------
        float or None
            R² = 1 - RSS/TSS using original regressors. Note: R² can be
            negative for IV models and should be interpreted carefully.
        """
        ...

    @property
    def r_squared_adj(self) -> Optional[float]:
        """Adjusted R-squared accounting for degrees of freedom.

        Returns
        -------
        float or None
            Adjusted R² = 1 - (1-R²)*(n-1)/(n-k-1) where n is sample size
            and k is number of parameters. Penalizes model complexity.
            Note: Can be negative for TSLS models due to endogeneity.
        """
        ...

    @property
    def residuals(self) -> Optional[np.ndarray]:
        """TSLS regression residuals.

        Returns
        -------
        np.ndarray or None
            Residuals: ê = y - Xβ̂ᵀˢᴸˢ computed using predicted
            regressors from first stage.
        """
        ...

    @property
    def n_samples(self) -> Optional[int]:
        """Number of samples used in fitting."""
        ...

    @property
    def n_features(self) -> Optional[int]:
        """Number of features (excluding intercept)."""
        ...

    def __repr__(self) -> str: ...

class FE:
    """Panel data Fixed Effects regression with clustered standard errors.

    High-performance Fixed Effects (Within) estimator for panel data models.
    Efficiently handles entity fixed effects by within-transformation (demeaning)
    and supports clustered standard errors to account for within-entity correlation
    of residuals.

    The estimator removes time-invariant entity heterogeneity by subtracting
    entity-specific means, then applies OLS to the demeaned data. This approach
    provides consistent estimates when unobserved heterogeneity is correlated
    with regressors.

    Parameters
    ----------
    robust : bool, default=False
        Whether to use clustered (robust) standard errors. When True, computes
        cluster-robust standard errors clustered by entity to account for
        within-entity correlation of residuals.

    Notes
    -----
    Fixed Effects model: yᵢₜ = αᵢ + Xᵢₜβ + εᵢₜ

    Within transformation: (yᵢₜ - ȳᵢ) = (Xᵢₜ - X̄ᵢ)β + (εᵢₜ - ε̄ᵢ)
    where ȳᵢ = (1/Tᵢ)∑ₜ yᵢₜ and X̄ᵢ = (1/Tᵢ)∑ₜ Xᵢₜ

    The estimator: β̂ = ((X̃'X̃)⁻¹X̃'ỹ) where X̃, ỹ are demeaned data.

    Fixed effects: α̂ᵢ = ȳᵢ - X̄ᵢβ̂ (entity-specific intercepts)

    Standard errors:
    - Classical: SE = √(σ̂²(X̃'X̃)⁻¹) where σ̂² = RSS/(NT-N-K)
    - Clustered: SE accounts for within-entity correlation using sandwich estimator

    Two R-squared measures:
    - Within R²: Goodness of fit for demeaned regression (variation within entities)
    - Overall R²: Total variation explained including fixed effects

    Memory optimized by efficient entity mapping and vectorized within transformation.

    Examples
    --------
    >>> import numpy as np
    >>> from econometrust import FE
    >>>
    >>> # Generate panel data: 100 entities, 5 time periods each
    >>> N, T = 100, 5
    >>> n_obs = N * T
    >>>
    >>> # Entity and time identifiers
    >>> entity_id = np.repeat(np.arange(N), T)
    >>>
    >>> # Generate data with entity fixed effects
    >>> np.random.seed(42)
    >>> alpha = np.random.randn(N)  # Entity fixed effects
    >>> X = np.random.randn(n_obs, 2)
    >>>
    >>> # Outcome with entity effects and time-varying component
    >>> y = np.repeat(alpha, T) + X @ [1.5, -2.0] + np.random.randn(n_obs) * 0.1
    >>>
    >>> # Fit Fixed Effects model
    >>> model = FE(robust=True)
    >>> model.fit(X, y, entity_id)
    >>> print(model.summary())
    >>>
    >>> # Make predictions for new data (requires entity_id)
    >>> X_new = np.random.randn(20, 2)
    >>> entity_id_new = np.repeat([0, 1], 10)  # Existing entities
    >>> y_pred = model.predict(X_new, entity_id_new)
    """

    def __init__(self, robust: bool = False) -> None: ...
    def fit(self, X: np.ndarray, y: np.ndarray, entity_id: np.ndarray) -> None:
        """Fit the Fixed Effects model using within transformation.

        Efficiently computes entity means and performs within transformation
        (demeaning) to remove fixed effects, then applies OLS to demeaned data.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Training data matrix. Each row is an observation.
        y : np.ndarray, shape (n_samples,)
            Target values (dependent variable).
        entity_id : np.ndarray, shape (n_samples,), dtype=int
            Entity identifiers for grouping observations. Each unique value
            represents a different entity (individual, firm, country, etc.).

        Raises
        ------
        ValueError
            If arrays have incompatible shapes, insufficient degrees of freedom,
            or number of entities >= number of observations.
        RuntimeError
            If the demeaned regression system cannot be solved.

        Notes
        -----
        Requires:
        - n_samples > n_features + n_entities (sufficient degrees of freedom)
        - At least 2 observations per entity for within variation
        - n_entities < n_samples (more observations than entities)

        The within transformation removes all time-invariant entity characteristics,
        identifying coefficients only from within-entity variation over time.

        Algorithm automatically selects between Cholesky decomposition and SVD
        based on problem size and numerical conditioning.
        """
        ...

    def is_fitted(self) -> bool:
        """Check if the model has been fitted to data.

        Returns
        -------
        bool
            True if fit() has been called successfully, False otherwise.
        """
        ...

    @property
    def coefficients(self) -> Optional[np.ndarray]:
        """Fixed Effects regression coefficients.

        Returns
        -------
        np.ndarray or None
            Array of shape (n_features,) containing fitted coefficients
            from within transformation. None if model not fitted.
        """
        ...

    @property
    def robust(self) -> bool:
        """Whether clustered standard errors are computed.

        Returns
        -------
        bool
            Configuration parameter set during initialization.
        """
        ...

    @property
    def fixed_effects(self) -> Optional[np.ndarray]:
        """Entity-specific fixed effects (intercepts).

        Returns
        -------
        np.ndarray or None
            Array of shape (n_entities,) containing estimated fixed effects
            α̂ᵢ = ȳᵢ - X̄ᵢβ̂ for each entity. None if model not fitted.
        """
        ...

    def predict(self, X: np.ndarray, entity_id: np.ndarray) -> np.ndarray:
        """Generate predictions using the fitted Fixed Effects model.

        Computes predictions as ŷ = Xβ̂ + α̂[entity_id] where α̂ are the
        estimated entity fixed effects.

        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Input data for prediction. Must have same number of features
            as training data.
        entity_id : np.ndarray, shape (n_samples,), dtype=int
            Entity identifiers for prediction samples. Must contain only
            entity IDs that were present in the training data.

        Returns
        -------
        np.ndarray, shape (n_samples,)
            Predicted values: ŷ = Xβ̂ + α̂[entity_id]

        Raises
        ------
        ValueError
            If model not fitted, X has wrong number of features, or
            entity_id contains unknown entities.

        Notes
        -----
        Can only predict for entities present in training data since
        their fixed effects were estimated. For new entities, the
        model would need to be refitted or use a random effects approach.
        """
        ...

    def standard_errors(self) -> Optional[np.ndarray]:
        """Standard errors of Fixed Effects coefficients.

        Returns
        -------
        np.ndarray or None
            Standard errors of coefficients. Uses cluster-robust estimator
            (clustered by entity) if robust=True, classical estimator otherwise.
        """
        ...

    def t_statistics(self) -> Optional[np.ndarray]:
        """T-statistics for coefficient significance tests.

        Returns
        -------
        np.ndarray or None
            T-statistics: t = β̂ / SE(β̂) for testing H₀: β = 0
        """
        ...

    def p_values(self) -> Optional[np.ndarray]:
        """P-values for two-sided coefficient significance tests.

        Returns
        -------
        np.ndarray or None
            P-values for H₀: βⱼ = 0 vs H₁: βⱼ ≠ 0. Uses t-distribution
            with appropriate degrees of freedom (NT - N - K).
        """
        ...

    def confidence_intervals(self, alpha: float = 0.05) -> Optional[np.ndarray]:
        """Confidence intervals for Fixed Effects coefficients.

        Parameters
        ----------
        alpha : float, default=0.05
            Significance level. Confidence level = 1 - alpha.

        Returns
        -------
        np.ndarray or None
            Array of shape (n_features, 2) containing [lower, upper] bounds
            for each coefficient at the specified confidence level.
        """
        ...

    def summary(self) -> str:
        """Generate comprehensive Fixed Effects regression summary.

        Returns
        -------
        str
            Formatted summary including coefficients, standard errors,
            t-statistics, p-values, within R², overall R², and model
            diagnostics specific to panel data.
        """
        ...

    def covariance_matrix(self) -> Optional[np.ndarray]:
        """Covariance matrix of Fixed Effects coefficient estimates.

        Returns
        -------
        np.ndarray or None
            Covariance matrix Var(β̂). Classical or cluster-robust depending
            on configuration. Shape (n_features, n_features).
        """
        ...

    @property
    def mse(self) -> Optional[float]:
        """Mean squared error of residuals.

        Returns
        -------
        float or None
            MSE = RSS / (NT - N - K) where RSS is residual sum of squares,
            NT is total observations, N is number of entities, and K is
            number of regressors.
        """
        ...

    @property
    def r_squared(self) -> Optional[float]:
        """Overall R-squared (total variation explained).

        Returns
        -------
        float or None
            Overall R² measuring fraction of total variance explained by
            the model including fixed effects. Compares total predictions
            (X̂β̂ + α̂ᵢ) to grand mean of y.
        """
        ...

    @property
    def within_r_squared(self) -> Optional[float]:
        """Within R-squared (within-entity variation explained).

        Returns
        -------
        float or None
            Within R² measuring fraction of within-entity variance explained
            by regressors after removing fixed effects. This is the R² from
            the demeaned regression: 1 - RSS_within/TSS_within.
        """
        ...

    @property
    def residuals(self) -> Optional[np.ndarray]:
        """Fixed Effects regression residuals.

        Returns
        -------
        np.ndarray or None
            Residuals from demeaned regression: ê = ỹ - X̃β̂ where ỹ, X̃
            are within-transformed (demeaned) data. Shape (n_samples,).
        """
        ...

    @property
    def n_samples(self) -> Optional[int]:
        """Number of observations used in fitting.

        Returns
        -------
        int or None
            Total sample size NT across all entities and time periods.
        """
        ...

    @property
    def n_features(self) -> Optional[int]:
        """Number of time-varying regressors.

        Returns
        -------
        int or None
            Number of regressors K (excluding fixed effects).
        """
        ...

    @property
    def n_entities(self) -> Optional[int]:
        """Number of entities in the panel.

        Returns
        -------
        int or None
            Number of unique entities N in the dataset.
        """
        ...

    def __repr__(self) -> str: ...

# -*- coding: utf-8 -*-
"""
Main module for sider-captcha-solver package
This file enables: from sider_captcha_solver import CaptchaPredictor
"""

# When installed as a package, src becomes sider_captcha_solver
try:
    # Try package import first (when installed via pip)
    from sider_captcha_solver.models.predictor import CaptchaPredictor
except ImportError:
    # Fallback to development import
    from src.models.predictor import CaptchaPredictor

__version__ = '1.0.1'
__all__ = ['CaptchaPredictor']
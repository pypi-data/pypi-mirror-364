from setuptools import setup, find_packages

setup(
      name="ThermoSim",
      version="2.3",
      packages= find_packages(),
      install_requires = [
          "numpy",
          "scipy",
          "matplotlib",
          "CoolProp",
          "pandas",
          "CoolProp",
          "pymoo"
          ],
      
      )
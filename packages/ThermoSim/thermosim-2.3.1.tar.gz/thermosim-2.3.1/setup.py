from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setup(
      name="ThermoSim",
      version="2.3.1",
      author="Md. Waheduzzaman Nouman",
      description="A simulation package for thermodynamic systems",
      long_description=long_description,
      long_description_content_type="text/markdown",
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
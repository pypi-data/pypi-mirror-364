import setuptools

setuptools.setup(
      name='cohere_ui',
      author='Barbara Frosik, Ross Harder',
      author_email='bfrosik@anl.gov',
      url='https://github.com/advancedPhotonSource/cohere/cohere-ui',
      version='4.2.4',
      packages=['cohere_ui', 
                'cohere_ui.api', 
                'cohere_ui.beamlines.aps_1ide', 
                'cohere_ui.beamlines.aps_34idc', 
                'cohere_ui.beamlines.esrf_id01', 
                'cohere_ui.beamlines.Petra3_P10', 
                'cohere_ui.beamlines.simple'],
      install_requires=[
                         'pyqt5',
                         'scikit-image',
                         'xrayutilities',
                         'pyvista',
                         'scipy==1.14.1',
                         'notebook',
                         'gputil',
                        ],
      classifiers=[
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
      ],
)

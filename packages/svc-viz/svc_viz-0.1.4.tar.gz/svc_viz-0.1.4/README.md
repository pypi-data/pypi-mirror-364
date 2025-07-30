# SVC-VIZ
![PyPI](https://img.shields.io/pypi/v/svc-viz)
![Python Version](https://img.shields.io/pypi/pyversions/svc-viz)
![GitHub last commit](https://img.shields.io/github/last-commit/marquisvictor/svc-viz)
![GitHub stars](https://img.shields.io/github/stars/marquisvictor/svc-viz?style=social)


<div align="center"><img src="examples/img/svcvizlogo.png" width="600px" /></div>

The spatially varying coefficient visualization (svc-viz) tool is an open-source Python software package designed to faciilitate the visualization of SVC model results with minimal effort. Svc-viz provides a codified interface for interpreting the results of local regression models based on the existing best practices for visualizing these models, requiring only a minimal amount of coding.

<div align="center"><img src="examples/img/svcviz-diagram.png" width="600px" /></div> 
<br /><br />

### Features
- Enables visualization of coefficient estimates from SVC models, adhering to visualization best practices as outlined in Irekponor and Oshan (in preparation).
- Facilitates exploration of replicability by comparing coefficient surfaces across two different SVC models.
- Provides a user-friendly 3-panel visualization template for systematic and consistent analysis.
- Offers simplicity and compatibility with any SVC model, ensuring broad applicability with minimal effort.

### Installation:

svc-viz can be installed from PyPI:

```bash
$ pip install svc-viz
```

To install the latest version from Github:

```bash
$ pip install git+https://github.com/marquisvictor/svc-viz.git
```


### Citation & Related Research

This package was developed in support of the research paper:

<i>"Reproducible visualization strategies for spatially varying coefficient models: Incorporating uncertainty and assessing replicability"</i>  
Available on GitHub: [2025_CaGIS_Special-Issue_Article](https://github.com/marquisvictor/2025_CaGIS_Special-Issue_Article)

If you use `svc-viz` in your work, please cite the paper and link to this repository to support continued development and visibility of the tool.


### License information

See the file “LICENSE.txt” for information on the history of this software, terms & conditions for usage, and a DISCLAIMER OF ALL WARRANTIES.

### Questions or Contributions?

Feel free to open an [issue](https://github.com/marquisvictor/svc-viz/issues) or submit a pull request. Contributions are welcome!

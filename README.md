# Cubix

Cubix is a simple, 100% python written, module for computing persistent homology in an alternative way. Given a data cloud *S* of **R**^n, it builds a simplicial cubic complex covering *S* and makes a filtration over this complex using a kernel density estimator (KDE) of *S*.  For a formal definition of the method and the simplicial cubic homology implemented, we redirect the reader to the paper 'Filtraciones cúbicas mediante KDE's para el cálculo de homología persistente' ---writen in Spanish--- available on the Github repository.

## Dependencies
Cubix has very few dependences:
* [numpy](https://pypi.org/project/numpy/) for numerical treatment
* [scipy](https://pypi.org/project/scipy/) as it uses *scipy.stats.gaussian_kde()* as kernel function
* [matplotlib](https://pypi.org/project/matplotlib/) for plotting

All of them are available in PyPI.


## Install
You can easily install Cubix via *pip*:
```
pip install cubix
``` 
## Usage
First of all, you must import the module:
```python
import cubix 
``` 
The second step is choosing the data cloud to analyze. Cubix class *Cloud* for these objects. You can create your cloud importing points from a CSV file just like: 
```python
X = cubex.Cloud(csv="input_file.csv")
``` 
If you have your *N* points of **R**^n stored in a numpy array (let's call it *array*) with shape *n x N* you can make a *Cloud* with them with:
```python
X = cubex.Cloud(data=array)
``` 
Alternatively, Cubix has methods to generate random data clouds with some particular shapes: the spheres *S⁰* (in **R**), *S¹* (in **R**²) and *S²* (in **R**³) , the torus *T²* (in **R**³), the real projective spaces **RP**² (in **R**⁴), and de wedge sum of two spheres *S¹vS¹* (in  **R**²). These are subclasses of *Cloud* so you can easily instantiate a 2000-point cloud with *S²* shape like:
```python
X = cubex.S2(center=(2,1,4), r=5, err=0.1, N=2000)
``` 
For more information about the arguments accepted to instantiate this classes, please read the documentation of each one.

*Cloud* class have some useful methods for plotting the data when possible. The following instruction will plot the points of the data cloud when dimension of the space is between 1 and 3.
```python
X.plot()
``` 
With the next one, you'll be able to see a representation of the KDE of the cloud with the precission you desire:
```python
X.kde_plot()
``` 

Once you have your cloud *X*, you can calculate the persistence homology of it. You just have to write:
```python
h = X.persistent_homology()
``` 
 Of course, this will run the algorithm with default values. Arguments accepted by *persistence_homology* are:
 * *n* - precision of the cubic complex covering the cloud (number of cubes per direction of **R**^n). Default: 10.
 * *margin* - parameter to make the cubic complex bigger than the space occupied by the cloud. Ex: with *margin=0.1* the cubic complex will take a 10% more of space. Default: 0.1 
 * *pruning* - parameter to cut off the last (the most insignificant) cubes of the filtration in order to make the algorithm faster. Ex: *pruning=0.9* will keep only the 90% most significant cubes. Default: 0 (don't cut off).
 * *verbose* - If *True*, print by standard error the progress of the calculation. Default: False.

Finally, you can see the results in three ways. In a persistence diagram:
```python
h.persitence_diagram()
``` 
In a bar code with:
```python
h.bar_code()
```
Or explicitly with: 
```python
h.detail()
```

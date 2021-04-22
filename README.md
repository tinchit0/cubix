# Cubix

Cubix is a simple, 100% python written, module for computing persistent homology in alternative way. Given a data cloud *S* of **R**^n, it builds a simplicial cubic complex covering *S* and makes a filtration over this complex using a kernel density estimator (KDE) of *S*.  For a formal definition of the method and the simplicial cubic homology implemented, we redirect the reader to the paper 'Filtraciones en homología persistente mediante estimadores kernel de densidad' ---writen in Spanish--- available on the Github repository.

## Install
You can easily install Cubix via *pip*:
```
pip install cubix
``` 

## Basic usage
First of all, you must import the module:
```python
import cubix 
``` 
The second step is choosing the data cloud to analyze. Cubix class *Cloud* is designed to contain these objects. You can create your cloud importing points from a CSV file just like: 
```python
X = cubix.Cloud(csv="input_file.csv")
``` 
If you have your *N* points of **R**^n stored in a numpy array (let's call it *array*) with shape *n x N* you can make a *Cloud* with them with:
```python
X = cubix.Cloud(data=array)
``` 
Alternatively, Cubix has methods to generate random data clouds with some particular shapes: the spheres *S⁰* (in **R**), *S¹* (in **R**²) and *S²* (in **R**³) , the torus *T²* (in **R**³), the real projective spaces **RP**² (in **R**⁴), and de wedge sum of two spheres *S¹vS¹* (in  **R**²). These are subclasses of *Cloud* so you can easily instantiate a 2000-point cloud with *S²* shape like:
```python
X = cubix.S2(center=(2,1,4), r=5, err=0.1, N=2000)
``` 
For more information about the arguments accepted to instantiate this classes, please read the documentation of each one.

*Cloud* class have some useful methods for plotting (when possible) and exporting data. Take a look at those 3 methods: 
```python
X.plot()
X.kde_plot()
X.export_to_csv("output.csv")
``` 

Once you have your cloud *X*, you can calculate the persistence homology of it. You just have to create a variable of the class *PersistentHomology* this way:
```python
h = X.persistent_homology()
``` 
 Of course, this will run the algorithm with default values. Arguments accepted by *persistence_homology* are:
 * *n* - precision of the cubic complex covering the cloud (number of cubes per direction of **R**^n). Default: 10.
 * *margin* - parameter to make the cubic complex bigger than the space occupied by the cloud. Ex: with *margin=0.1* the cubic complex will take a 10% more of space. Default: 0.1 
 * *pruning* - parameter to cut off the last (the most insignificant) cubes of the filtration in order to make the algorithm faster. Ex: *pruning=0.9* will keep only the 90% most significant cubes. Default: 0 (don't cut off).
 * *verbose* - If *True*, print by standard error the progress of the calculation. Default: False.

Finally, you can see the results in three ways: a persistence diagram, a bar code or just explicitly printing out all born and death times:
```python
h.persitence_diagram()
h.bar_code()
h.detail()
```

For more information, please check the documentation in the source code.


*This software has been developed as part of the Final Degree Project in Mathematics for Universitat Autònoma de Barcelona (UAB). If you are interested in filtrations using KDE's and you understand Spanish, please take a look at the paper 'Filtraciones en homología persistente mediante estimadores kernel de densidad' available on the Github repository.*

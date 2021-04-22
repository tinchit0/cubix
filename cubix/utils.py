import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from itertools import combinations, product
from time import time


class Cube():
    """
    Simplicial cube of Z^n with size 1.

    Requiered arguments:
    root        -- Root point of the cube (n-tuple of integers)
    directions  -- Directions where the cube expands (m-tuple of integers bet-
                   ween 1 and n)

    Optional arguments:
    value       -- Value of the simplex in a filtration (real number)
    filtration  -- Filtration where the cube belongs
    """

    def __init__(self, root, directions, value=0, filtration=None):
        self.root = root
        self.directions = directions
        self.value = value
        self.filtration = filtration
        self.homology_class = None

    @property
    def dimension(self):
        """ Dimension of the cube """
        return len(self.directions)

    @property
    def space_dimension(self):
        """ Dimension of the space where the cube belongs """
        return len(self.root)

    @property
    def points(self):
        """ List of cube's vertex """
        cube_points = [self.root]
        for direction in self.directions:
            new_points = []
            for point in cube_points:
                new_point = Cube.point_expand(point, direction)
                new_points.append(new_point)
            cube_points.extend(new_points)
        return cube_points

    @staticmethod
    def point_expand(point, direction):
        """ Augments in 1 the given point in the a certain direction """
        new_point = list(point)
        new_point[direction] += 1
        return tuple(new_point)

    @staticmethod
    def directions_pop(directions, direction):
        """ Extracts one direction from a list """
        new_directions = list(directions)
        new_directions.remove(direction)
        return tuple(new_directions)

    def border(self):
        """ Returns a list with cube faces """
        border_list = []
        for direction in self.directions:
            new_directions = Cube.directions_pop(self.directions, direction)
            new_point = Cube.point_expand(self.root, direction)
            if self.filtration is not None:
                border_list.append(self.filtration.cubic_complex[
                                   (self.root, new_directions)])
                border_list.append(self.filtration.cubic_complex[
                                   (new_point, new_directions)])
            else:
                border_list.append(Cube(self.root, new_directions))
                border_list.append(Cube(new_point, new_directions))
        return border_list

    def diferencial(self):
        """ Sum of homology classes of cube's border """
        return sum(s.homology_class for s in self.border())

    def __hash__(self):
        return hash((self.root, self.directions))

    def __eq__(self, other):
        return self.root == other.root and self.directions == other.directions

    def __ne__(self, other):
        return self.root != other.root or self.directions != other.directions

    def __str__(self):
        return "C(%s,%s)" % (str(self.root), str(self.directions))

    def __repr__(self):
        return self.__str__()


class Filtration():
    """
    Cubic filtration with KDE under a data cloud.

    Requiered arguments:
    cloud       -- Data cloud
    precision  -- Number of points in each direction for the grid used (positi-
                  ve integer)

    Optional arguments:
    margin      -- Factor to augment grid size. Ex: 0.1 it will create a grid
                   10% bigger than the space occupied by the data cloud
    pruning     -- Cut off the filtration cubes with bigger value than pruning
                   (real number between 0 and 1)
    verbose     -- Print the bulding process
    """

    def __init__(self, cloud, precision, margin=0, pruning=0, verbose=False):
        self.cloud = cloud
        self.dimension = cloud.dimension
        self.precision = precision

        if not verbose:
            self.grid = Grid(cloud, precision, margin)
            self.values = self.grid.evaluate(cloud.kde)
            self.cubic_complex = {}
            self.build_cubic_complex()
            self.body = sorted(self.cubic_complex.values(),
                               key=lambda x: (x.value, x.dimension,
                                              x.root, x.directions))
            if pruning:
                self.prune(pruning)
        else:
            t0 = time()

            sys.stderr.write("    Building grid...")
            t = time()
            self.grid = Grid(cloud, precision, margin)
            sys.stderr.write("    Done! (%f s)\n" % (time() - t))

            sys.stderr.write("    Giving value to points...")
            t = time()
            self.values = self.grid.evaluate(cloud.kde)
            sys.stderr.write("    Done! (%f s)\n" % (time() - t))

            sys.stderr.write("    Building cubic complex...")
            t = time()
            self.cubic_complex = {}
            self.build_cubic_complex()
            sys.stderr.write("    Done! (%f s)\n" % (time() - t))

            sys.stderr.write("    Sorting...")
            t = time()
            self.body = sorted(self.cubic_complex.values(),
                               key=lambda x: (x.value, x.dimension,
                                              x.root, x.directions))
            sys.stderr.write("    Done! (%f s)\n" % (time() - t))

            if pruning:
                sys.stderr.write("    Pruning...")
                self.prune(pruning)
                sys.stderr.write("    Done! (%f s)\n" % (time() - t))

            sys.stderr.write("    Total time: %f s\n" % (time() - t0))

    def build_cubic_complex(self):
        """ Creates all cubes in the grid """
        maximum = max(self.values.ravel())
        for dim in range(self.dimension + 1):
            for point in self.grid.positions:
                possible_directions = self.grid.possible_directions(point)
                for directions in combinations(possible_directions, dim):
                    dirs = tuple(directions)
                    cube = Cube(point, dirs, filtration=self)
                    if dim == 0:
                        cube.value = 1 - self.values[point] / maximum
                    else:
                        cube.value = max(s.value for s in cube.border())
                    self.cubic_complex[(point, dirs)] = cube

    def prune(self, n):
        """ Cuts off cubes with bigger value than n """
        self.body = [x for x in self[n]]

    def sorted_points(self):
        """ Sort grid points per value """
        return sorted(self.grid.positions, key=lambda x: self.values[x])

    def __getitem__(self, n):
        for s in self.body:
            if s.value < n:
                yield s
            else:
                break

    def __len__(self):
        return len(self.body)

    def __repr__(self):
        return "<Filtration of R^%d with %d cubes>" \
            % (self.dimension, len(self))


class Grid():
    """
    Grid in R^n containing data cloud. The field mesh containg a map between
    grid indexes and the corresponding points.

    Requiered arguments:
    cloud       -- Data cloud
    precision  -- Number of points in each direction for the grid used (positi-
                  ve integer)

    Optional arguments:
    margin      -- Factor to augment grid size. Ex: 0.1 it will create a grid
                   10% bigger than the space occupied by the data cloud
    """

    def __init__(self, cloud, precision, margin=0):
        self.dimension = cloud.dimension
        self.precision = precision
        self.size = []
        self.mounting = []
        for row in cloud.data:
            m = row.min()
            M = row.max()
            if margin:
                L = M - m
                m -= L * margin
                M += L * margin
            self.size.append((m, M))
            self.mounting.append(np.linspace(m, M, num=self.precision))
        self.mesh = np.meshgrid(*self.mounting)

    @property
    def epsilon(self):
        """ Returns grid precision in each direction """
        return [(M - m) / self.precision for m, M in self.size]

    @property
    def shape(self):
        """ Shape of the grid """
        return tuple(self.dimension * [self.precision])

    @property
    def positions(self):
        """ Returns all indexes of the grid mesh """
        return [x for x in product(range(self.precision),
                                   repeat=self.dimension)]

    def possible_directions(self, point):
        """ Possible expanding directions of a point """
        directions = list(range(self.dimension))
        for i, coordinate in enumerate(point):
            if coordinate == self.precision - 1:
                directions.remove(i)
        return directions

    def evaluate(self, function):
        """ Evaluates a functions in all grid points """
        data_ravel = np.vstack([line.ravel() for line in self.mesh])
        values = function(data_ravel)
        return np.reshape(values, self.shape)

    def __getitem__(self, position):
        point = [self.mesh[i][position] for i in range(self.dimension)]
        return tuple(point)

    def __repr__(self):
        return "<Grid of R^%d with shape %s>" % (self.dimension,
                                                 str(self.shape))


class HomologyClass():

    def __init__(self, homology, dimension, generators=[], representants=[]):
        self.homology = homology
        self.dimension = dimension
        self.generators = set(generators)
        self.representants = set(representants)

    def collapse(self, other):
        other.representants |= self.representants
        for rep in self.representants:
            rep.homology_class = other
        self.homology._classes[self.dimension].remove(self)

    def add(self, other):
        self.generators ^= other.generators
        for _class in self.homology._classes[self.dimension]:
            if self.generators == _class.generators and _class is not self:
                self.collapse(_class)

    def __bool__(self):
        return bool(self.generators)

    def __add__(self, other):
        new_class = HomologyClass(self.homology, self.dimension)
        new_class.generators = self.generators ^ other.generators
        return new_class

    # Not sure if I really need this
    def __radd__(self, other):
        if other:
            return other.__add__(self)
        else:
            return self

    def __str__(self):
        return "[ %s ]" % " + ".join(g.__str__() for g in self.generators)

    def __repr__(self):
        return self.__str__()


class HomologyGenerator():

    def __init__(self, homology, dimension, born_time):
        self.homology = homology
        self.dimension = dimension
        self.born = born_time
        self.death = 1
        self.id = self.homology.generator_index
        self.homology.generator_index += 1

    def die(self, death_time):
        self.death = death_time

    def life(self):
        return self.death - self.born

    def becomes(self, to_class):
        for _class in self.homology._classes[self.dimension][:]:
            if self in _class.generators:
                _class.generators.remove(self)
                _class.add(to_class)

    def __str__(self):
        return "g%d" % self.id

    def __repr__(self):
        return self.__str__()


class PersistentHomology():
    """
    Persistent homology of a cubic filtration.

    Requiered arguments:
    filtration  -- Filtration

    Optional arguments:
    verbose     -- Print the building progress
    """

    def __init__(self, filtration, verbose=False):
        self.filtration = filtration
        self.dimension = filtration.dimension
        self.generator_index = 1
        self.holes = [[] for i in range(self.dimension + 1)]

        self.calculate(verbose=verbose)

    def calculate(self, verbose=False):
        """ Calculates persistent homology """
        __NULLCLASS_ = [HomologyClass(self, i)
                        for i in range(self.dimension + 1)]
        self._classes = [[__NULLCLASS_[i]] for i in range(self.dimension + 1)]
        if verbose:
            t0 = time()
            total = len(self.filtration.body)
            cont = 1
            sys.stderr.write("  Starting calculate..\n")
        for cube in self.filtration.body:
            if verbose:
                sys.stderr.write("\033[F")
                sys.stderr.write(
                    "    Processing cube %d of %d\n" % (cont, total))
                cont += 1
            dim = cube.dimension
            t = cube.value
            d = cube.diferencial()
            if d:
                # Kill generator
                younger = max(d.generators, key=lambda x: x.born)
                younger.becomes(
                    d + HomologyClass(self, dim, generators=[younger]))
                younger.die(death_time=t)
                if younger.life() == 0:
                    self.holes[dim - 1].remove(younger)
                cube.homology_class = __NULLCLASS_[dim]
            else:
                # New generator
                new_generator = HomologyGenerator(
                    self, dimension=dim, born_time=t)
                self.holes[dim].append(new_generator)
                new_class = HomologyClass(self, dim, generators=[
                                          new_generator], representants=[cube])
                self._classes[dim].append(new_class)
                cube.homology_class = new_class
        if verbose:
            sys.stderr.write("    Done!\n" % (time() - t))
            sys.stderr.write("    Total time: %f s\n" % (time() - t0))

    def detail(self):
        """ Prints persistent homology results """
        for dim in range(self.dimension):
            print("Dimension %d:" % dim)
            if self.holes[dim]:
                for g in self.holes[dim]:
                    print("   %f -> %f  (%lf)" % (g.born, g.death, g.life()))
            else:
                print("    No holes")

    def persistence_diagram(self, dimensions="all"):
        """ Persistence diagram plot"""
        CLASSES_COLORS = {
            0: 'red',
            1: 'green',
            2: 'fuchsia',
            3: 'blue',
            4: 'turquoise',
            5: 'lime',
            6: 'purple',
            7: 'gold',
            8: 'brown',
            9: 'navy',
        }

        MAX_COLORS = len(CLASSES_COLORS)

        if dimensions == "all":
            dimensions = range(self.dimension + 1)

        plt.title("Persistence diagram")
        plt.plot((0, 1), (0, 1), color='gray')
        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, 1.05])
        handles = []
        for dim in dimensions:
            if not self.holes[dim]:
                continue
            for hclass in self.holes[dim]:
                x = [hclass.born, hclass.born]
                y = [hclass.born, hclass.death]
                plt.plot([hclass.born, hclass.born], [hclass.born, hclass.death],
                         linewidth=2.0,
                         color=CLASSES_COLORS[dim % MAX_COLORS])
                plt.plot([hclass.born, hclass.death], [hclass.death, hclass.death],
                         linewidth=0.5, linestyle="dashed",
                         color=CLASSES_COLORS[dim % MAX_COLORS])
            handles.append(mpatches.Patch(color=CLASSES_COLORS[
                           dim % MAX_COLORS], label='H%d' % dim))
        plt.legend(handles=handles, loc=4)
        plt.show()

    def bar_code(self, dimensions="all"):
        """ Bar code plot """
        CLASSES_COLORS = {
            0: 'red',
            1: 'green',
            2: 'fuchsia',
            3: 'blue',
            4: 'turquoise',
            5: 'lime',
            6: 'purple',
            7: 'gold',
            8: 'brown',
            9: 'navy',
        }

        MAX_COLORS = len(CLASSES_COLORS)

        if dimensions == "all":
            dimensions = range(self.dimension + 1)

        plt.title("Bar code")
        handles = []
        height = 1
        for dim in dimensions:
            if not self.holes[dim]:
                continue
            for hclass in self.holes[dim]:
                x = [hclass.born, hclass.death]
                y = [height, height]
                plt.plot(x, y, linewidth=2.0,
                         color=CLASSES_COLORS[dim % MAX_COLORS])
                height += 1
            handles.append(mpatches.Patch(color=CLASSES_COLORS[
                           dim % MAX_COLORS], label='H%d' % dim))
        plt.xlim([-0.05, 1.05])
        plt.ylim([-0.05, height + 0.05])
        plt.legend(handles=handles, loc=4)
        plt.show()

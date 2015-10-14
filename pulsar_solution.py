"""A virtual pulsar class"""

# Just to be forward-compatible with Python 3
from __future__ import division, print_function, unicode_literals

import astropy.coordinates as C
import astropy.table as T
import astropy.units as U
import numpy as np

class Pulsar(object):
    name = None

    default_catalog = "atnf.xml"
    catalog = None

    def __init__(self, name, coords, period, period_derivative=None):
        self.name = name
        self.coords = coords
        self.period = period
        self.period_derivative = period_derivative
        if period_derivative is None:
            self.period_derivative = 0 * U.dimensionless_unscaled

    def prettyprint(self):
        ra = self.coords.ra.to_string(unit=U.hourangle, sep=':', precision=2)
        dec = self.coords.dec.to_string(unit=U.degree, sep=':', precision=2, alwayssign=True)
        print("Pulsar \"{}\":".format(self.name))
        print("  Coordinates (ICRS): RA = {} (h:m:s), DEC = {} (d:m:s)".format(ra, dec))
        print("  Period: {:.5e} s".format(self.period.to(U.s).value))
        print("  Period derivative: {:.5e} s / s".format(self.period_derivative.to(U.s / U.s).value))
        print("  Frequency: {:.5e} Hz".format(self.frequency.to(U.Hz).value))
        print("  Frequency derivative: {:.5e} Hz / s".format(self.frequency_derivative.to(U.Hz / U.s).value))

    def __repr__(self):
        # This function is called when you want to represent the instance as a string
        return "<Pulsar(%r)>" % self.name

    @property
    def frequency(self):
        return 1 / self.period

    @frequency.setter
    def frequency(self, freq):
        self.period = 1 / freq

    @property
    def frequency_derivative(self):
        return -self.period_derivative / self.period**2

    @frequency_derivative.setter
    def frequency_derivative(self, fdot):
        self.period_derivative = -fdot / self.frequency**2

    @classmethod
    def read_catalog(cls, fname=default_catalog): # The first argument is the class itself
        cls.catalog = T.Table.read(fname)

    @classmethod
    def from_catalog_row(cls, row, name=None):
        row = T.QTable(row)[0] # To handle units correctly

        if name is None:
            name = row['NAME']

        coords = C.SkyCoord(ra=row['RAJ'], dec=row['DECJ'], frame='icrs')
        return cls(name, coords, row['P0'], row['P1'])

    @classmethod
    def from_catalog(cls, name):
        if cls.catalog is None: # Ensure we have a catalog available
            cls.read_catalog()

        match = np.where((cls.catalog['NAME'] == name) | \
                         (cls.catalog['PSRJ'] == name))
        rows = cls.catalog[match]

        if len(rows) == 0:
            raise ValueError("Pulsar {!r} not found".format(name))

        return cls.from_catalog_row(rows[0], name)

# Testing routines -------------------------------------------------------------

import random
import testhelper as TH

@TH.register_test
def test_class():
    """Check if there is a Pulsar class"""
    if isinstance(Pulsar, type):
        print("OK, Pulsar is a class.")
    else:
        print("Something went wrong, the type of Pulsar is {!r}".format(type(Pulsar)))

@TH.register_test
def test_instance():
    """Try to create a Pulsar instance"""
    # Check if a constructor already exists
    if '__init__' in Pulsar.__dict__:
        print("Not performing this test because you already defined a constructor")
        return

    # Create a Pulsar
    psr = Pulsar()
    print("OK, we created a Pulsar instance: {!r}".format(psr))

@TH.register_test
def test_attribute():
    """Try to add a 'name' attribute to a Pulsar instance"""
    # Check if a constructor already exists
    if '__init__' in Pulsar.__dict__:
        print("Not performing this test because you already defined a constructor")
        return
    if 'name' in Pulsar.__dict__:
        print("Not performing this test because you already defined a 'name' attribute")
        return

    psr = Pulsar()
    # Set an attribute by hand
    psr.name = "Vela"
    print("OK, we created a Pulsar instance: {0!r}. Its name is {0.name}".format(psr))

@TH.register_test
def test_class_attribute():
    """Check that the Pulsar class now has a 'name' attribute"""
    if hasattr(Pulsar, "name"):
        print("OK, Pulsar now has a 'name' attribute. Its default value is {!r}".format(Pulsar.name))
    else:
        print("Something went wrong, the Pulsar class does not have a 'name' attribute!")

@TH.register_test
def test_prettyprint():
    """Try to call a method"""
    # Check if a constructor already exists, don't bother for now
    if '__init__' in Pulsar.__dict__:
        print("Not performing this test because you already defined a constructor")
        return

    psr = Pulsar()
    psr.name = "Vela"
    # Set the attributes by hand
    psr.coords = C.SkyCoord.from_name("Vela")
    psr.period = 0.089308556629 * U.s
    # Pretty-print the Pulsar object
    psr.prettyprint()

def make_crab():
    """ Create a representation of the Crab pulsar """
    name = "Crab"
    coords = C.SkyCoord.from_name("Crab pulsar")
    period = 0.0333924123 * U.s
    return Pulsar(name, coords, period)

@TH.register_test
def test_constructor():
    """Try to use the Pulsar constructor"""
    # Make a representation of the Crab pulsar
    psr = make_crab()
    # Print it
    psr.prettyprint()

@TH.register_test
def test_repr():
    """Try to show a textual version of a Pulsar object"""
    psr = make_crab()
    # Print the textual version
    print(psr)

@TH.register_test
def test_property():
    """Try out the properties of the Pulsar class"""
    # Make a representation of the Crab pulsar without the period derivative
    psr = make_crab()
    print("Without period derivative")
    psr.prettyprint()
    # Set the frequency derivative by hand
    psr.frequency_derivative = -3.77535E-10 * U.Hz / U.s
    print("With period derivative")
    psr.prettyprint()

@TH.register_test
def test_classmethod():
    """Try the from_catalog class method"""
    # Fetch a pulsar from the ATNF catalog
    psr = Pulsar.from_catalog("J1944+2236")
    psr.prettyprint()

@TH.register_test
def test_full():
    """Perform a full test"""
    # Print a random selection of 20 pulsars from the ATNF catalog
    Pulsar.read_catalog()
    print("Name".center(12), "RA".center(11), "DEC".center(12), "Freq".center(12), "Fdot".center(12), sep=" | ")
    print("".center(12), "h:m:s".center(11), "d:m:s".center(12), "Hz".center(12), "Hz/s".center(12), sep=" | ")
    print("-" * 12, "-" * 11, "-" * 12, "-" * 12, "-" * 12, sep="-+-")
    for prow in random.sample(Pulsar.catalog, 20): # Choose 20 pulsars to show
        psr = Pulsar.from_catalog_row(prow)
        name = psr.name
        ra = psr.coords.ra.to_string(unit=U.hourangle, sep=':', precision=2, pad=True)
        dec = psr.coords.dec.to_string(unit=U.degree, sep=':', precision=2, alwayssign=True, pad=True)
        freq = psr.frequency.to(U.Hz).value
        fdot = psr.frequency_derivative.to(U.Hz/U.s).value
        print("{:12s} | {:11s} | {:12s} | {:12.5e} | {:+12.5e}".format(name, ra, dec, freq, fdot))

# Main entry point: list available tests and ask which one to run --------------
if __name__ == '__main__':
    TH.test_main()


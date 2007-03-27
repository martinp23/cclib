import os, unittest
from Numeric import alltrue, array
from testall import getfile
from cclib.parser import Gaussian, GAMESS, Jaguar
import bettertest

class GenericCITest(bettertest.TestCase):
    """CI calculations."""
    nstates = 0
    
    def testnumberofstates(self):
        """ Are there nstate elements in etenergies/etsecs/etsyms?"""
        self.assertEqual(len(self.data.etenergies), self.nstates)
        self.assertEqual(len(self.data.etsecs), self.nstates)
        self.assertEqual(len(self.data.etsyms), self.nstates)
    
    def testetenergies(self):
        """ Are transition energies positive and rising?"""
        self.failUnless(alltrue(self.data.etenergies > 0.0))
        changes = self.data.etenergies[1:] - self.data.etenergies[:-1]
        self.failUnless(alltrue(changes > 0.0))

class GenericCISTest(GenericCITest):
    """CIS calculations."""
    
class GenericCISWaterTest(GenericCISTest):
    """CIS(RHF) calculations of water (STO-3G)."""
    # First four singlet/triplet state excitation energies [cm-1].
    # Based on output in GAMESS test.
    etenergies0 = array([98614.56, 114906.59, 127948.12, 146480.64])
    etenergies1 = array([82085.34,  98999.11, 104077.89, 113978.37])
    # First four singlet/triplet state excitation orbitals and coefficients.
    # Tuples: (from MO, to MO, coefficient) - don't need spin indices.
    # Based on output in GAMESS test.
    # Note that only coefficients larger than 0.1 are included here, as
    #   the Gaussian test does not contain smaller ones.
    etsecs0 = [ [(4, 5, -0.70710678)],
                [(4, 6, -0.70710678)],
                [(3, 5,  0.68368723)],
                [(2, 5,  0.31163855), (3, 6, -0.63471970)] ]
    etsecs1 = [ [(4, 5,  0.70710678)],
                [(2, 6, -0.16333506), (3, 6, -0.68422741)],
                [(4, 6,  0.70710678)],
                [(2, 5, -0.37899667), (3, 6, -0.59602876)] ]
                
    def testetenergiesvalues(self):
        """ Are etenergies within 50cm-1 of the correct values?"""
        indices0 = [i for i in range(self.nstates) if self.data.etsyms[i][0] == "S"]
        indices1 = [i for i in range(self.nstates) if self.data.etsyms[i][0] == "T"]
        singlets = [self.data.etenergies[i] for i in indices0]
        triplets = [self.data.etenergies[i] for i in indices1]
        # All programs do singlets.
        singletdiff = singlets[:4] - self.etenergies0
        self.failUnless(alltrue(singletdiff < 50))
        # Not all programs do triplets (i.e. Jaguar).
        if len(triplets) >= 4:
            tripletdiff = triplets[:4] - self.etenergies1
            self.failUnless(alltrue(tripletdiff < 50))

    def testetsecsvalues(self):
        """ Are etsecs correct and coefficients within 0.0005 of the correct values?"""
        indices0 = [i for i in range(self.nstates) if self.data.etsyms[i][0] == "S"]
        indices1 = [i for i in range(self.nstates) if self.data.etsyms[i][0] == "T"]
        singlets = [self.data.etsecs[i] for i in indices0]
        triplets = [self.data.etsecs[i] for i in indices1]
        # All programs do singlets.
        found = False
        for i in range(4):
            for exc in self.etsecs0[i]:
                for s in singlets[i]:
                    if s[0][0] == exc[0] and s[1][0] == exc[1]:
                        found = True
                        self.assertInside(s[2], exc[2], 0.0005)
        if not found:
            self.fail("Excitation %i->%s not found" %(exc[0], exc[1]))

class GaussianCISTest(GenericCISWaterTest):
    def setUp(self):
        self.data = data[0]
        self.nstates = 10

class GAMESSCISTest(GenericCISWaterTest):
    def setUp(self):
        self.data = data[1]
        self.nstates = 10

class Jaguar65CISTest(GenericCISWaterTest):
    def setUp(self):
        self.data = data[2]
        self.nstates = 5

names = [ "Gaussian", "GAMESS", "Jaguar" ]
tests = [ GaussianCISTest, GAMESSCISTest, Jaguar65CISTest ]
data = [getfile(Gaussian, "basicGaussian03", "water_cis.log"),
        getfile(GAMESS, "basicGAMESS-US", "water_cis.out"),
        getfile(Jaguar, "basicJaguar6.5", "water_cis.out")
        ]
              
if __name__=="__main__":
    total = errors = failures = 0

    for name,test in zip(names,tests):
        print "\n**** Testing %s ****" % name
        myunittest = unittest.makeSuite(test)
        a = unittest.TextTestRunner(verbosity=2).run(myunittest)
        total += a.testsRun
        errors += len(a.errors)
        failures += len(a.failures)

    print "\n\n********* SUMMARY OF CI TEST **************"
    print "TOTAL: %d\tPASSED: %d\tFAILED: %d\tERRORS: %d" % (total,total-(errors+failures),failures,errors)
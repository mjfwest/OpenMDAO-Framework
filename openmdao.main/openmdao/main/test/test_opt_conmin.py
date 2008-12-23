"""
Test the CONMIN optimizer component
"""

import unittest
import numpy

# pylint: disable-msg=F0401,E0611
from openmdao.main.component import Component
from openmdao.main.assembly import Assembly
from openmdao.lib.conmindriver import CONMINdriver
from openmdao.main.arrayvar import ArrayVariable
from openmdao.main.variable import INPUT,OUTPUT
from openmdao.main.float import Float

# we need to add the ImportFactory to the factorymanager to be 
# able to find plugin modules
import openmdao.main.factorymanager as factorymanager
from openmdao.main.importfactory import ImportFactory
factorymanager.register_factory(ImportFactory())

class OptRosenSuzukiComponent(Component):
    """ From the CONMIN User's Manual:
    EXAMPLE 1 - CONSTRAINED ROSEN-SUZUKI FUNCTION. NO GRADIENT INFORMATION.
    
         MINIMIZE OBJ = X(1)**2 - 5*X(1) + X(2)**2 - 5*X(2) +
                        2*X(3)**2 - 21*X(3) + X(4)**2 + 7*X(4) + 50
    
         Subject to:
    
              G(1) = X(1)**2 + X(1) + X(2)**2 - X(2) +
                     X(3)**2 + X(3) + X(4)**2 - X(4) - 8   .LE.0
    
              G(2) = X(1)**2 - X(1) + 2*X(2)**2 + X(3)**2 +
                     2*X(4)**2 - X(4) - 10                  .LE.0
    
              G(3) = 2*X(1)**2 + 2*X(1) + X(2)**2 - X(2) +
                     X(3)**2 - X(4) - 5                     .LE.0
                     
    This problem is solved beginning with an initial X-vector of
         X = (1.0, 1.0, 1.0, 1.0)
    The optimum design is known to be
         OBJ = 6.000
    and the corresponding X-vector is
         X = (0.0, 1.0, 2.0, -1.0)
    """
    
    # pylint: disable-msg=C0103
    def __init__(self, name, parent=None, desc=None):
        super(OptRosenSuzukiComponent, self).__init__(name, parent, desc)
        self.x = numpy.array([1.,1.,1.,1.],dtype=float)
        self.result = 0.
        ArrayVariable('x',self,iostatus=INPUT,entry_type=float)
        Float('result',self,iostatus=OUTPUT)
        
        self.opt_objective = 6.
        self.opt_design_vars = [0., 1., 2., -1.]

    def execute(self):
        """calculate the new objective value"""
        self.result = (self.x[0]**2 - 5.*self.x[0] + 
                       self.x[1]**2 - 5.*self.x[1] +
                       2.*self.x[2]**2 - 21.*self.x[2] + 
                       self.x[3]**2 + 7.*self.x[3] + 50)
        
        
class CONMINdriverTestCase(unittest.TestCase):
    """test CONMIN optimizer component"""

    def test_opt1(self):
        """test Rosen-Suzuki optimization problem using 
        CONMIN optimizer component"""
        top = Assembly('top',None)
        comp = OptRosenSuzukiComponent('comp', top)
        top.add_child(comp)
        top.workflow.add_node(comp)
        top.add_child(CONMINdriver('driver'))
        
        top.driver.iprint = 0
        top.driver.objective = 'comp.result'
        top.driver.maxiters = 30
        top.driver.design_vars = ['comp.x[0]','comp.x[1]',
                                  'comp.x[2]','comp.x[3]']
        # pylint: disable-msg=C0301
        top.driver.constraints = [
            'comp.x[0]**2+comp.x[0]+comp.x[1]**2-comp.x[1]+comp.x[2]**2+comp.x[2]+comp.x[3]**2-comp.x[3]-8',
            'comp.x[0]**2-comp.x[0]+2*comp.x[1]**2+comp.x[2]**2+2*comp.x[3]**2-comp.x[3]-10',
            '2*comp.x[0]**2+2*comp.x[0]+comp.x[1]**2-comp.x[1]+comp.x[2]**2-comp.x[3]-5']        
        top.run()
        # pylint: disable-msg=E1101
        self.assertAlmostEqual(top.comp.opt_objective, 
                               top.driver.objective_val, places=2)
        self.assertAlmostEqual(top.comp.opt_design_vars[0], 
                               top.comp.x[0], places=1)
        self.assertAlmostEqual(top.comp.opt_design_vars[1], 
                               top.comp.x[1], places=2)
        self.assertAlmostEqual(top.comp.opt_design_vars[2], 
                               top.comp.x[2], places=2)
        self.assertAlmostEqual(top.comp.opt_design_vars[3], 
                               top.comp.x[3], places=1)

    
if __name__ == "__main__":
    unittest.main()
    #suite = unittest.TestLoader().loadTestsFromTestCase(ContainerTestCase)
    #unittest.TextTestRunner(verbosity=2).run(suite)    




    
    
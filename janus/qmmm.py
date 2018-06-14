from copy import deepcopy
"""
QMMM class for QMMM computations
"""
class QMMM(object):

    def __init__(self, mm_wrapper, qm_wrapper, system):
        
        self.mm_wrapper = mm_wrapper
        self.qm_wrapper = qm_wrapper
        self.system = system
        
    def additive(self):
        """
        Gets energies of needed components and computes
        a qm/mm energy with a specified embedding method using
        an additive scheme
        """
        self.mm_wrapper = mm_wrapper
        self.qm_wrapper = mm_wrapper
        self.system = system

        #need to add if these things are none then do the following

        # Get MM energy on MM region
        if not system.second_subsys:
            system.second_subsys = mm_wrapper.get_second_subsys()

        # Get non coulomb MM energy on PS-SS interaction
        if not system.boundary:
            system.boundary = mm_wrapper.get_boundary(coulomb=False)

        # Get any link atom information
        if not system.boundary_info:
            system.boundary_info = mm_wrapper.get_boundary_info()

        # Get QM energy
        if not system.qm:
            # get QM positions from pdb
            if system.qm_positions == None:
                system.qm_positions = mm_wrapper.get_qm_positions() 
            system.qm = qm_wrapper.get_qm()

        # Compute total QM/MM energy based on additive scheme
        system.qmmm_energy = system.second_subsys['energy']\
                            + system.boundary['energy']\
                            + system.qm['energy']

    def subtractive(system):
        """
        Gets energies of needed components and computes
        a qm/mm energy with a subtractive mechanical embedding scheme
        """
        self.mm_wrapper = mm_wrapper
        self.qm_wrapper = mm_wrapper
        self.system = system

        mm_wrapper, qm_wrapper = initialize_wrappers(system)

        # Get MM energy on whole system
        if not system.entire_sys:
            system.entire_sys = mm_wrapper.get_entire_sys()

        # Get MM energy on QM region
        if not system.primary_subsys:
            system.primary_subsys = mm_wrapper.get_primary_subsys(link=True)

        # Get any link atom information
        if not system.boundary_info:
            system.boundary_info = mm_wrapper.get_boundary_info()

        # Get QM energy
        if not system.qm:
            # get QM positions from pdb
            if system.qm_positions == None:
                system.qm_positions = mm_wrapper.get_qm_positions() 
            system.qm = qm_wrapper.get_qm()

        # Compute the total QM/MM energy based on
        # subtractive Mechanical embedding
        system.qmmm_energy = system.entire_sys['energy']\
                            - system.primary_subsys['energy']\
                            + system.qm['energy']

        # Compute QM/MM gradients 
        system.qmmm_gradients = self.compute_gradients(scheme='subtractive')


    def compute_gradients(self, scheme = 'subtractive'):

        if scheme == 'subtractive':

            all_mm_grad, ps_mm_grad, qm_grad = self.system.entire_sys['gradients'], self.system.primary_subsys['gradients'], self.system.qm['gradients']
            qmmm_grad = deepcopy(all_mm_grad)
                
            # iterate over list of qm atoms
            for i, atom in enumerate(self.system.qm_atoms):

                # compute the qmmm gradient for the qm atoms: 
                # mm_entire - mm_primary - qm
                qmmm_grad[atom] += - ps_mm_grad[i] + qm_grad[i]
                
                if self.system.boundary_info:
                    q1 = int(self.system.boundary_info[0]['qm_id']) - 1
                    m1 = int(self.system.boundary_info[0]['mm_id']) - 1
                    g = self.system.boundary_info[0]['g_factor']
                    if atom == q1:
                        if self.system.boundary_treatment == 'link_atom':
                            # Project forces of link atoms onto the mm and qm atoms of the link atom bond
                            qmmm_grad[atom] += -(1 - g) * ps_mm_grad[-1] + (1 - g) * qm_grad[-1]
                            qmmm_grad[m1] += -g * ps_mm_grad[-1] + g * qm_grad[-1]

                        if self.system.boundary_treatment == 'RC' or self.system.boundary_treatment == 'RCD':
                            qmmm_grad[atom] += -(1 - g) * ps_mm_grad[-1] + (1 - g) * qm_grad[-1]
                            qmmm_grad[m1] += -g * ps_mm_grad[-1] + g * qm_grad[-1]

            
        if scheme == 'additive':
            pass

        return qmmm_grad
        

    def get_system(self):

        return self.system


from abc import ABC, abstractmethod
import mendeleev as mdlv

class QMWrapper(ABC):

    def __init__(self, class_type):
        """
        QM wrapper super class

        Note
        ----
        Since QMWrapper is a super class and has abstract methods
        the user cannot actually instantiate a QMWrapper object, but only its child objects
        """
        self.class_type = class_type

        self.qm_param = None
        self.external_charges = None
        self.charges = None
        self.is_open_shelled = False
        self.qm_geometry = None


    def get_energy_and_gradient(self, traj=None, geometry=None, include_coulomb='all', link_atoms=None, minimize=False, charges=None):
        """
        Gets the energy and gradient from a QM computation of the primary subsystem 

        Parameters
        ----------
        traj : MDtraj trajectory object
            A trajectory object from which to extract geometry information if geometry is None
        geometry : str
            A string containing geometry information as XYZ coordinates. Default is None.
        include_coulomb : str
            whether to include coulombic interactions. Not applicable for QM programs
        link_atoms : list
            indices of link_atoms
        minimize : bool
            whether to return the geometry optimized energy 
        charges : list
            charges and corresponding positions in angstroms as xyz coordinates

        Returns
        -------
        dict
            A dictionary with energy('energy') and gradient('gradients') information

        Examples
        --------
        >>> get_energy_and_gradient(traj=mdtraj, geometry=None)
        """
        
        if (geometry is None and traj is not None):
            self.get_geom_from_trajectory(traj)
        elif (geometry is not None and traj is None):
            self.set_qm_geometry(geometry)

        if charges is not None:
            self.external_charges = charges

        if self.qm_param is None:
            self.build_qm_param()

        if minimize is True:
            geom = self.optimize_geometry()
        else:
            self.compute_info()

        self.info = {}
        self.info['energy'] = self.energy
        self.info['gradients'] = self.gradient
        
        return self.info

            
    def get_geom_from_trajectory(self, qm_traj=None):
        """
        Obtains geometry information from an MDtrah trajectory object.

        Parameters
        ----------
        qm_traj : MDtraj object
             describes just the primary subsystem, default is None

        """

        out = ""
        line = '{:3} {: > 7.3f} {: > 7.3f} {: > 7.3f} \n '
        self.total_elec = 0.0

        for i in range(qm_traj.n_atoms):
            x, y, z =   qm_traj.xyz[0][i][0],\
                        qm_traj.xyz[0][i][1],\
                        qm_traj.xyz[0][i][2]

            symbol = qm_traj.topology.atom(i).element.symbol
            n = mdlv.element(symbol).atomic_number
            self.total_elec += n
            
            out += line.format(symbol, x*10, y*10, z*10)

        self.qm_geometry = out

        if self.total_elec % 2 != 0:
            self.total_elec += self.charge   # takes charge into account
            if self.total_elec % 2 != 0:
                self.is_open_shelled = True

    def set_qm_geometry(self, geom):
        """
        Sets self.qm_geometry as geom
        
        Parameters
        ----------
        geom : str
            A str containing an XYZ coordinate 
        """
        self.qm_geometry = geom

    @abstractmethod
    def compute_info(self):
        """
        Function implemented in individual child classes
        """
        pass

    @abstractmethod
    def build_qm_param(self):
        """
        Function implemented in individual child classes
        """
        pass

    @abstractmethod
    def optimize_geometry(self):
        """
        Function implemented in individual child classes
        """
        pass

    def get_main_info(self):
        """
        Function not implemented for QM wrappers
        """
        raise Exception('method not implemented for class')

    def set_external_charges(self):
        """
        Function not implemented for QM wrappers
        """
        raise Exception('method not implemented for class')

    def initialize(self):
        """
        Function not implemented for QM wrappers
        """
        raise Exception('method not implemented for class')

    def take_step(self, force):
        """
        Function not implemented for QM wrappers
        """
        raise Exception('method not implemented for class')

    def get_main_charges(self):
        """
        Function not implemented for QM wrappers
        """
        raise Exception('method not implemented for class')

    def convert_trajectory(self):
        """
        Function not implemented for QM wrappers
        """
        raise Exception('method not implemented for class')

    def convert_input(self):
        """
        Function not implemented for QM wrappers
        """
        raise Exception('method not implemented for class')

    def set_up_reporters(self):
        """
        Function not implemented for QM wrappers
        """
        raise Exception('method not implemented for class')
    

from abc import ABC, abstractmethod
import numpy as np
from janus.system import Buffer
from copy import deepcopy
import mdtraj as md
import mendeleev as mdlv

class Partition(ABC):

    nm_to_angstrom = 10.0000000

    def __init__(self, trajectory, topology, class_type):

        self.traj = trajectory
        self.topology = topology
        self.class_type = class_type
    

    def compute_COM(self, atoms):
        """
        Computes the center of mass of a specified group

        Parameters
        ----------
        atoms : list 
            indices defining the group to compute the COM for

        Returns
        -------
        numpy array
            COM xyz coordinates 
        dict
            the indices of each atom in the group and the atomic weight for each atom
        dict
            the indices of each atom in the group and the weight ratio of each atom to
            the total weight of the group (sum of all atomic weights)

        """
        
        xyz = np.zeros(3)
        M = 0

        atom_weight = {}
        weight_ratio = {}
        for i in atoms:

            symbol = self.traj.topology.atom(i).element.symbol
            m = mdlv.element(symbol).atomic_weight
            # this gives positions in nm
            position =  np.array(self.traj.xyz[0][i])

            M += m
            xyz += m * position
            atom_weight[i] = m

        for i in atoms:
            weight_ratio[i] = atom_weight[i]/M
            
        xyz *= 1/M
        
        return xyz, atom_weight, weight_ratio

    def edit_atoms(self, atoms, res_idx, remove=False, add=False):
        """
        Edits a given list of atoms based on give parameters.

        Parameters
        ----------
        atoms : list 
            List of atom indicies to performed the desired action on
        res_idx : int
            Index of the residue 
        remove : bool
            Whether to remove the atoms of residue res_idx from atoms.
            Default is False.
        add : bool
            Whether to add the atoms of residue res_idx to atoms
            Default is False.

        Returns
        -------
        list
            List of edited atoms

        Examples
        --------
        >>> atoms = edit_qm_atoms(atoms=[0,1,2], res_idx=0, remove=True)
        """

        top = self.topology

        if (remove is True and add is False):
            for a in top.residue(res_idx).atoms:
                if a.index in atoms:
                    atoms.remove(a.index)

        if (remove is False and add is True):
            for a in top.residue(res_idx).atoms:
                if a.index not in atoms:
                    atoms.append(a.index)

        atoms.sort()
        return atoms

    def get_residue_info(self, idx, qm_center_xyz=None):
        """
        Gets the COM information and distance from the qm_center 
        for a give residue. Saves the information in a 
        :class:`~janus.system.Buffer` object.

        Parameters
        ----------
        idx : int
            index of the residue
        qm_center_xyz : list
            XYZ coordinates of the qm_center as a list

        Returns
        ------- 
        :class:`~janus.system.Buffer` 
        
        """

        if qm_center_xyz is None:
            qm_center_xyz = self.qm_center_xyz

        buf = Buffer(ID=idx)

        for a in self.topology.residue(idx).atoms:
            buf.atoms.append(a.index)

        buf.COM_coord, buf.atom_weights, buf.weight_ratio = self.compute_COM(buf.atoms)
        buf.r_i = np.linalg.norm(buf.COM_coord - np.array(qm_center_xyz))*Partition.nm_to_angstrom

        return buf

    def compute_qm_center_info(self, qm_center):

        if len(qm_center) == 1:
            self.COM_as_qm_center = False
            self.qm_center_xyz = self.traj.xyz[0][qm_center[0]]
            qm_center_idx = qm_center
            temp_traj = self.traj
            self.qm_center_weight_ratio = {qm_center[0] : 1}
        else:
            self.COM_as_qm_center = True
            self.qm_center_xyz, self.qm_center_atom_weights, self.qm_center_weight_ratio = self.compute_COM(qm_center)
            t = deepcopy(self.traj)
            t.topology.add_atom('DUM', md.element.Element.getBySymbol('H'), t.topology.atom(0).residue, 1)
            for atom in t.topology.atoms:
                if atom.name == 'DUM':
                    qm_center_idx = [atom.index]
            t.xyz = np.append(t.xyz[0], [self.qm_center_xyz], axis=0)
            temp_traj = t

        return temp_traj, qm_center_idx

    def get_qm_atoms(self):

        return self.qm_atoms

    def get_qm_residues(self):

        return self.qm_residues
        
    def get_qm_center_info(self):
        return self.qm_center_weight_ratio

    def get_buffer_groups(self):
        
        return self.buffer_groups

    @abstractmethod
    def define_buffer_zone(self):
        """
        Function implemented in individual child classes
        """
        pass

    @abstractmethod
    def find_buffer_atoms(self):
        """
        Function implemented in individual child classes
        """
        pass
    

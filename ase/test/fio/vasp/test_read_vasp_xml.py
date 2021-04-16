import pytest

import numpy as np
from ase.io import read
from io import StringIO


@pytest.fixture()
def vasprun():
    # "Hand-written" (reduced) vasprun.xml
    sample_vasprun = """\
<?xml version="1.0" encoding="ISO-8859-1"?>
<modeling>
 <structure name="primitive_cell" >
  <crystal>
   <varray name="basis" >
    <v>       3.16000000       0.00000000       0.00000000 </v>
    <v>       0.00000000       3.16000000       0.00000000 </v>
    <v>       0.00000000       0.00000000       3.16000000 </v>
   </varray>
  </crystal>
  <varray name="positions" >
   <v>       0.00000000       0.00000000       0.00000000 </v>
   <v>       0.50000000       0.50000000       0.50000000 </v>
  </varray>
 </structure>
 <kpoints>
  <varray name="kpointlist" >
   <v>       0.00000000       0.00000000       0.00000000 </v>
  </varray>
 </kpoints>
 <atominfo>
  <atoms>       2 </atoms>
  <types>       1 </types>
  <array name="atoms" >
   <set>
    <rc><c>W </c><c>   1</c></rc>
    <rc><c>W </c><c>   1</c></rc>
   </set>
  </array>
 </atominfo>
 <structure name="initialpos" >
  <crystal>
   <varray name="basis" >
    <v>       3.16000000       0.00000000       0.00000000 </v>
    <v>       0.00000000       3.16000000       0.00000000 </v>
    <v>       0.00000000       0.00000000       3.16000000 </v>
   </varray>
   <i name="volume">     31.55449600 </i>
  </crystal>
  <varray name="positions" >
   <v>       0.00000000       0.00000000       0.00000000 </v>
   <v>       0.50000000       0.50000000       0.50000000 </v>
  </varray>
 </structure>
"""
    return sample_vasprun


@pytest.fixture()
def calculation():
    def factory(e_0_energy=-29.67691672,
                e_fr_energy=-29.67243317,
                forces=np.array([[7.58587457, -5.22590317, 6.88227285],
                                [-7.58587457, 5.22590317, -6.88227285]]),
                stress=np.array(
                        [[4300.36902090, -284.50040544, -1468.20603140],
                         [-284.50040595, 4824.17435683, -1625.37541639],
                         [-1468.20603158, -1625.37541697, 5726.84189498]])):
        # "Hand-written" calculation record
        sample_calculation = f"""\
 <calculation>
  <scstep>
   <energy>
    <i name="e_fr_energy">     32.61376955 </i>
    <i name="e_wo_entrp">     32.60797165 </i>
    <i name="e_0_energy">     32.61183692 </i>
   </energy>
  </scstep>
  <scstep>
   <energy>
    <i name="e_fr_energy">   {e_fr_energy:.8f} </i>
    <i name="e_wo_entrp">    -29.68588381 </i>
    <i name="e_0_energy">    {e_0_energy:.8f}   </i>
   </energy>
  </scstep>
  <structure>
   <crystal>
    <varray name="basis" >
     <v>       3.16000000       0.00000000       0.00000000 </v>
     <v>       0.00000000       3.16000000       0.00000000 </v>
     <v>       0.00000000       0.00000000       3.16000000 </v>
    </varray>
    <i name="volume">     31.55449600 </i>
    <varray name="rec_basis" >
     <v>       0.31645570       0.00000000       0.00000000 </v>
     <v>       0.00000000       0.31645570       0.00000000 </v>
     <v>       0.00000000       0.00000000       0.31645570 </v>
    </varray>
   </crystal>
   <varray name="positions" >
    <v>       0.00000000       0.00000000       0.00000000 </v>
    <v>       0.50000000       0.50000000       0.50000000 </v>
   </varray>
  </structure>
  <varray name="forces" >
   <v>      {forces[0, 0]:.8f} {forces[0, 1]:.8f} {forces[0, 2]:.8f} </v>
   <v>      {forces[1, 0]:.8f} {forces[1, 1]:.8f} {forces[1, 2]:.8f} </v>
  </varray>
  <varray name="stress" >
   <v>    {stress[0, 0]:.8f} {stress[0, 1]:.8f} {stress[0, 2]:.8f}  </v>
   <v>    {stress[1, 0]:.8f} {stress[1, 1]:.8f} {stress[1, 2]:.8f} </v>
   <v>    {stress[2, 0]:.8f} {stress[2, 1]:.8f} {stress[2, 2]:.8f} </v>
  </varray>
  <energy>
   <i name="e_fr_energy">   {e_fr_energy:.8f} </i>
   <i name="e_wo_entrp">    -29.68588381 </i>
   <i name="e_0_energy">    {e_0_energy:.8f} </i>
  </energy>
"""
        return sample_calculation

    return factory


def test_atoms(vasprun):

    atoms = read(StringIO(vasprun), index=-1, format='vasp-xml')

    # check number of atoms
    assert len(atoms) == 2

    # make sure it is still tungsten
    assert all(np.array(atoms.get_chemical_symbols()) == "W")

    # check scaled_positions
    expected_scaled_positions = np.array([[0.0, 0.0, 0.0],
                                          [0.5,  0.5, 0.5]])

    np.testing.assert_allclose(atoms.get_scaled_positions(),
                               expected_scaled_positions)

    expected_cell = np.array([[3.16, 0.0, 0.0],
                              [0.0, 3.16, 0.0],
                              [0.0, 0.0, 3.16]])

    # check cell
    np.testing.assert_allclose(atoms.cell, expected_cell)

    # check real positions
    np.testing.assert_allclose(atoms.positions,
                               expected_scaled_positions @
                               atoms.cell.complete())


def check_calculation(vasprun, index=-1,
                      expected_e_0_energy=-29.67691672,
                      expected_e_fr_energy=-29.67243317,
                      expected_forces=np.array([[7.58587457,
                                                 -5.22590317,
                                                 6.88227285],
                                                [-7.58587457,
                                                 5.22590317,
                                                 -6.88227285]]),
                      expected_stress=np.array([[4300.36902090,
                                                 -284.50040544,
                                                 -1468.20603140],
                                                [-284.50040595,
                                                 4824.17435683,
                                                 -1625.37541639],
                                                [-1468.20603158,
                                                 -1625.37541697,
                                                 5726.84189498]])
                      ):

    from ase.units import GPa

    atoms = read(StringIO(vasprun), index=index,
                 format='vasp-xml')

    assert atoms.get_potential_energy() == expected_e_0_energy

    assert (atoms.get_potential_energy(force_consistent=True) ==
            expected_e_fr_energy)

    np.testing.assert_allclose(atoms.get_forces(),
                               expected_forces)

    assertion_stress = -0.1 * GPa * expected_stress
    assertion_stress = assertion_stress.reshape(9)[[0, 4, 8, 5, 2, 1]]

    np.testing.assert_allclose(atoms.get_stress(), assertion_stress)


def test_calculation(vasprun, calculation):

    check_calculation(vasprun + calculation())


def test_two_calculations(vasprun, calculation):

    second_e_0_energy = -2.0
    second_e_fr_energy = -3.0
    second_forces = np.full((2, 3), np.pi)
    second_stress = np.full((3, 3), 2.0 * np.pi)

    second_calculation_record = calculation(e_0_energy=second_e_0_energy,
                                            e_fr_energy=second_e_fr_energy,
                                            forces=second_forces,
                                            stress=second_stress)

    extended_vasprun = vasprun + calculation() + second_calculation_record
    check_calculation(extended_vasprun,
                      expected_e_0_energy=second_e_0_energy,
                      expected_e_fr_energy=second_e_fr_energy,
                      expected_forces=second_forces,
                      expected_stress=second_stress)

    # make sure we can read the first (second from the end)
    # calculation by passing index=-2
    check_calculation(extended_vasprun,
                      index=-2)


def test_corrupted_calculation(vasprun, calculation):

    corrupted_e_0_energy = -10.0
    corrupted_e_fr_energy = -15.0
    corrupted_forces = np.full((2, 3), np.pi)
    corrupted_stress = np.full((3, 3), 2.0 * np.pi)

    second_calculation = calculation(e_0_energy=corrupted_e_0_energy,
                                     e_fr_energy=corrupted_e_fr_energy,
                                     forces=corrupted_forces,
                                     stress=corrupted_stress)

    # corrupted calculation that does not have energy record.
    # Thus the parser is expected to read the previous one.
    corrupted_record = '\n'.join(second_calculation.split('\n')[:-6])
    # assert that we actually do have two calculations in the set up
    check_calculation(vasprun + calculation() + corrupted_record, index=-2)
    # check that the parser skips the corrupted last one
    # Should there be a warning in this case?
    check_calculation(vasprun + calculation() + corrupted_record, index=-1)


def test_vasp_parameters(vasprun, calculation):

    from collections import OrderedDict

    vasp_parameters = """\
 <kpoints>
  <generation param="Monkhorst-Pack">
   <v type="int" name="divisions">       1        1        1 </v>
   <v name="usershift">      0.00000000       0.00000000       0.00000000 </v>
   <v name="genvec1">      1.00000000       0.00000000       0.00000000 </v>
   <v name="genvec2">      0.00000000       1.00000000       0.00000000 </v>
   <v name="genvec3">      0.00000000       0.00000000       1.00000000 </v>
   <v name="shift">      0.00000000       0.00000000       0.00000000 </v>
  </generation>
  <varray name="kpointlist" >
   <v>       0.00000000       0.00000000       0.00000000 </v>
  </varray>
  <varray name="weights" >
   <v>       1.00000000 </v>
  </varray>
 </kpoints>
<parameters>
  <separator name="electronic" >
   <i type="string" name="PREC">medium</i>
   <i name="ENMAX">    500.00000000</i>
   <i name="ENAUG">    373.43800000</i>
   <i name="EDIFF">      1.00000000</i>
   <separator name="electronic smearing" >
    <i type="int" name="ISMEAR">     1</i>
    <i name="SIGMA">      0.10000000</i>
    <i name="KSPACING">      0.50000000</i>
   </separator>
   <separator name="electronic startup" >
    <i type="int" name="ISTART">     0</i>
    <i type="int" name="ICHARG">     2</i>
    <i type="int" name="INIWAV">     1</i>
   </separator>
   <separator name="electronic exchange-correlation" >
    <i type="logical" name="LASPH"> F  </i>
    <i type="logical" name="LMETAGGA"> F  </i>
   </separator>
  </separator>
  <separator name="ionic" >
   <i type="int" name="NSW"> 10000</i>
   <i type="int" name="IBRION">    11</i>
   <i name="EDIFFG">     10.00000000</i>
  </separator>
  <separator name="symmetry" >
   <i type="int" name="ISYM">     0</i>
   <i name="SYMPREC">      0.00001000</i>
  </separator>
 </parameters>   
    """
    atoms = read(StringIO(vasprun + calculation() + vasp_parameters),
                 index=-1, format="vasp-xml")

    expected_parameters = \
        OrderedDict([('kpoints_generation',
                      OrderedDict([('divisions', [1, 1, 1]),
                                   ('usershift', [0.0, 0.0, 0.0]),
                                   ('genvec1', [1.0, 0.0, 0.0]),
                                   ('genvec2', [0.0, 1.0, 0.0]),
                                   ('genvec3', [0.0, 0.0, 1.0]),
                                   ('shift', [0.0, 0.0, 0.0])])),
                     ('prec', 'medium'), ('enmax', 500.0),
                     ('enaug', 373.438), ('ediff', 1.0),
                     ('ismear', 1), ('sigma', 0.1),
                     ('kspacing', 0.5), ('istart', 0),
                     ('icharg', 2), ('iniwav', 1),
                     ('lasph', False), ('lmetagga', False),
                     ('nsw', 10000), ('ibrion', 11), ('ediffg', 10.0),
                     ('isym', 0), ('symprec', 1e-05)])

    assert atoms.calc.parameters == expected_parameters

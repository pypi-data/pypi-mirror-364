import numpy as np
from coarsify.src.tools.radii import element_radii, special_radii


def get_radius(atom, my_radii=None):
    """
    Finds the radius of the ball from the symbol or vice versa
    :return: The radius of the ball from the symbol or vice versa
    """
    if my_radii is None:
        elements_radii, specials_radii = element_radii, special_radii
    else:
        elements_radii, specials_radii = my_radii['elements'], my_radii['specials']
    # Get the radius and the element from the name of the ball
    if atom['res'] is not None and atom['res'].name in specials_radii:
        # Check if no ball name exists or its empty
        if atom['name'] is not None and atom['name'] != '':
            for i in range(len(atom['name'])):
                name = atom['name'][:-i]
                # Check the residue name
                if name in specials_radii[atom['res'].name]:
                    atom['rad'] = specials_radii[atom['res'].name][name]
    # If we have the type and just want the radius, keep scanning until we find the radius
    if atom['rad'] is None and atom['element'].upper() in elements_radii:
        atom['rad'] = elements_radii[atom['element'].upper()]
    # If indicated we return the symbol of ball that the radius indicates
    if atom['rad'] is None or atom['rad'] == 0:
        # Check to see if the radius is in the system
        if atom['rad'] in {elements_radii[_] for _ in elements_radii[1]}:
            atom['element'] = elements_radii[atom['rad']]
        else:
            # Get the closest ball to it
            min_diff = np.inf
            # Go through the radii in the system looking for the smallest difference
            for radius in elements_radii:
                if elements_radii[radius] - atom['rad'] < min_diff:
                    atom['element'] = elements_radii[radius]
    return atom['rad']


def make_atom(system=None, location=None, radius=None, index='', name='', residue='', chain='', chn_name='',
              res_name='', res_seq="", seg_id="", element="", chn=None, res=None, mass=None, set_index=None):
    atom = {
        # System groups
        'sys': system,           # System       :   Main system object

        'num': index,            # Number       :   The position index from the initial atom file
        'index': set_index,      # Set Index    :   The number that is in the index position of the pdb file
        'loc': location,         # Location     :   Set the location of the center of the sphere
        'rad': radius,           # Radius       :   Set the radius for the sphere object. Default is 1

        # Calculated Traits
        'vol': 0,                # Cell Volume  :   Volume of the voronoi cell for the atom
        'sa': 0,                 # Surface Area :   Surface area of the atom's cell
        'curv': 0,
        'box': [],               # Box          :   The grid location of the atom

        # Network objects
        'verts': [],             # Vertices     :   List of Vertex type objects
        'surfs': [],             # Surfaces     :   List of Surface type objects
        'edges': [],             # Edges        :   List of Edge type objects

        # Molecule traits
        'name': name,            # Name         :   Name retrieved from pdb file
        'res': res,              # Residue      :   Residue object of which the atom is a part
        'chn': chn,              # Chain        :   Chain object of which the atom is a part
        'chain': chain,          # Chain        :   Molecule chain the atom is a part of
        'chain_name': chn_name,  # Chain Name   :   Name of the chain that the ball is a part of
        'residue': residue,      # Residue      :   Class of molecule that the atom is a part of
        'res_name': res_name,    # Residue Name :   Name of the residue the ball is a part of
        'res_seq': res_seq,      # Sequence     :   Sequence of the residue that the atom is a part of
        'seg_id': seg_id,        # Segment ID   :   Segment identifier for the atom
        'element': element,      # Symbol       :   Element of the atom
        'mass': mass             # Mass         :   Mass of the atom
    }
    if atom['rad'] is None:
        atom['rad'] = get_radius(atom)
    return atom

import sqlite3


class Material():
    """Represents material (reflectance data points and curve function)."""

    def __init__(self, name, purity=(100, 0), other=None):
        self.name = name
        self.purity = purity
        self.other = other

    def mix(self, other, constrained=True):
        """Returns a list of materials created by two member mixing. """

        mixtures = [(75, 25), (50, 50), (25, 75)]
        if not constrained:
            mixtures = zip(range(1, 99, 1), range(99, 0, -1))
        names = [self.name + ':' + other.name + '({}:{})'.format(mix[0], mix[1])
                 for mix in mixtures]
        return [Material(name, purity=purity, other=other)
                for name, purity in zip(names, mixtures)]

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return "Material('{}')".format(self.name)


def read_data(file):
    """opens a connection to a database. Opens a text file of data from
    USGS Spectroscopy Lab. Ignores first 16 lines of header data. Saves
    subsequent rows to sqlite3 database in the format wavelength, reflectance,
    standard deviation, short material name: 'material', full material name:
    'full_name', and data source: 'source.'

    """

    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    f = open(file, 'r')
    data = f.readlines()
    f.close()

    n = 0
    source = data[0].strip('\n')
    full_name = data[14].strip('\n')
    material = full_name.split(' ')[0]
    for line in data[16:]:
        current = line.strip('\n')
        current = current.split('      ')
        current = [each.strip(' ') for each in current]
        del current[0]
        wavelength, reflectance, sd = current[0], current[1], current[2]
        if reflectance != '-1.23e34':
            # Convert micrometeres to nanometers
            wavelength = float(wavelength) * 1000
            reflectance = float(reflectance) * 100
            c.execute("""INSERT INTO main VALUES (?, ?, ?, ?, ?, ?);""",
                      (wavelength, reflectance, sd, material,
                       full_name, source))
    c.execute("""SELECT COUNT(*) FROM main;""")
    conn.commit()
    conn.close()


def create_db():
    """Creates a database data.db if none exists. Creates a table called main
    in data.db. Deletes and recreates the table main if it already exists

    """
    table_name = 'main'
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""DROP TABLE IF EXISTS {}""".format(table_name))
    c.execute("""CREATE TABLE {}(wavelength REAL, reflectance REAL, standard deviation REAL, material TEXT, full_name TEXT, source TEXT);""".format(table_name))
    conn.commit()
    conn.close()


concrete = Material('Concrete')

lawn = Material('Lawn_Grass')


quartz = Material('Quartz')

three_materials = {'lawn': lawn,
                   'concrete': concrete,
                   'sand': quartz
                   }
#
two_materials = {'lawn': lawn,
                 'concrete': concrete,
                 }
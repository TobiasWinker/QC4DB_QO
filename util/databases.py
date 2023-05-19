class Database:

    tables: list = None
    relations: dict = None

    def toId(self, s):
        if not s in self.tables:
            self.tables.append(s)
        return int(self.tables.index(s))

    def toString(self, id):
        return str(self.tables[id])

    def maxId(self):
        return len(self.tables) - 1

    def aliasT(self, t):
        return self.aliases[self.tables.index(t)]


class ErgastF1(Database):

    # define tables
    tables = ['constructorstandings', 'constructorresults', 'results', 'qualifying', 'pitstops', 'driverstandings', 'laptimes', 'constructors', 'status', 'races', 'drivers', 'seasons', 'circuits']

    aliases = ['cs', 'cr', 're', 'q', 'p', 'ds', 'l', 'c', 'st', 'ra', 'd', 'se', 'ci']

    relationsAlias = {
        ('cs', 'c'): 'cs.constructorId=c.constructorId',
        ('cs', 'ra'): 'cs.raceId=ra.raceId',
        ('cr', 'c'): 'cr.constructorId=c.constructorId',
        ('cr', 'ra'): 'cr.raceId=ra.raceId',
        ('re', 'c'): 're.constructorId=c.constructorId',
        ('re', 'st'): 're.statusId=st.statusId',
        ('re', 'ra'): 're.raceId=ra.raceId',
        ('re', 'd'): 're.driverId=d.driverId',
        ('q', 'c'): 'q.constructorId=c.constructorId',
        ('q', 'ra'): 'q.raceId=ra.raceId',
        ('q', 'd'): 'q.driverId=d.driverId',
        ('p', 'ra'): 'p.raceId=ra.raceId',
        ('p', 'd'): 'p.driverId=d.driverId',
        ('ds', 'ra'): 'ds.raceId=ra.raceId',
        ('ds', 'd'): 'ds.driverId=d.driverId',
        ('l', 'ra'): 'l.raceId=ra.raceId',
        ('l', 'd'): 'l.driverId=d.driverId',
        ('ra', 'ci'): 'ra.circuitId=ci.circuitId',
        ('ra', 'se'): 'ra.year=se.year'
    }

    # define primary foreign key relations
    relations = {
        ('constructorstandings', 'constructors'): 'constructorstandings.constructorId=constructors.constructorId',
        ('constructorstandings', 'races'): 'constructorstandings.raceId=races.raceId',
        ('constructorresults', 'constructors'): 'constructorresults.constructorId=constructors.constructorId',
        ('constructorresults', 'races'): 'constructorresults.raceId=races.raceId',
        ('results', 'constructors'): 'results.constructorId=constructors.constructorId',
        ('results', 'status'): 'results.statusId=status.statusId',
        ('results', 'races'): 'results.raceId=races.raceId',
        ('results', 'drivers'): 'results.driverId=drivers.driverId',
        ('qualifying', 'constructors'): 'qualifying.constructorId=constructors.constructorId',
        ('qualifying', 'races'): 'qualifying.raceId=races.raceId',
        ('qualifying', 'drivers'): 'qualifying.driverId=drivers.driverId',
        ('pitstops', 'races'): 'pitstops.raceId=races.raceId',
        ('pitstops', 'drivers'): 'pitstops.driverId=drivers.driverId',
        ('driverstandings', 'races'): 'driverstandings.raceId=races.raceId',
        ('driverstandings', 'drivers'): 'driverstandings.driverId=drivers.driverId',
        ('laptimes', 'races'): 'laptimes.raceId=races.raceId',
        ('laptimes', 'drivers'): 'laptimes.driverId=drivers.driverId',
        ('races', 'circuits'): 'races.circuitId=circuits.circuitId',
        ('races', 'seasons'): 'races.year=seasons.year'
    }


'''
# define tables
tables = ['badges', 'comments', 'posthistory', \
        'posts', 'users', 'votes']

# define primary foreign key relations
relations = {
    ('badges','users') : 'badges.userid=users.id',
    ('comments','users'): 'comments.userid=users.id',
    ('comments','posts'): 'comments.postid=posts.id',
    ('posthistory','posts'): 'posthistory.postid=posts.id',
    ('posthistory','users'): 'posthistory.userid=users.id',
    ('votes','posts'): 'votes.postid=posts.id',
    ('votes','users'): 'votes.userid=users.id'
}
'''

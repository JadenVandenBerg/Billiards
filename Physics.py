import phylib
import sqlite3
import os
import math
from copy import copy, deepcopy
import random

################################################################################
# import constants from phylib to global varaibles
BALL_RADIUS = phylib.PHYLIB_BALL_RADIUS
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER
HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH

SIM_RATE = phylib.PHYLIB_SIM_RATE
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON
DRAG = phylib.PHYLIB_DRAG
MAX_TIME = phylib.PHYLIB_MAX_TIME
MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS

FRAME_INTERVAL = 0.1

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />"""
FOOTER = """</svg>\n"""

# add more here

################################################################################
# the standard colours of pool balls
# if you are curious check this out:
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",  # no LIGHTRED
    "MEDIUMPURPLE",  # no LIGHTPURPLE
    "LIGHTSALMON",  # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",  # no LIGHTBROWN 
]


################################################################################
class Coordinate(phylib.phylib_coord):
  """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
  pass


################################################################################
class StillBall(phylib.phylib_object):
  """
    Python StillBall class.
    """

  def __init__(self, number, pos):
    """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

    # this creates a generic phylib_object
    phylib.phylib_object.__init__(self, phylib.PHYLIB_STILL_BALL, number, pos,
                                  None, None, 0.0, 0.0)

    self.__class__ = StillBall

  # add an svg method here
  def svg(self):
    cx = self.obj.still_ball.pos.x
    cy = self.obj.still_ball.pos.y
    r = BALL_RADIUS
    fill = BALL_COLOURS[self.obj.still_ball.number]

    if self.obj.still_ball.number == 0:
        svg_string = f'<circle id="cue" cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />\n'
    else:
        svg_string = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />\n'
    return svg_string


class RollingBall(phylib.phylib_object):
  """
    Python RollingBall class.
    """

  def __init__(self, number, pos, vel, acc):
    """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

    # this creates a generic phylib_object
    phylib.phylib_object.__init__(self, phylib.PHYLIB_ROLLING_BALL, number,
                                  pos, vel, acc, 0.0, 0.0)

    self.__class__ = RollingBall

  # add an svg method here
  def svg(self):
    cx = self.obj.rolling_ball.pos.x
    cy = self.obj.rolling_ball.pos.y
    r = BALL_RADIUS
    fill = BALL_COLOURS[self.obj.rolling_ball.number]

    if self.obj.rolling_ball.number == 0:
        svg_string = f'<circle id="cue" cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />\n'
    else:
        svg_string = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />\n'
    return svg_string


class Hole(phylib.phylib_object):
  """
    Python Hole class.
    """

  def __init__(self, pos):
    """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

    # this creates a generic phylib_object
    phylib.phylib_object.__init__(self, phylib.PHYLIB_HOLE, 0, pos, None,
                                  None, 0.0, 0.0)

    self.__class__ = Hole

  # add an svg method here
  def svg(self):
    cx = self.obj.hole.pos.x
    cy = self.obj.hole.pos.y
    r = BALL_DIAMETER * 2
    fill = "black"

    svg_string = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" />\n'
    return svg_string


class HCushion(phylib.phylib_object):
  """
    Python HCushion class.
    """

  def __init__(self, posY):
    """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

    # this creates a generic phylib_object
    phylib.phylib_object.__init__(self, phylib.PHYLIB_HCUSHION, 0, None,
                                  None, None, 0.0, posY)

    self.__class__ = HCUSHION

  # add an svg method here
  def svg(self):
    y = self.obj.hcushion.y
    if y != 2700:
        y -= 25

    return f'<rect width="1400" height="25" x="-25" y="{y}" fill="darkgreen" />\n'


class VCushion(phylib.phylib_object):
  """
    Python VCushion class.
    """

  def __init__(self, posX):
    """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

    # this creates a generic phylib_object
    phylib.phylib_object.__init__(self, phylib.PHYLIB_VCUSHION, 0, None,
                                  None, None, posX, 0.0)

    self.__class__ = VCUSHION

  # add an svg method here
  def svg(self):
    x = self.obj.vcushion.x
    if x != 1350:
        x -= 25

    return f'<rect width="25" height="2750" x="{x}" y="-25" fill="darkgreen" />\n'


################################################################################


class Table(phylib.phylib_table):
    """
        Pool table class.
    """

    def __init__(self):
        """
            Table constructor method.
            This method call the phylib_table constructor and sets the current
            object index to -1.
            """
        phylib.phylib_table.__init__(self)
        self.current = -1

    def __iadd__(self, other):
        """
            += operator overloading method.
            This method allows you to write "table+=object" to add another object
            to the table.
        """
        self.add_object(other)
        return self

    def __iter__(self):
        """
            This method adds iterator support for the table.
            This allows you to write "for object in table:" to loop over all
            the objects in the table.
        """
        return self

    def __next__(self):
        """
            This provides the next object from the table in a loop.
            """
        self.current += 1  # increment the index to the next object
        if self.current < MAX_OBJECTS:  # check if there are no more objects
            return self[self.current]  # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1  # reset the index counter
        raise StopIteration  # raise StopIteration to tell for loop to stop

    def __getitem__(self, index):
        """
            This method adds item retreivel support using square brackets [ ] .
            It calls get_object (see phylib.i) to retreive a generic phylib_object
            and then sets the __class__ attribute to make the class match
            the object type.
            """
        result = self.get_object(index)
        if result == None:
            return None
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion
        return result

    def __str__(self):
        """
            Returns a string representation of the table that matches
            the phylib_print_table function from A1Test1.c.
            """
        result = ""  # create empty string
        result += "time = %6.1f\n" % self.time  # append time
        for i, obj in enumerate(self):  # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i, obj)  # append object description
        return result  # return the string

    def segment(self):
        """
            Calls the segment method from phylib.i (which calls the phylib_segment
            functions in phylib.c.
            Sets the __class__ of the returned phylib_table object to Table
            to make it a Table object.
            """

        result = phylib.phylib_table.segment(self)
        if result:
            result.__class__ = Table
            result.current = -1
            return result

    def svg(self):
        string = HEADER
        for obj in self:
            if obj:
                string += obj.svg()

        string += FOOTER
        return string

    def roll( self, t ):
        new = Table()
        for ball in self:
            if isinstance( ball, RollingBall ):
                # create4 a new ball with the same number as the old ball
                new_ball = RollingBall( ball.obj.rolling_ball.number, Coordinate(0,0), Coordinate(0,0), Coordinate(0,0) )
                # compute where it rolls to
                phylib.phylib_roll( new_ball, ball, t )
                # add ball to table
                new += new_ball

            if isinstance( ball, StillBall ):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall( ball.obj.still_ball.number, Coordinate( ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y ) )
                # add ball to table
                new += new_ball
        # return table
        return new

    def copyTable(self, table):
        newTable = phylib.phylib_copy_table(table)
        newTable.__class__ = Table
        newTable.current = -1
        index = -1
        for obj in table:
            index += 1
            x = newTable[index]
        
        return newTable

    def cueBall(self):
        for obj in self:
            if isinstance(obj, StillBall) and obj.obj.still_ball.number == 0:
                return obj


def check_table_exists(table_name, cursor):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

class Database():
    def __init__( self, reset=False ):

        if reset is True:
            if os.path.exists("phylib.db"):
                os.remove("phylib.db")

        self.connect = sqlite3.connect("phylib.db")
        self.conn = self.connect

    def createDB(self):
        cursor = self.connect.cursor()
        if check_table_exists("Ball", cursor) is not True:
            cursor.execute("""
                CREATE TABLE Ball (
                    BALLID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    BALLNO INTEGER NOT NULL,
                    XPOS FLOAT NOT NULL,
                    YPOS FLOAT NOT NULL,
                    XVEL FLOAT,
                    YVEL FLOAT
                )
            """)

        if check_table_exists("TTable", cursor) is not True:
            cursor.execute("""
                CREATE TABLE TTable (
                    TABLEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    TIME FLOAT NOT NULL
                )
            """)

        if check_table_exists("BallTable", cursor) is not True:
            cursor.execute("""
                CREATE TABLE BallTable (
                    BALLID INTEGER NOT NULL,
                    TABLEID INTEGER NOT NULL,
                    FOREIGN KEY (BALLID) REFERENCES Ball,
                    FOREIGN KEY (TABLEID) REFERENCES TTable
                )
            """)

        if check_table_exists("Shot", cursor) is not True:
            cursor.execute("""
                CREATE TABLE Shot (
                    SHOTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    PLAYERID INTEGER NOT NULL,
                    GAMEID INTEGER NOT NULL,
                    FOREIGN KEY (PLAYERID) REFERENCES Player,
                    FOREIGN KEY (GAMEID) REFERENCES Game
                )
            """)
        
        if check_table_exists("TableShot", cursor) is not True:
            cursor.execute("""
                CREATE TABLE TableShot (
                    TABLEID INTEGER NOT NULL,
                    SHOTID INTEGER NOT NULL,
                    FOREIGN KEY (TABLEID) REFERENCES TTable,
                    FOREIGN KEY (SHOTID) REFERENCES Shot
                )
            """)

        if check_table_exists("Game", cursor) is not True:
            cursor.execute("""
                CREATE TABLE Game (
                    GAMEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    GAMENAME VARCHAR(64) NOT NULL
                )
            """)

        if check_table_exists("Player", cursor) is not True:
            cursor.execute("""
                CREATE TABLE Player (
                    PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    GAMEID INTEGER NOT NULL,
                    PLAYERNAME VARCHAR(64) NOT NULL,
                    FOREIGN KEY (GAMEID) REFERENCES Game
                )
            """)

        cursor.close()
        self.connect.commit()

    def readTable(self, tableID):
        table = Table()
        newID = tableID + 1
        cursor = self.connect.cursor()
        cursor.execute(f"""
            SELECT * FROM BallTable INNER JOIN Ball INNER JOIN TTable
            ON Ball.BALLID = BallTable.BALLID AND TTable.TABLEID = BallTable.TABLEID AND TTable.TABLEID = {newID}
        """)

        z = cursor.fetchall()
        if z == None or len(z) == 0:
            return None

        for x in range(len(z)):
            if z[x][6] == 0 and z[x][7] == 0:
                sb = StillBall(z[x][3], Coordinate(z[x][4], z[x][5]))
                table += sb
            else:
                rb_vel_x = z[x][6]
                rb_vel_y = z[x][7]
                rb_acc_x = 0
                rb_acc_y = 0

                speed = math.sqrt(rb_vel_x * rb_vel_x + rb_vel_y * rb_vel_y)
                if speed > VEL_EPSILON:
                    rb_acc_x = rb_vel_x / speed * DRAG
                    rb_acc_y = rb_vel_y / speed * DRAG

                rb = RollingBall(z[x][3], Coordinate(z[x][4], z[x][5]), Coordinate(z[x][6], z[x][7]), Coordinate(rb_acc_x, rb_acc_y))
                table += rb
        
        if len(z) != 0:
            table.time = z[0][9]
        else:
            table.time = 0
        cursor.close()
        self.connect.commit()

        return table

    def writeTable(self, table):
        cursor = self.connect.cursor()
        cursor.execute(f"""
            INSERT INTO TTable (TIME)
            VALUES ({table.time})
        """)

        cursor.execute("""
            SELECT last_insert_rowid()
        """)
        rowIDTable = cursor.fetchone()

        for item in table:
            insert = False
            if isinstance(item, StillBall):
                insert = True
                cursor.execute(f"""
                    INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL)
                    VALUES ({item.obj.still_ball.number}, {item.obj.still_ball.pos.x}, {item.obj.still_ball.pos.y}, 0, 0)
                """)
            elif isinstance(item, RollingBall):
                insert = True
                cursor.execute(f"""
                    INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL)
                    VALUES ({item.obj.rolling_ball.number}, {item.obj.rolling_ball.pos.x}, {item.obj.rolling_ball.pos.y}, {item.obj.rolling_ball.vel.x}, {item.obj.rolling_ball.vel.y})
                """)
            
            if insert:
                cursor.execute("""
                    SELECT last_insert_rowid()
                """)
                rowIDBall = cursor.fetchone()

                cursor.execute(f"""
                    INSERT INTO BallTable
                    VALUES ({rowIDBall[0]}, {rowIDTable[0]})
                """)
        
        cursor.close()
        self.connect.commit()

        return rowIDTable[0] - 1

    def getGame(self, gameID):
        cursor = self.connect.cursor()
        cursor.execute(f"""
            SELECT PLAYERNAME, GAMENAME FROM Player INNER JOIN Game
            ON Player.GAMEID = {gameID}
        """)

        allPlayers = cursor.fetchall()

        cursor.close()

        return allPlayers[0][1], allPlayers[0][0], allPlayers[1][0]

    def setGame(self, gameName, player1Name, player2Name):
        cursor = self.connect.cursor()
        cursor.execute(f"""
            INSERT INTO Game (GAMENAME)
            VALUES ('{gameName}')
        """)

        cursor.execute("""
            SELECT last_insert_rowid()
        """)
        gameID = cursor.fetchone()

        cursor.execute(f"""
            INSERT INTO Player (GAMEID, PLAYERNAME)
            VALUES {gameID[0], player1Name}
        """)
        cursor.execute(f"""
            INSERT INTO Player (GAMEID, PLAYERNAME)
            VALUES {gameID[0], player2Name}
        """)

        cursor.close()
        self.connect.commit()

        return gameID

    def newShot(self, gameID, playerName):
        cursor = self.connect.cursor()
        playerID = 0
        cursor.execute(f"""
            SELECT PLAYERID from Player
            WHERE PLAYERNAME = '{playerName}' AND GAMEID = '{gameID}'
        """)

        select = cursor.fetchall()

        if len(select) == 0:
            return None
        playerID = select[0][0]

        cursor.execute(f"""
            INSERT INTO Shot (PLAYERID, GAMEID)
            VALUES ({playerID}, {gameID})
        """)

        cursor.execute("""
            SELECT last_insert_rowid()
        """)
        shotID = cursor.fetchone()[0]

        return shotID

    def close( self ):
        self.connect.commit()
        self.connect.close()

class Game():
    def __init__( self, gameID=None, gameName=None, player1Name=None, player2Name=None ):
        self.db = Database(False)
        if gameID is not None and gameName is None and player1Name is None and player2Name is None:
            self.db.getGame(gameID + 1)
        elif gameID is None and gameName is not None and player1Name is not None and player2Name is not None:
            self.gameId = self.db.setGame(gameName, player1Name, player2Name)
        else:
            raise TypeError("Enter valid arguments")

    def shoot( self, gameName, playerName, table, xvel, yvel ):
        print("ENTERING SHOT")
        self.db.connect = sqlite3.connect("phylib.db")
        self.db.cursor = self.db.connect.cursor()

        cue_ball = table.cueBall()
        print(cue_ball)
        if cue_ball is None:
            print("CUEBALL NONE")
        xpos = cue_ball.obj.still_ball.pos.x
        ypos = cue_ball.obj.still_ball.pos.y

        cue_ball.type = phylib.PHYLIB_ROLLING_BALL
        cue_ball.obj.rolling_ball.pos.x = xpos
        cue_ball.obj.rolling_ball.pos.y = ypos
        cue_ball.obj.rolling_ball.vel.x = xvel
        cue_ball.obj.rolling_ball.vel.y = yvel
        cue_ball.obj.rolling_ball.number = 0

        speed = math.sqrt(xvel * xvel + yvel * yvel)
        if speed > VEL_EPSILON:
            cue_ball.obj.rolling_ball.acc.x = -xvel / speed * DRAG
            cue_ball.obj.rolling_ball.acc.y = -yvel / speed * DRAG
        else:
            cue_ball.obj.rolling_ball.acc.x = 0
            cue_ball.obj.rolling_ball.acc.y = 0

        shotID = self.db.newShot(self.gameId, playerName)
        lastTable = table
        while table:
            time1 = table.time
            print(f"ENTERING SEGMENT {time1}")
            lastTable = table
            tableCopy = table.copyTable(table)
            theTable = tableCopy.segment()
            if theTable is None:
                break


            time = theTable.time - time1
            time = math.floor(time / FRAME_INTERVAL)
            for x in range(time):
                elapsed = x * FRAME_INTERVAL
                newTable = tableCopy.roll(elapsed)
                newTable.time = tableCopy.time + elapsed

                tableID = self.db.writeTable(newTable)
                self.db.cursor.execute(f"""
                    INSERT INTO TableShot (SHOTID, TABLEID)
                    VALUES ('{shotID}', '{tableID}')
                """)

            time1 = theTable.time
            table = theTable
        
        possibleCue = lastTable.cueBall()
        if (possibleCue is None):
            lastTable += StillBall(0,  Coordinate(TABLE_WIDTH / 2.0, TABLE_LENGTH * 0.75))
        
        for item in lastTable:
            if item is not None and item.type == phylib.PHYLIB_ROLLING_BALL:
                item.obj.rolling_ball.vel.x = 0
                item.obj.rolling_ball.vel.y = 0
                item.obj.rolling_ball.acc.x = 0
                item.obj.rolling_ball.acc.y = 0
                item.__class__ = StillBall
        tableID = self.db.writeTable(lastTable)
        self.db.cursor.execute(f"""
                INSERT INTO TableShot (SHOTID, TABLEID)
                VALUES ('{shotID}', '{tableID}')
            """)

        self.db.connect.commit()
        self.db.cursor.close()

def nudge2():
    return random.uniform( -1.5, 1.5 );

def generateStartTableNoStr():
    table = Table()

    # 1 ball
    pos = Coordinate( 
                    TABLE_WIDTH / 2.0,
                    TABLE_LENGTH * 0.75,
                    )

    sb = StillBall( 0, pos )
    table += sb

    xP = TABLE_WIDTH / 2.0
    yP = TABLE_WIDTH / 2.0

    xLess = 0
    xMore = 0
    yMore = 0
    counter = 1
    for x in range(5):
        xMore = 0
        for y in range(x + 1):
            pos = Coordinate(xP - xLess + xMore + nudge2() , yP - yMore + nudge2())
            number = counter
            if number == 5:
                number = 8
            elif number == 8:
                number = 5
            sb = StillBall( number, pos )
            table += sb
            xMore += BALL_DIAMETER + 4.0
            counter += 1
        xLess += (BALL_DIAMETER+4.0) / 2
        yMore += BALL_DIAMETER+4.0

    return table

def generateStartTable():

    return generateStartTableNoStr().svg()

if __name__ == "__main__":
    db = Database(reset=True)
    db.createDB()
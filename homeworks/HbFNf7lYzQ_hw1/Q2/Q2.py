########################### DO NOT MODIFY THIS SECTION ##########################
#################################################################################
import sqlite3
from sqlite3 import Error
import csv
#################################################################################

## Change to False to disable Sample
SHOW = True

############### SAMPLE CLASS AND SQL QUERY ###########################
######################################################################
class Sample():
    def sample(self):
        try:
            connection = sqlite3.connect("sample")
            connection.text_factory = str
        except Error as e:
            print("Error occurred: " + str(e))
        print('\033[32m' + "Sample: " + '\033[m')
        
        # Sample Drop table
        connection.execute("DROP TABLE IF EXISTS sample;")
        # Sample Create
        connection.execute("CREATE TABLE sample(id integer, name text);")
        # Sample Insert
        connection.execute("INSERT INTO sample VALUES (?,?)",("1","test_name"))
        connection.commit()
        # Sample Select
        cursor = connection.execute("SELECT * FROM sample;")
        print(cursor.fetchall())

######################################################################

class HW2_sql():
    ############### DO NOT MODIFY THIS SECTION ###########################
    ######################################################################
    def create_connection(self, path):
        connection = None
        try:
            connection = sqlite3.connect(path)
            connection.text_factory = str
        except Error as e:
            print("Error occurred: " + str(e))
    
        return connection

    def execute_query(self, connection, query):
        cursor = connection.cursor()
        try:
            if query == "":
                return "Query Blank"
            else:
                cursor.execute(query)
                connection.commit()
                return "Query executed successfully"
        except Error as e:
            return "Error occurred: " + str(e)
    ######################################################################
    ######################################################################

    # GTusername [0 points]
    def GTusername(self):
        gt_username = "ndinapoli6"
        return gt_username
    
    # Part a.i Create Tables [2 points]
    def part_ai_1(self,connection):
        ############### EDIT SQL STATEMENT ###################################
        part_ai_1_sql = "CREATE TABLE movies(id integer, " \
                        "title text, " \
                        "score real)"
        ######################################################################

        return self.execute_query(connection, part_ai_1_sql)

    def part_ai_2(self,connection):
        ############### EDIT SQL STATEMENT ###################################
        part_ai_2_sql = "CREATE TABLE movie_cast(movie_id integer, " \
                        "cast_id integer, " \
                        "cast_name text, " \
                        "birthday text, " \
                        "popularity real)"
        ######################################################################

        return self.execute_query(connection, part_ai_2_sql)
    
    # Part a.ii Import Data [2 points]
    def part_aii_1(self,connection,path):
        ############### CREATE IMPORT CODE BELOW ############################
        file = open(path)
        movies = csv.reader(file)
        movies_sql = "INSERT INTO movies (id, title, score) VALUES (?,?,?)"
        cursor = connection.cursor()
        cursor.executemany(movies_sql, movies)
        connection.commit()
        #####################################################################

        sql = "SELECT COUNT(id) FROM movies;"
        cursor = connection.execute(sql)
        return cursor.fetchall()[0][0]
    
    def part_aii_2(self,connection, path):
        ############### CREATE IMPORT CODE BELOW ############################
        file = open(path)
        movie_cast = csv.reader(file)
        movie_cast_sql = "INSERT INTO movie_cast (movie_id, cast_id, cast_name, birthday, popularity) VALUES (?,?,?,?,?)"
        cursor = connection.cursor()
        cursor.executemany(movie_cast_sql, movie_cast)
        connection.commit()
        ######################################################################

        sql = "SELECT COUNT(cast_id) FROM movie_cast;"
        cursor = connection.execute(sql)
        return cursor.fetchall()[0][0]

    # Part a.iii Vertical Database Partitioning [5 points]
    def part_aiii(self,connection):
        ############### EDIT CREATE TABLE SQL STATEMENT ###################################
        part_aiii_sql = "CREATE TABLE cast_bio(cast_id integer, cast_name text, birthday text, popularity real)"
        ######################################################################

        self.execute_query(connection, part_aiii_sql)

        ############### CREATE IMPORT CODE BELOW ############################
        # part_aiii_insert_sql = "INSERT INTO cast_bio (cast_id, cast_name, birthday, popularity) SELECT cast_id, cast_name, birthday, popularity FROM movie_cast"
        part_aiii_insert_sql = "INSERT INTO cast_bio(cast_id, cast_name, birthday, popularity) " \
                               "SELECT DISTINCT movie_cast.cast_id, movie_cast.cast_name, movie_cast.birthday, movie_cast.popularity " \
                               "FROM movie_cast"
        ######################################################################

        self.execute_query(connection, part_aiii_insert_sql)

        sql = "SELECT COUNT(cast_id) FROM cast_bio;"
        cursor = connection.execute(sql)
        return cursor.fetchall()[0][0]

    # Part b Create Indexes [1 points]
    def part_b_1(self, connection):
        ############### EDIT SQL STATEMENT ###################################
        part_b_1_sql = "CREATE INDEX movie_index " \
                       "ON movies (id)"
        ######################################################################
        return self.execute_query(connection, part_b_1_sql)

    def part_b_2(self, connection):
        ############### EDIT SQL STATEMENT ###################################
        part_b_2_sql = "CREATE INDEX cast_index " \
                       "ON movie_cast (cast_id)"
        ######################################################################
        return self.execute_query(connection, part_b_2_sql)

    def part_b_3(self, connection):
        ############### EDIT SQL STATEMENT ###################################
        part_b_3_sql = "CREATE INDEX cast_bio_index " \
                       "ON cast_bio (cast_id)"
        ######################################################################
        return self.execute_query(connection, part_b_3_sql)
    
    # Part c Calculate a Proportion [3 points]
    def part_c(self,connection):
        ############### EDIT SQL STATEMENT ###################################
        part_c_sql = "SELECT printf('%.2f', " \
                     "(SELECT 100.0 * COUNT(*) " \
                     "FROM movies " \
                     "WHERE score >= 7 AND score <= 20) / (SELECT 1.0 * COUNT(*) FROM movies))"
        ######################################################################

        cursor = connection.execute(part_c_sql)
        return cursor.fetchall()[0][0]

    # Part d Find the Most Prolific Actors [4 points]
    def part_d(self,connection):
        ############### EDIT SQL STATEMENT ###################################
        part_d_sql = "SELECT cast_name, COUNT(*) " \
                     "FROM movie_cast " \
                     "WHERE popularity > 10 " \
                     "GROUP BY cast_id " \
                     "ORDER BY COUNT(*) DESC, cast_name " \
                     "LIMIT 5"
        ######################################################################
        cursor = connection.execute(part_d_sql)
        return cursor.fetchall()

    # Part e Find the Highest Scoring Movies With the Least Amount of Cast [4 points]
    def part_e(self,connection):
        ############### EDIT SQL STATEMENT ###################################
        part_e_sql = "SELECT title, printf('%.2f', score), COUNT(*) " \
                     "FROM movies " \
                     "INNER JOIN movie_cast ON movies.id = movie_cast.movie_id " \
                     "GROUP BY movies.id " \
                     "ORDER BY score DESC, COUNT(*) ASC, title ASC " \
                     "LIMIT 5"
        ######################################################################
        cursor = connection.execute(part_e_sql)
        return cursor.fetchall()
    
    # Part f Get High Scoring Actors [4 points]
    def part_f(self,connection):
        ############### EDIT SQL STATEMENT ###################################
        part_f_sql = "SELECT cast_id, cast_name, printf('%.2f', AVG(movies.score)) AS avg_score " \
                     "FROM movie_cast, movies " \
                     "WHERE movie_cast.movie_id = movies.id AND movies.score >=25 " \
                     "GROUP BY movie_cast.cast_id " \
                     "HAVING COUNT(*) > 2 " \
                     "ORDER BY avg_score DESC, movie_cast.cast_name ASC " \
                     "LIMIT 10"
        ######################################################################
        cursor = connection.execute(part_f_sql)
        return cursor.fetchall()

    # Part g Creating Views [6 points]
    def part_g(self,connection):
        ############### EDIT SQL STATEMENT ###################################
        part_g_sql = "CREATE VIEW good_collaboration AS " \
                     "SELECT " \
                     "LEAST(cast_member_id1, cast_member_id2) AS cast_member_id1, " \
                     "GREATEST(cast_member_id1, cast_member_id2) AS cast_member_id2, " \
                     "COUNT(DISTINCT movie_cast.movie_id) AS movie_count, " \
                     "AVG(m.score) AS average_movie_score " \
                     "FROM movie_cast " \
                     "INNER JOIN movie_cast mc2 ON movie_cast.movie_id = movie_cast.movie_id AND movie_cast.cast_member_id < movie_cast.cast_member_id " \
                     "INNER JOIN movies m ON movie_cast.movie_id = m.movie_id " \
                     "GROUP BY cast_member_id1, cast_member_id2 " \
                     "HAVING movie_count >= 2 AND average_movie_score >= 40"
        ######################################################################
        return self.execute_query(connection, part_g_sql)
    
    def part_gi(self,connection):
        ############### EDIT SQL STATEMENT ###################################
        part_g_i_sql = """
            SELECT good_collaboration.cast_member_id1 AS cast_member_id, cast_name, printf('%.2f', AVG(average_movie_score)) AS collaboration_score
            FROM (
                SELECT good_collaboration.cast_member_id1, AVG(average_movie_score) AS average_movie_score
                FROM good_collaboration
                JOIN movie_cast ON good_collaboration.cast_member_id1 = movie_cast.cast_member_id
                GROUP BY good_collaboration.cast_member_id1
                HAVING COUNT(DISTINCT good_collaboration.movie_id) >= 2 AND AVG(average_movie_score) >= 40
                UNION
                SELECT good_collaboration.cast_member_id2, AVG(average_movie_score) AS average_movie_score
                FROM good_collaboration
                JOIN movie_cast ON good_collaboration.cast_member_id2 = movie_cast.cast_member_id
                GROUP BY good_collaboration.cast_member_id2
                HAVING COUNT(DISTINCT good_collaboration.movie_id) >= 2 AND AVG(average_movie_score) >= 40
            ) AS subquery
            JOIN movie_cast ON subquery.cast_member_id = movie_cast.cast_member_id
            GROUP BY cast_member_id, cast_name
            ORDER BY collaboration_score DESC, cast_name;
        """
        ######################################################################
        cursor = connection.execute(part_g_i_sql)
        return cursor.fetchall()

    
    # Part h FTS [4 points]
    def part_h(self,connection,path):
        ############### EDIT SQL STATEMENT ###################################
        part_h_sql = "CREATE VIRTUAL TABLE movie_overview USING FTS4 (id INTEGER, overview TEXT)"
        ######################################################################
        connection.execute(part_h_sql)
        ############### CREATE IMPORT CODE BELOW ############################
        file = open(path)
        movie_overview = csv.reader(file)
        movie_overview_sql = "INSERT INTO movie_overview (id, overview) VALUES (?,?)"
        cursor = connection.cursor()
        cursor.executemany(movie_overview_sql, movie_overview)
        connection.commit()
        ######################################################################
        sql = "SELECT COUNT(id) FROM movie_overview;"
        cursor = connection.execute(sql)
        return cursor.fetchall()[0][0]
        
    def part_hi(self,connection):
        ############### EDIT SQL STATEMENT ###################################
        part_hi_sql = """
            SELECT COUNT(*) AS count
            FROM movie_overview
            WHERE (
                overview LIKE 'fight %' COLLATE NOCASE
                OR overview LIKE '% fight.%' COLLATE NOCASE
                OR overview LIKE '% fight %' COLLATE NOCASE
                OR overview = 'fight' COLLATE NOCASE
            )
        """
        ######################################################################
        cursor = connection.execute(part_hi_sql)
        return cursor.fetchall()[0][0]
    
    def part_hii(self,connection):
        ############### EDIT SQL STATEMENT ###################################
        part_hii_sql = """
        SELECT COUNT(DISTINCT overview) AS count
        FROM movie_overview
        WHERE (
            overview GLOB '*[sS][pP][aA][cC][eE]* *[pP][rR][oO][gG][rR][aA][mM]*'
            OR overview GLOB '*[sS][pP][aA][cC][eE]* *[a-zA-Z]* *[pP][rR][oO][gG][rR][aA][mM]*'
            OR overview GLOB '*[sS][pP][aA][cC][eE]* *[a-zA-Z]* *[a-zA-Z]*  *[pP][rR][oO][gG][rR][aA][mM]*'
            OR overview GLOB '*[sS][pP][aA][cC][eE]* *[a-zA-Z]* *[a-zA-Z]* *[a-zA-Z]* *[pP][rR][oO][gG][rR][aA][mM]*'
            OR overview GLOB '*[sS][pP][aA][cC][eE]* *[a-zA-Z]* *[a-zA-Z]* *[a-zA-Z]* *[a-zA-Z]* *[pP][rR][oO][gG][rR][aA][mM]*'
            OR overview GLOB '*[sS][pP][aA][cC][eE]* *[a-zA-Z]* *[a-zA-Z]* *[a-zA-Z]* *[a-zA-Z]* *[a-zA-Z]* *[pP][rR][oO][gG][rR][aA][mM]*'
        ) COLLATE NOCASE
        """
        ######################################################################
        cursor = connection.execute(part_hii_sql)
        return cursor.fetchall()[0][0]


if __name__ == "__main__":
    
    ########################### DO NOT MODIFY THIS SECTION ##########################
    #################################################################################
    if SHOW == True:
        sample = Sample()
        sample.sample()

    print('\033[32m' + "Q2 Output: " + '\033[m')
    db = HW2_sql()
    try:
        conn = db.create_connection("Q2")
    except:
        print("Database Creation Error")

    try:
        conn.execute("DROP TABLE IF EXISTS movies;")
        conn.execute("DROP TABLE IF EXISTS movie_cast;")
        conn.execute("DROP TABLE IF EXISTS cast_bio;")
        conn.execute("DROP VIEW IF EXISTS good_collaboration;")
        conn.execute("DROP TABLE IF EXISTS movie_overview;")
    except:
        print("Error in Table Drops")

    try:
        print('\033[32m' + "part ai 1: " + '\033[m' + str(db.part_ai_1(conn)))
        print('\033[32m' + "part ai 2: " + '\033[m' + str(db.part_ai_2(conn)))
    except:
         print("Error in Part a.i")

    try:
        print('\033[32m' + "Row count for Movies Table: " + '\033[m' + str(db.part_aii_1(conn,"data/movies.csv")))
        print('\033[32m' + "Row count for Movie Cast Table: " + '\033[m' + str(db.part_aii_2(conn,"data/movie_cast.csv")))
    except:
        print("Error in part a.ii")

    try:
        print('\033[32m' + "Row count for Cast Bio Table: " + '\033[m' + str(db.part_aiii(conn)))
    except:
        print("Error in part a.iii")

    try:
        print('\033[32m' + "part b 1: " + '\033[m' + db.part_b_1(conn))
        print('\033[32m' + "part b 2: " + '\033[m' + db.part_b_2(conn))
        print('\033[32m' + "part b 3: " + '\033[m' + db.part_b_3(conn))
    except:
        print("Error in part b")

    try:
        print('\033[32m' + "part c: " + '\033[m' + str(db.part_c(conn)))
    except:
        print("Error in part c")

    try:
        print('\033[32m' + "part d: " + '\033[m')
        for line in db.part_d(conn):
            print(line[0],line[1])
    except:
        print("Error in part d")

    try:
        print('\033[32m' + "part e: " + '\033[m')
        for line in db.part_e(conn):
            print(line[0],line[1],line[2])
    except:
        print("Error in part e")

    try:
        print('\033[32m' + "part f: " + '\033[m')
        for line in db.part_f(conn):
            print(line[0],line[1],line[2])
    except:
        print("Error in part f")
    
    try:
        print('\033[32m' + "part g: " + '\033[m' + str(db.part_g(conn)))
        print('\033[32m' + "part g.i: " + '\033[m')
        for line in db.part_gi(conn):
            print(line[0],line[1],line[2])
    except Exception as e:
        print("Error in part g", e)

    try:   
        print('\033[32m' + "part h: " + '\033[m'+ str(db.part_h(conn,"data/movie_overview.csv")))
        print('\033[32m' + "Count h.i: " + '\033[m' + str(db.part_hi(conn)))
        print('\033[32m' + "Count h.ii: " + '\033[m' + str(db.part_hii(conn)))

    except Exception as e:
        print("Error in part h", e)


    # Extra work
    cursor = conn.cursor()

    # Get the column names of the 'good_collaboration' view
    cursor.execute("PRAGMA table_info(good_collaboration)")
    columns = cursor.fetchall()

    # Extract and print the column names
    column_names = [column[1] for column in columns]
    print("Column Names of 'good_collaboration' View:", column_names)

    conn.close()
    #################################################################################
    #################################################################################
  

import psycopg2

"""
Note: It's essential never to include database credentials in code pushed to GitHub. 
Instead, sensitive information should be stored securely and accessed through environment variables or similar. 
However, in this particular exercise, we are allowing it for simplicity, as the focus is on a different aspect.
Remember to follow best practices for secure coding in production environments.
"""

# Acquire a connection to the database by specifying the credentials.
conn = psycopg2.connect(
    host="psql-dd1368-ht23.sys.kth.se", 
    database="maadf",
    user="maadf",
    password="xFB2bEp2")

# Create a cursor. The cursor allows you to execute database queries.
cur = conn.cursor()


def search_airports():
    try:
        # Prompt the user for input
        search_term = input("Enter airport name or IATA code: ").strip()
        
        # Add wildcard characters for partial matching
        wildcard_term = f"%{search_term}%"

        # SQL query to find matching airports
        query = """
                SELECT 
                    Airport.Name AS AirportName, 
                    Airport.IATACode, 
                    Country.Name AS CountryName
                FROM 
                    Airport
                JOIN 
                    Country ON Airport.Country = Country.Code
                WHERE 
                    Airport.Name ILIKE %s OR Airport.IATACode ILIKE %s
                ORDER BY 
                    CASE 
                        WHEN Airport.Name = %s THEN 1  -- Exact match for Airport Name
                        WHEN Airport.IATACode = %s THEN 1  -- Exact match for IATA Code
                        ELSE 2
                    END, 
                    Airport.Name ASC;
                """
        
        # Execute the query with the wildcard and exact terms
        cur.execute(query, (wildcard_term, wildcard_term, search_term, search_term))
        
        # Fetch the results of query
        results = cur.fetchall()

        if results:
            print(f"\n{'Airport Name':<30} {'IATA Code':<10} {'Country':<10}")
            print("-" * 50)
            for row in results:
                print(f"{row[0]:<30} {row[1]:<10} {row[2]:<10}")
        else:
            print("No airports found matching your search.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
 



def speakers():
    try:
        language = input("Enter a language: ").strip()

        # SQL query to fetch countries and number of speakers
        query = """
                SELECT 
                    c.Name AS Country, 
                    ROUND((c.Population * s.Percentage / 100), 0) AS Speakers
                FROM 
                    Country c
                JOIN 
                    Spoken s
                ON 
                    c.Code = s.Country
                WHERE 
                    s.Language = %s
                ORDER BY 
                    Speakers DESC
                """

        # Execute the query
        cur.execute(query, (language,))
        results = cur.fetchall()

        # Display the results
        if results:
            print(f"{'Country':<30} {'Number of Speakers':<20}")
            print("-" * 50)
            for row in results:
                print(f"{row[0]:<30} {int(row[1]):,}".replace(",", " "))

        else:
            print(f"No countries found where {language} is spoken.")

    except psycopg2.Error as e:
        print(f"Database error: {e}")
 

def create_desert():
    try:
        # User input
        name = input("Enter the name of the desert: ").strip()
        area = float(input("Enter the area of the desert in square kilometers: "))
        province = input("Enter the province where the desert is located: ").strip()
        country = input("Enter the country code where the desert is located: ").strip()
        latitude = float(input("Enter the latitude of the desert: "))
        longitude = float(input("Enter the longitude of the desert: "))

        # Validate that the province and country exist
        query_province_check = """
                               SELECT 1
                               FROM Province
                               WHERE Name = %s AND Country = %s
                               """
        cur.execute(query_province_check, (province, country))
        province_exists = cur.fetchone()

        if not province_exists:
            print(f"Error: Province '{province}' in country '{country}' does not exist.")
            return

        # Check if the desert already exists in the Desert table
        query_desert_check = """
                             SELECT 1
                             FROM Desert
                             WHERE Name = %s
                             """
        cur.execute(query_desert_check, (name,))
        desert_exists = cur.fetchone()

        if desert_exists:
            # Insert only into geo_Desert
            query_geo_desert_insert = """
                                      INSERT INTO geo_Desert (Desert, Country, Province)
                                      VALUES (%s, %s, %s)
                                      ON CONFLICT DO NOTHING
                                      """
            cur.execute(query_geo_desert_insert, (name, country, province))
            print(f"Desert '{name}' already exists. Added to geo_Desert.")
        else:
            # Insert into both Desert and geo_Desert
            query_desert_insert = """
                                  INSERT INTO Desert (Name, Area, Coordinates)
                                  VALUES (%s, %s, ROW(%s, %s)::GeoCoord)
                                  """
            cur.execute(query_desert_insert, (name, area, latitude, longitude))

            query_geo_desert_insert = """
                                      INSERT INTO geo_Desert (Desert, Country, Province)
                                      VALUES (%s, %s, %s)
                                      """
            cur.execute(query_geo_desert_insert, (name, country, province))
            print(f"Desert '{name}' created and added to both Desert and geo_Desert.")

        # Commit the transaction
        conn.commit()

    except psycopg2.Error as e:
        # Handle database errors
        print(f"Database error: {e}")
        if conn:
            conn.rollback()

def create_desert2():
    try:
        # User input
        name = input("Enter the name of the desert: ").strip()
        area = float(input("Enter the area of the desert in square kilometers: "))
        province = input("Enter the province where the desert is located: ").strip()
        country = input("Enter the country code where the desert is located: ").strip()
        latitude = float(input("Enter the latitude of the desert: "))
        longitude = float(input("Enter the longitude of the desert: "))

        # Validate that the province and country exist
        query_province_check = """
                               SELECT 1
                               FROM Province
                               WHERE Name = %s AND Country = %s
                               """
        cur.execute(query_province_check, (province, country))
        province_data = cur.fetchone()

        if not province_data:
            print(f"Error: Province '{province}' in country '{country}' does not exist.")
            return


        province_area = province_data[0]

        # Check the maximum number of provinces the desert can span
        query_desert_provinces_check = """
                                       SELECT COUNT(*)
                                       FROM geo_Desert
                                       WHERE Desert = %s
                                       """
        cur.execute(query_desert_provinces_check, (name,))
        provinces_count = cur.fetchone()[0]

        if provinces_count >= 9:
            print(f"Error: Desert '{name}' already spans the maximum of 9 provinces.")
            return

        # Check the maximum number of deserts in the country
        query_country_deserts_check = """
                                      SELECT COUNT(DISTINCT Desert)
                                      FROM geo_Desert
                                      WHERE Country = %s
                                      """
        cur.execute(query_country_deserts_check, (country,))
        deserts_in_country = cur.fetchone()[0]

        if deserts_in_country >= 20:
            print(f"Error: Country '{country}' already contains the maximum of 20 deserts.")
            return

        # Check that the desert area is at most 30 times larger than the province area
        if area > 30 * province_area:
            print(f"Error: The area of the desert '{name}' exceeds 30 times the area of the province '{province}'.")
            return



        query_desert_check = """
                             SELECT 1
                             FROM Desert
                             WHERE Name = %s
                             """
        cur.execute(query_desert_check, (name,))
        desert_exists = cur.fetchone()

        if desert_exists:
            # Insert only into geo_Desert
            query_geo_desert_insert = """
                                      INSERT INTO geo_Desert (Desert, Country, Province)
                                      VALUES (%s, %s, %s)
                                      ON CONFLICT DO NOTHING
                                      """
            cur.execute(query_geo_desert_insert, (name, country, province))
            print(f"Desert '{name}' already exists. Added to geo_Desert.")
        else:
            # Insert into both Desert and geo_Desert
            query_desert_insert = """
                                  INSERT INTO Desert (Name, Area, Coordinates)
                                  VALUES (%s, %s, ROW(%s, %s)::GeoCoord)
                                  """
            cur.execute(query_desert_insert, (name, area, latitude, longitude))

            query_geo_desert_insert = """
                                      INSERT INTO geo_Desert (Desert, Country, Province)
                                      VALUES (%s, %s, %s)
                                      """
            cur.execute(query_geo_desert_insert, (name, country, province))
            print(f"Desert '{name}' created and added to both Desert and geo_Desert.")

        # Commit the transaction
        conn.commit()

    except psycopg2.Error as e:
        # Handle database errors
        print(f"Database error: {e}")
        if conn:
            conn.rollback()


def user_cli():
    try: 
        while True:
            print("\n\033[1;34mMenu:\033[0m")
            print("\033[1;32m1. Get airport by IATA/Name\033[0m")
            print("\033[1;32m2. Get number of speakers by language\033[0m")
            print("\033[1;32m3. Create Desert\033[0m")
            print("\033[1;32m4. Create Desert (P+)\033[0m")
            print("\033[1;31m5. Exit\033[0m")

            choice = input("Enter choice: ")

            if choice == "1":
                search_airports()
            elif choice == "2":
                speakers()
            elif choice == "3":
                create_desert()
            elif choice == "4":
                create_desert2()
            elif choice == "5":
                print("Exiting...")
                break
            else:
                print("Invalid choice")
    finally:
        conn.close()
        cur.close()


if __name__ == "__main__":
    user_cli()

import time


def stream() -> str:
    """
    This function is used to test the stream feature of Funix.
    """
    message = "Freedom has many difficulties and democracy is not perfect, but we have never had to put a wall up to keep our people in, to prevent them from leaving us. I want to say, on behalf of my countrymen, who live many miles away on the other side of the Atlantic, who are far distant from you, that they take the greatest pride that they have been able to share with you, even from a distance, the story of the last 18 years. I know of no town, no city, that has been besieged for 18 years that still lives with the vitality and the force and the hope and the determination of the city of West Berlin. While the wall is the most obvious and vivid demonstration of the failures of the communist system, for all the world to see, we take no satisfaction in it, for it is, as your mayor has said, an offense not only against history but an offense against humanity, separating families, dividing husbands and wives and brothers and sisters, and dividing a people who wish to be joined together. -- President John F. Kennedy at the Rudolph Wilde Platz, Berlin, June 26, 1963."

    for i in range(len(message)):
        time.sleep(0.01)
        yield message[0:i]

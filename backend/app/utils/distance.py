from math import radians, cos, sin, asin, sqrt
import math
from typing import Tuple, List
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
import base64
from bson import ObjectId
from fastapi import HTTPException


def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(
        radians, [float(lon1), float(lat1), float(lon2), float(lat2)]
    )

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2.0) ** 2.0 + cos(lat1) * cos(lat2) * sin(dlon / 2.0) ** 2.0
    c = 2.0 * asin(sqrt(a))
    return c * 6371.0  # Kilometers


def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth
    specified in decimal degrees (latitude and longitude).

    Parameters:
    lat1, lon1 : float : Latitude and Longitude of point 1 (in decimal degrees)
    lat2, lon2 : float : Latitude and Longitude of point 2 (in decimal degrees)

    Returns:
    float : Distance between the two points in kilometers
    """

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))

    # Radius of Earth in kilometers (mean radius)
    r = 6371.0

    # Calculate the distance
    distance = r * c
    return distance


def calculate_distance(lon1, lat1, lon2, lat2):
    R = 6371.0  # Earth's radius in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = (
        math.sin(dLat / 2.0) ** 2.0
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dLon / 2.0) ** 2.0
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)


def calculate_midpoint(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> Tuple[float, float]:
    """
    Calculate the midpoint between two coordinates.

    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees

    Returns:
        Tuple containing (latitude, longitude) of the midpoint
    """
    # Convert to radians
    lat1, lon1 = math.radians(lat1), math.radians(lon1)
    lat2, lon2 = math.radians(lat2), math.radians(lon2)

    # Calculate the midpoint
    bx = math.cos(lat2) * math.cos(lon2 - lon1)
    by = math.cos(lat2) * math.sin(lon2 - lon1)

    mid_lat = math.atan2(
        math.sin(lat1) + math.sin(lat2), math.sqrt((math.cos(lat1) + bx) ** 2 + by**2)
    )
    mid_lon = lon1 + math.atan2(by, math.cos(lat1) + bx)

    # Convert back to degrees
    return math.degrees(mid_lat), math.degrees(mid_lon)


def calculate_all_midpoints(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> List[Tuple[float, float]]:
    """
    Calculate the initial midpoint and then the midpoints between that point and the original coordinates.

    Args:
        lat1: Latitude of first point in degrees
        lon1: Longitude of first point in degrees
        lat2: Latitude of second point in degrees
        lon2: Longitude of second point in degrees

    Returns:
        List of tuples containing (latitude, longitude) for all midpoints:
        [central_midpoint, midpoint1, midpoint2]
        where midpoint1 is between first coordinate and central_midpoint
        and midpoint2 is between second coordinate and central_midpoint
    """
    # Calculate the central midpoint
    central_mid_lat, central_mid_lon = calculate_midpoint(lat1, lon1, lat2, lon2)

    # Calculate midpoint between first coordinate and central midpoint
    midpoint1_lat, midpoint1_lon = calculate_midpoint(
        lat1, lon1, central_mid_lat, central_mid_lon
    )

    # Calculate midpoint between second coordinate and central midpoint
    midpoint2_lat, midpoint2_lon = calculate_midpoint(
        lat2, lon2, central_mid_lat, central_mid_lon
    )

    return [
        (central_mid_lat, central_mid_lon),  # Central midpoint
        (midpoint1_lat, midpoint1_lon),  # Midpoint between first coordinate and central
        (
            midpoint2_lat,
            midpoint2_lon,
        ),  # Midpoint between second coordinate and central
    ]


async def fetch_nearby_comments_(
    long1: float,
    lat1: float,
    long2: float,
    lat2: float,
    # radius: str,
    db,
):

    radius = calculate_distance(float(long1), float(lat1), float(long2), float(lat2))
    print(radius)

    all_docs = (
        await db["threads"]
        .find({"parent_id": None})
        .sort("vote", -1)
        .to_list(length=None)
    )

    nearby_docs = []
    for doc in all_docs:
        if "coordinates" in doc["location"]:
            doc_longitude = doc["location"]["coordinates"][0]
            doc_latitude = doc["location"]["coordinates"][1]
            distance = calculate_distance(
                float(long1), float(lat1), float(doc_longitude), float(doc_latitude)
            )
            print("Debugging")
            print(doc_longitude, doc_latitude, distance)
            if distance <= float(radius):
                doc["_id"] = str(doc["_id"])
                doc["parent_id"] = str(doc["parent_id"])
                if doc["image_id"]:
                    doc["image_id"] = str(doc["image_id"])
                    image_dict = await show_image(file_id=doc["image_id"], db=db)
                    doc["image_data"] = image_dict
                else:
                    doc["image_data"] = None
                nearby_docs.append(doc)

    return {"threads": nearby_docs}


async def show_image(file_id, db):
    try:
        fs = AsyncIOMotorGridFSBucket(
            db
        )  # Use the same collection name as used for uploads
        print("fkdsajfls", file_id)
        # Retrieve the file from GridFS
        stream = await fs.open_download_stream(ObjectId(file_id))

        # Read and encode the image as a base64 string
        file_content = await stream.read()
        image_data = base64.b64encode(file_content).decode("utf-8")

        # Retrieve metadata from the file document
        file_doc = await db["fs.files"].find_one({"_id": ObjectId(file_id)})
        metadata = file_doc.get("metadata", {})

        return {
            # "file_id": file_id,
            # "filename": stream.filename,
            "verifier_status": metadata.get("verifier_status"),
            "tag": metadata.get("tag"),
            "image_base64": image_data,
        }

    except Exception as e:
        raise HTTPException(status_code=404, detail="Image not found") from e


# Example usage:
# if __name__ == "__main__":
#     # Example coordinates (New York and Los Angeles)
#     ny_lat, ny_lon = 40.7128, -74.0060  # New York
#     la_lat, la_lon = 34.0522, -118.2437  # Los Angeles

#     midpoints = calculate_all_midpoints(ny_lat, ny_lon, la_lat, la_lon)

#     print("Central Midpoint:", midpoints[0])
#     print("Midpoint between NY and central:", midpoints[1])
#     print("Midpoint between LA and central:", midpoints[2])

#     print("Debugging")
#     print((ny_lat + la_lat) / 2)
#     print((ny_lon + la_lon) / 2)


def test():
    first = {"name": ["kasmik"]}
    second = {"name": ["ram"]}
    return {"name": first["name"] + second["name"]}

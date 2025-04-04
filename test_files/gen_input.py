import random


def generate_kmeans_input(filename, dimensions, num_points, value_range=(-100, 100)):
    """
    Generate an input file for KMEANS clustering with the specified dimensions and number of points.

    :param filename: Name of the output file.
    :param dimensions: Number of dimensions for each point.
    :param num_points: Number of points to generate.
    :param value_range: Range (min, max) for the generated values.
    """
    with open(filename, "w") as f:
        for _ in range(num_points):
            point = [str(random.randint(*value_range)) for _ in range(dimensions)]
            f.write("\t".join(point) + "\n")

    print(
        f"File '{filename}' generated with {num_points} points in {dimensions} dimensions."
    )


if __name__ == "__main__":
    dimensions = 100
    num_points = 200000
    num1_points = 400000
    num2_points = 800000
    num3_points = 1000000
    generate_kmeans_input(f"input{dimensions}D_200K.inp", dimensions, num_points)
    generate_kmeans_input(f"input{dimensions}D_400K.inp", dimensions, num1_points)
    generate_kmeans_input(f"input{dimensions}D_800K.inp", dimensions, num2_points)
    generate_kmeans_input(f"input{dimensions}D_1000K.inp", dimensions, num3_points)

import random


class RegionDistribution():
    # This class distributes the users in the grid region according to the region_weights
    def __init__(self, region_weights, seed=0):
        self.rand_gen = random.Random()
        self.rand_gen.seed(seed)
        self.regions = region_weights

    def _get_region(self):
        total_probability = sum(self.regions.values())
        random_sample = total_probability * self.rand_gen.random()
        distribution = 0
        for (region, value) in self.regions.iteritems():
            distribution = distribution + value
            if random_sample < distribution:
                # user is in the region
                return region

    def get_position(self, region_length):
        region = self._get_region()
        pos_x = (region[0] - self.rand_gen.random()) * region_length
        pos_y = (region[1] - self.rand_gen.random()) * region_length
        return pos_x, pos_y

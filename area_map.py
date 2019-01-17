import hlt
import math
import pdb
# areas_per_side

class MapManager:
    def __init__(self, game_map, player_me, len):
        # my_id : our player ID
        self.len = len
        self.game_map = game_map
        self.my_id = player_me.id
        self.tot_hal = 0
        self.n_players = 0
        self.area_arr = []
        self.tot_hal = 0
        self.area_arr = []
        self.get_area_arr()

    def get_area_arr(self):
        r = self.game_map.width % self.len
        q = int((self.game_map.width - r) / self.len) # q = num of area sections per dimension

        len_arr = []
        idx_arr = []
        idx = 0
        n = 0
        for i in range(q):
            if i < r:
                len = self.len+1
            else:
                len = self.len
            len_arr.append(len)
            if i != 0:
                idx += len
            idx_arr.append(idx)
            n += 1

        for i in range(n-1):
            i_arr = []
            for j in range(n-1):
                centroid_x = math.floor((idx_arr[i]+idx_arr[i+1])/2)
                centroid_y = math.floor((idx_arr[j]+idx_arr[j+1])/2)
                centroid = hlt.Position(centroid_x, centroid_y)
                len = len_arr[i]
                area_ij = Area(centroid,len)
                self.area_stats(area_ij)
                #self.area_arr.append(area_ij)
                i_arr.append(area_ij)
                self.tot_hal += area_ij.hal
            self.area_arr.append(i_arr)

    def get_n_players(self):
        for player in self.game_map.players:
            self.n_players += 1

    def area_stats(self, area):
        x1,y1,x2,y2 = area.boundaries
        area.hal = 0
        area.n_enemies = 0
        for i in range(x1,x2+1):
            for j in range(y1,y2+1):
                cell = self.game_map[hlt.Position(i,j)]
                area.hal += cell.halite_amount
                if cell.is_occupied and cell.ship.id is not self.my_id:
                    area.n_enemies += 1

    def update(self,game_map):
        self.game_map = game_map
        self.tot_hal = 0
        for list in self.area_arr:
            for area in list:
                self.area_stats(area)
                area.update()
                self.tot_hal += area.hal

    def max_dense_area(self):
        max_density = 0
        max_i = -1
        max_j = -1
        for i in range(len(self.area_arr)):
            for j in range(len(self.area_arr)):
                tmp_den = self.area_arr[i][j].density
                if tmp_den > max_density:
                    max_density = tmp_den
                    max_i = i
                    max_j = j

        return self.area_arr[i][j]

    def max_dense_spec(self,source,radius):
        max_density = 0
        max_i = -1
        max_j = -1


class Area:
    #let boundaries = [x1 y1 x2 y2]
    def __init__(self, centroid, len):
        self.centroid = centroid
        self.len = len
        self.hal = 0
        self.density = 0
        self.dropoff = False
        self.n_enemies = 0
        self.inspired = 0 # inspired = 2 opponent ships per 4 cell radius. Thus, rough n enemy ships for inspiration
        self.n_inspired = 2 * (len * len)/(3.1 * 4 * 4)

        self.bounding_pts()

    def calculate_distance(self, game_game_map, position):
        dist = game_game_map.calculate_distance(self.centroid, position)
        return dist

    def update(self):
        self.hal = self.hal
        self.density = self.hal / (self.len*self.len)
        self.n_enemies = self.n_enemies
        self.inspired = self.n_enemies / self.n_inspired

    def bounding_pts(self):
        d = self.len/2
        # hacky fix for len even where centroid has been rounded up
        if self.len % 2 == 0:
            x_c = self.centroid.x - 0.5
            y_c = self.centroid.y - 0.5
        else:
            x_c = self.centroid.x
            y_c = self.centroid.y

        x1 = math.ceil(x_c - d)
        y1 = math.ceil(y_c - d)
        x2 = math.floor(x_c + d)
        y2 = math.floor(y_c + d)
        self.boundaries = [x1,y1,x2,y2]

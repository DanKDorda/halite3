import hlt
import math
import pdb
import heapq
# areas_per_side

class MapManager:
    def __init__(self, game_map, player_me, len):
        # my_id : our player ID
        self.len = len
        self.game_map = game_map
        self.player = player_me
        self.my_id = player_me.id
        self.tot_hal = 0
        self.n_players = 0
        self.area_arr = []
        self.tot_hal = 0
        self.area_arr = []
        self.idx_arr = []
        self.get_area_arr()

    def get_area_arr(self):
        r = self.game_map.width % self.len
        q = int((self.game_map.width - r) / self.len) # q = num of area sections per dimension

        len_arr = []
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
            self.idx_arr.append(idx)
            n += 1

        for i in range(n-1):
            i_arr = []
            for j in range(n-1):
                centroid_x = math.floor((self.idx_arr[i]+self.idx_arr[i+1])/2)
                centroid_y = math.floor((self.idx_arr[j]+self.idx_arr[j+1])/2)
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

        return self.area_arr[max_i][max_j]

    def local_max_dense(self,source,radius):
        #
        max_density = 0
        max_i = -1
        max_j = -1
        idx_space = int(round(radius / self.len))
        if idx_space == 0:
            idx_space = 1
        source_i,source_j = self.current_area_idx(source)

        div = len(self.area_arr[0])
        i_1 = (source_i - idx_space) % div
        i_2 = (source_i + idx_space) % div
        j_1 = (source_j - idx_space) % div
        j_2 = (source_j + idx_space) % div
        for i in range(i_1,i_2):
            for j in range(j_1,j_2):
                tmp_den = self.area_arr[i][j].density
                if tmp_den > max_density:
                    max_density = tmp_den
                    max_i = i
                    max_j = j
        return self.area_arr[max_i][max_j]


    def current_area_idx(self,source):
        i = round(source.x/self.len)
        j = round(source.y/self.len)

        return i,j

    def smart_rand_dense(self,source,turn_num):
        max_r = self.game_map.width/2
        min_r = 8
        range_ = max_r - min_r
        interp_x = range_*turn_num/500
        search_r = min_r + interp_x
        area = self.local_max_dense(source,search_r)
        return area

    def local_high_dense(self,radius,num):
        # make sure num of 4x4 areas is within the radius
        dense_area_list = []
        shipyard = self.player.shipyard
        source_i,source_j = self.current_area_idx(shipyard.position)
        idx_space = int(round(radius / self.len))
        div = len(self.area_arr[0])
        i_1 = (source_i - idx_space) % div
        i_2 = (source_i + idx_space) % div
        j_1 = (source_j - idx_space) % div
        j_2 = (source_j + idx_space) % div
        for i in range(i_1,i_2):
            for j in range(j_1,j_2):
                tmp_den = self.area_arr[i][j].density
                if len(dense_area_list) < num:
                    dense_area_list.append(self.area[i][j])
                else:
                    min = 100000
                    idx = -1
                    for k in range(len(dense_area_list)):
                        tmp_min = area.density
                        if tmp_min < min:
                            min = tmp_min
                            idx = k
                    if tmp_min < tmp_den:
                        dense_area_list[idx] = self.area[i][j]

        return dense_area_list

    #def most_dank_cell(self,area):





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

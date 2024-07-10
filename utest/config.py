

class Config:
    def __init__(self, zone):
        if zone == "hk":
            self.config = HkConfig
        elif zone == "sg":
            self.config = SgConfig
        else:
            raise Exception("config zone not exist")


class HkConfig:

    area_id_list = [217, 221, 222, 223, 288, 293, 301]
    area_id_father_list = [3, 161, 34, 38]
    area_id_child_list = [171, 176, 203, 216, 229, 230]
    shop_coordinate = ["114.229374,22.314137", "114.156458,22.241108", "114.251091,22.263868"]
    receive_coordinate = ["114.236124,22.321017", "114.159124,22.243969", "114.241510,22.267104"]
    tasker_coordinate = ["114.229500,22.314137", "114.139320,22.253180","114.239540,22.268112"]


class SgConfig:
    area_id_list = [217, 221, 222, 223, 288, 293, 301]
    area_id_father_list = [3, 161, 34, 38]
    area_id_child_list = [171, 176, 203, 216, 229, 230]
    shop_coordinate = ["114.229374,22.314137", "114.156458,22.241108", "114.251091,22.263868"]
    receive_coordinate = ["114.236124,22.321017", "114.159124,22.243969", "114.241510,22.267104"]
    tasker_coordinate = ["114.229500,22.314137", "114.139320,22.253180", "114.239540,22.268112"]


from client.api_client import ApiClient
tasker = list(ApiClient().client.get_data("tasker", "tasker_order_num").id)

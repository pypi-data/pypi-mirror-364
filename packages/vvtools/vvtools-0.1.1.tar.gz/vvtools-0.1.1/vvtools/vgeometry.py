import torch
from dataclasses import dataclass
from typing import Tuple, List
import math
import numpy as np
import copy

#############################################################
############################################################
## GEOMETRY UTILITIES


@dataclass
class rect2d:
    x: float
    y: float
    width: float
    height: float

    def to_tensor(self) -> torch.Tensor:
        return torch.tensor([self.x, self.y, self.width, self.height], dtype=torch.float32)

    def to_string(self):
        return f"(x={self.x}, y={self.y}, width={self.width}, height={self.height})"


def scale_rect2d(rect: rect2d, scale: float) -> rect2d:
    new_rect = rect2d(x=rect.x * scale, y=rect.y * scale, width=rect.width * scale, height=rect.height * scale)
    return new_rect


def tensor_to_rect2d(tensor):
    x, y, width, height = tensor
    return rect2d(float(x), float(y), float(width), float(height))


def is_inside_rect2d(inner: rect2d, outer: rect2d) -> bool:
    # inner 직사각형의 좌상단 및 우하단 좌표 계산
    inner_left = inner.x
    inner_right = inner.x + inner.width
    inner_top = inner.y
    inner_bottom = inner.y + inner.height

    # outer 직사각형의 좌상단 및 우하단 좌표 계산
    outer_left = outer.x
    outer_right = outer.x + outer.width
    outer_top = outer.y
    outer_bottom = outer.y + outer.height

    # inner 직사각형이 outer 직사각형 안에 완벽히 들어오는지 확인
    return outer_left <= inner_left and outer_right >= inner_right and outer_top <= inner_top and outer_bottom >= inner_bottom


@dataclass
class pos2d:
    x: float
    y: float

    def to_tensor(self) -> torch.Tensor:
        return torch.tensor([self.x, self.y], dtype=torch.float32)

    def to_string(self):
        return f"({self.x}, {self.y})"


def tensor_to_pos2d(tensor):
    x, y = tensor
    return pos2d(float(x), float(y))


class pos3d:

    int_min_32 = -(2**31)

    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z
        self.scale_factor = 1.0

    @classmethod
    def make_from_list(cls, coordinates):
        if len(coordinates) != 3:
            raise ValueError("Coordinates must be a list of three values: [x, y, z]")
        return cls(*coordinates)

    @classmethod
    def EmptyPos(cls):
        return cls(pos3d.int_min_32, 0, 0)

    def set_empty(self):
        self.x = pos3d.int_min_32
        self.y = 0
        self.z = 0

    @property
    def empty(self) -> bool:
        return self.x == pos3d.int_min_32

    def get_scaled_pos(self) -> np.ndarray:
        if self.empty:
            return np.zeros(3, dtype=float)
        else:
            return np.array([self.x, self.y, self.z], dtype=float) * self.scale_factor

    @classmethod
    def make_from_tensor(cls, tensor):
        x, y, z = tensor
        return cls(int(x), int(y), int(z))

    def update_position(self, pos):
        self.x = pos.x
        self.y = pos.y
        self.z = pos.z

    def to_string(self):
        if self.x == pos3d.int_min_32:
            return "(empty pos3d)"
        else:
            return f"{self.x}, {self.y}, {self.z}"


def calculate_center_position(points: List[pos3d]) -> pos3d:
    if not points:
        raise ValueError("The list of points cannot be empty.")

    # Calculate the sum of all x, y, and z coordinates
    sum_x = sum(point.x for point in points)
    sum_y = sum(point.y for point in points)
    sum_z = sum(point.z for point in points)

    # Calculate the number of points
    num_points = len(points)

    # Calculate the average for each coordinate
    center_x = sum_x / num_points
    center_y = sum_y / num_points
    center_z = sum_z / num_points

    # Return the center as a new pos3d object
    return pos3d(int(center_x), int(center_y), int(center_z))


@dataclass
class rect3d:
    p1: pos3d
    p2: pos3d

    def to_tensor(self) -> torch.Tensor:
        return torch.tensor([self.p1.to_tensor(), self.p2.to_tensor()], dtype=torch.float32)

    def to_string(self):
        return f"rect3d(p1={self.p1.to_string()}, p2={self.p2.to_string()})"


def tensor_to_rect3d(tensor):
    t1, t2 = tensor
    return rect3d(pos3d.make_from_tensor(t1), pos3d.make_from_tensor(t2))


def is_inside_rect3d(point: pos3d, rect: rect3d) -> bool:
    # 두 점 p1과 p2의 좌표를 기준으로 min/max를 사용하여 직각 육면체의 경계를 계산
    # 예시 사용
    # p1 = pos3d(0, 0, 0)
    # p2 = pos3d(5, 5, 5)
    # rect = rect3d(p1, p2)
    # point = pos3d(3, 3, 3)
    #
    # print(is_in_rect3d(point, rect))  # True 출력

    x_min = min(rect.p1.x, rect.p2.x)
    x_max = max(rect.p1.x, rect.p2.x)
    y_min = min(rect.p1.y, rect.p2.y)
    y_max = max(rect.p1.y, rect.p2.y)
    z_min = min(rect.p1.z, rect.p2.z)
    z_max = max(rect.p1.z, rect.p2.z)

    # 점이 직각 육면체 내부에 있는지 확인
    return x_min <= point.x <= x_max and y_min <= point.y <= y_max and z_min <= point.z <= z_max


@dataclass
class size3d:
    width: float
    height: float
    depth: float

    def to_tensor(self) -> torch.Tensor:
        return torch.tensor([self.width, self.height, self.depth], dtype=torch.float32)

    def to_string(self):
        return f"({self.width}, {self.height}, {self.depth})"

def tensor_to_size3d(tensor):
    width, height, depth = tensor
    return size3d(float(width), float(height), float(depth))


def calc_move_time_sec(pos_a: pos3d, pos_b: pos3d, velocity_mmps: float) -> float:
    """3D 공간 pos_a에서 pos_b를 veclocity_mmps 속력으로 이동 할 때 걸리는 시간을 리턴한다. 단위(초)"""
    # Calculate the Euclidean distance between pos_a and pos_b
    distance = math.sqrt((pos_b.x - pos_a.x) ** 2 + (pos_b.y - pos_a.y) ** 2 + (pos_b.z - pos_a.z) ** 2)

    # Calculate the time taken to move at the given velocity
    move_time_sec = distance / velocity_mmps

    return move_time_sec


def get_distance(pos_a: pos3d, pos_b: pos3d) -> int:

    # Calculate the Euclidean distance between pos_a and pos_b
    distance = math.sqrt((pos_b.x - pos_a.x) ** 2 + (pos_b.y - pos_a.y) ** 2 + (pos_b.z - pos_a.z) ** 2)
    return int(distance)


def calc_pos_by_time(src_pos: pos3d, target_pos: pos3d, velocity_mmps: float, time_after_sec: float) -> pos3d:
    """3D 공간 src_pos에서 target_pos로 velocity_mmps 속도로 나아갈 때, 일정시간(time_after_sec) 이 지난 후 위치를 반환한다."""
    # Calculate the total distance between source and target
    total_distance = math.sqrt(
        (target_pos.x - src_pos.x) ** 2 + (target_pos.y - src_pos.y) ** 2 + (target_pos.z - src_pos.z) ** 2
    )

    # Calculate the distance covered after the given time
    distance_covered = velocity_mmps * time_after_sec

    # Handle the case where the distance covered exceeds or reaches the total distance
    if distance_covered >= total_distance:
        return target_pos  # Object has reached or surpassed the target position

    if total_distance == 0:
        return copy.deepcopy(src_pos)

    # Calculate the ratio of the distance covered to the total distance
    ratio = distance_covered / total_distance

    # Calculate the intermediate position based on the ratio
    new_pos = pos3d(
        int(src_pos.x + (target_pos.x - src_pos.x) * ratio),
        int(src_pos.y + (target_pos.y - src_pos.y) * ratio),
        int(src_pos.z + (target_pos.z - src_pos.z) * ratio),
    )
    new_pos.scale_factor = src_pos.scale_factor
    return new_pos